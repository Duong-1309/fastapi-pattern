import os
import urllib.parse
from fastapi import FastAPI
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware

from pymongo import MongoClient

from .tags import TAGS

# using lib openssl with command "openssl rand -hex 32"
PROJECT_SECRET_KEY = '4fc9ddfb759d191722e3d4b9814a578232780320e4a8a9f41da3866b7ff81af5'

DEBUG = os.environ.get('DEBUG', 0)

PROJECT_TITLE = 'Project sample FastAPI'
__VERSION__='1.0'
DESCRIPTION='Project sample used FastAPI and PyMongo'

# Initial FastAPI app
app = FastAPI(
    debug=bool(DEBUG),
    title=PROJECT_TITLE,
    docs_url=None,
    redoc_url=None
)

@app.get(path='/docs', include_in_schema=False)
async def overridden_swagger():
    return get_swagger_ui_html(
        openapi_url='/openapi.json',
        title=PROJECT_TITLE,
        # swagger_favicon_url='link icon', icon in path
    )

@app.get(path='/redoc', include_in_schema=False)
async def overridden_redoc():
    return get_redoc_html(
        openapi_url='/openapi.json',
        title=PROJECT_TITLE,
        # redoc_favicon_url='link' icon in path redoc
    )

def custom_api():
    openapi_schema = get_openapi(
        title=PROJECT_TITLE,
        version=__VERSION__,
        description=DESCRIPTION,
        routes=app.routes,
        tags=TAGS,
    )
    # openapi_schema['info']['x-logo'] = {
    #     'url': 'Link logo'
    # }
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_api

# configs origins
origins = ['*']
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# GET DB host from environment
DB_NAME = 'sample_fastapi'

DB_HOST = os.environ.get('DB_HOST')

DB_PORT = os.environ.get('DB_PORT')

CLOUDINARY_URL = os.environ.get('CLOUDINARY_URL')

SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')

REMOTE_MONGO_URL = os.environ.get('REMOTE_MONGO_URL')

REMOTE_POSTGRES_URL = os.environ.get('REMOTE_POSTGRES_URL')

CELERY_APP_NAME = 'celery_app'

MONGO_CLIENT = None

if all([DB_HOST, DB_PORT]):
    # Initital connection to database
    MONGO_CLIENT = MongoClient(
        f'mongodb://root:{urllib.parse.quote("rootghouldb2021")}@{DB_HOST}:{DB_PORT}/?authMechanism=SCRAM-SHA-256'
    )
    if not MONGO_CLIENT['schedule'].command('usersInfo', usersInfo={"user": "root", "db": "schedule"}):
        MONGO_CLIENT['schedule'].command(
            'createUser',
            createUser='root',
            pwd='rootghouldb2021',
            roles=["readWrite", "dbAdmin"],
            mechanisms=["SCRAM-SHA-256"],
        )
