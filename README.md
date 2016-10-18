# Facebook Messenger Watson Recipe Bot
This is a Python Flask web application that serves as a webhook for a Facebook Messenger chatbot.

The app responds to GET requests as well as incoming messages from Facebook via POST. It uses:
 - IBM Watson™ Conversation service to extract intent and entities as well as navigate through a dialog.
 - Cloudant NoSQL DB to store user context for future reference in the conversation
 - Spoonacular API to return recipe suggestions and steps based on user input

### The code is a merging of two repositories:

## Recipe Slack Bot Using Watson Conversation and Spoonacular API:
Tutorial: [How To Build a Recipe Slack Bot Using Watson Conversation and Spoonacular API](https://medium.com/ibm-watson-developer-cloud/how-to-build-a-recipe-slack-bot-using-watson-conversation-and-spoonacular-api-487eacaf01d4)
Code: [watson-recipe-bot](https://github.com/boxcarton/watson-recipe-bot)

## Facebook Messenger Chat Bot in Python:
Tutorial: [Facebook Messenger Bot Tutorial: Step-by-Step Instructions for Building a Basic Facebook Chat Bot](https://blog.hartleybrody.com/fb-messenger-bot/)
Code: [Facebook Messenger Bot](https://github.com/hartleybrody/fb-messenger-bot)
