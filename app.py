import os
import sys
import json

import requests
from flask import Flask, request, g
from couchdb import ResourceNotFound
from cloudant.document import Document
from database import get_couch

from watson_developer_cloud import ConversationV1

from souschef.recipe import RecipeClient
from souschef.souschef import SousChef

app = Flask(__name__)

conversation_client = ConversationV1(version='2016-07-11',
                                     username=os.environ.get("CONVERSATION_USERNAME"),
                                     password=os.environ.get("CONVERSATION_PASSWORD"))
workspace_id = os.environ.get("WORKSPACE_ID")
recipe_client = RecipeClient(os.environ.get("SPOONACULAR_KEY"))
souschef = SousChef(conversation_client, workspace_id, recipe_client)


@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Hello world", 200


@app.route('/', methods=['POST'])
def webhook():
    # endpoint for processing incoming messaging events

    data = request.get_json()

    if data["object"] == "page":

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                log("Received message event: " + json.dumps(messaging_event))

                if messaging_event.get("message"):  # someone sent us a message

                    sender_id = messaging_event["sender"]["id"]  # the facebook ID of the person sending you the message

                    message = messaging_event["message"]
                    message_text = message["text"]  # the message's text
                    # context = json.loads(message["metadata"]) if message.get("metadata") else None  # message context

                    # get the context from the database
                    db = get_db()
                    context = db[sender_id]['context'] if sender_id in db else None

                    # Handle the message
                    response, context = souschef.handle_message(message_text, context)

                    log("new context = " + json.dumps(context))
                    if sender_id in db:
                        doc = db[sender_id]
                        doc['context'] = context
                        db.save(doc)
                    else:
                        db.save({
                            '_id': sender_id,  # Setting _id is optional
                            'context': context
                        })

                    if isinstance(response, list):
                        for step in response:
                            send_message(sender_id, step)
                    else:
                        send_message(sender_id, response)

                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    pass

    return "ok", 200


def send_message(recipient_id, message_text):
    # log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })
    log("Responding to Messenger with " + data)
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)


def get_db():
    if not hasattr(g, 'db'):
        couch = get_couch()
        g.db = couch['recipe_bot']
    return g.db


def log(message):  # simple wrapper for logging to stdout on heroku
    print str(message)
    sys.stdout.flush()


if __name__ == '__main__':
    app.run(debug=True)
