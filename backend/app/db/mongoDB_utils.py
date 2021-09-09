import logging

from motor.motor_asyncio import AsyncIOMotorClient
from ..core.config import MONGODB_URL, MAX_CONNECTIONS_COUNT, MIN_CONNECTIONS_COUNT
from app.db.mongoDB import db
#APScheduler Related Libraries

async def mongoDB_startup_event():
    logging.info("Connnecting to MongoDB")
    db.client = AsyncIOMotorClient(str(MONGODB_URL),
                                   maxPoolSize=MAX_CONNECTIONS_COUNT,
                                   minPoolSize=MIN_CONNECTIONS_COUNT,
                                   maxIdleTimeMS=5000
                                   )
    logging.info("MongoDB connected！")

async def mongoDB_shutdown_event():
    logging.info("===========")
    logging.info("Disconnecting mongoDB connection...")
    db.client.close()
    logging.info("MongoDB Connection closed！")