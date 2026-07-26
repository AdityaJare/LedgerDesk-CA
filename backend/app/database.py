import logging
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

logger = logging.getLogger("uvicorn.error")

class Database:
    client: AsyncIOMotorClient = None
    db = None

db_helper = Database()

async def connect_to_mongo():
    logger.info("Connecting to MongoDB...")
    mongo_kwargs = {}
    if "mongodb+srv://" in settings.MONGODB_URL:
        mongo_kwargs["tlsAllowInvalidCertificates"] = True
    db_helper.client = AsyncIOMotorClient(settings.MONGODB_URL, **mongo_kwargs)
    db_helper.db = db_helper.client[settings.DB_NAME]
    logger.info("Connected to MongoDB!")


async def close_mongo_connection():
    logger.info("Closing MongoDB connection...")
    if db_helper.client:
        db_helper.client.close()
    logger.info("MongoDB connection closed!")

def get_database():
    return db_helper.db
