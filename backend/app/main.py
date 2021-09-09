import os
import logging
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.logger import logger as fastapi_logger
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY
from app.db.mongoDB_utils import mongoDB_startup_event, mongoDB_shutdown_event
from app.core.error import http_error_handler, http_422_error_handler
from app.api.v1.api import router as api_router
# loading .env
load_dotenv()

print(os.getenv('ENVIROMENT'))
# configuring swagger docs
if os.getenv('ENVIROMENT') == "DEVELOPMENT":
    print("lol")
    app = FastAPI(title="Buy Me Crypto API")
else:
    print("ll")
    app = FastAPI(title="Buy Me Crypto API", docs_url=None, redoc_url=None, openapi_url="/app/v1/openapi.json")


'''
configuring start and stop events

1. MongoDB
    - startup: event = Start MongoDB instance
    - shutdown: event = Stop MonogDB instance
'''

app.add_event_handler('startup', mongoDB_startup_event)
app.add_event_handler('shutdown', mongoDB_shutdown_event)

# handle http exceptions
app.add_exception_handler(HTTPException, http_error_handler)
app.add_exception_handler(HTTP_422_UNPROCESSABLE_ENTITY, http_422_error_handler)


# configurin routers
app.include_router(api_router, prefix="/bmc") 

origins = [
    "http://localhost:3000",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

gunicorn_logger = logging.getLogger("gunicorn")
log_level = gunicorn_logger.level

root_logger = logging.getLogger()
gunicorn_error_logger = logging.getLogger("gunicorn.error")
uvicorn_access_logger = logging.getLogger("uvicorn.access")

# Use gunicorn error handlers for root, uvicorn, and fastapi loggers
root_logger.handlers = gunicorn_error_logger.handlers
uvicorn_access_logger.handlers = gunicorn_error_logger.handlers
fastapi_logger.handlers = gunicorn_error_logger.handlers

# Pass on logging levels for root, uvicorn, and fastapi loggers
if os.getenv('ENVIROMENT') == "DEVELOPMENT":
    root_logger.setLevel(logging.DEBUG)
    uvicorn_access_logger.setLevel(logging.DEBUG)
    fastapi_logger.setLevel(logging.DEBUG)
else:
    root_logger.setLevel(logging.INFO)
    uvicorn_access_logger.setLevel(logging.INFO)
    fastapi_logger.setLevel(logging.INFO)

