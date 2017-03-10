import os, json
import couchdb

if 'VCAP_SERVICES' in os.environ:
    cloudant_service = json.loads(os.environ['VCAP_SERVICES'])['cloudantNoSQLDB'][0]
    credentials = cloudant_service['credentials']
    cl_username = credentials['username']
    cl_password = credentials['password']
    cl_url = credentials['url']
else:
    cl_username = os.getenv("CLOUDANT_USERNAME")
    cl_password = os.getenv("CLOUDANT_PASSWORD")
    cl_url = os.getenv("CLOUDANT_URL")


def init_db():
    couch = get_couch()
    if 'recipe_bot' not in couch:
        couch.create('recipe_bot')
    print 'Initialized the database.'


def get_couch():
    couch = couchdb.Server(cl_url)
    couch.resource.credentials = (cl_username, cl_password)
    return couch


def print_database():
    couch = get_couch()
    db = couch['recipe_bot']
    for doc_id in db:
        print db[doc_id]

init_db()
