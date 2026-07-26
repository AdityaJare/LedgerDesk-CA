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
    urls_to_try = [settings.MONGODB_URL, "mongodb://localhost:27017"]
    
    for url in urls_to_try:
        try:
            mongo_kwargs = {"serverSelectionTimeoutMS": 5000}
            if "mongodb+srv://" in url:
                mongo_kwargs["tls"] = True
                mongo_kwargs["tlsAllowInvalidCertificates"] = True

            client = AsyncIOMotorClient(url, **mongo_kwargs)
            # Test ping
            await client.admin.command('ping')
            db_helper.client = client
            db_helper.db = client[settings.DB_NAME]
            logger.info(f"Connected to MongoDB successfully at {url[:25]}...")
            return
        except Exception as e:
            logger.warning(f"MongoDB connection to {url[:25]} failed: {str(e)}. Trying fallback...")
            
    # Default fallback client if both pings failed
    db_helper.client = AsyncIOMotorClient("mongodb://localhost:27017")
    db_helper.db = db_helper.client[settings.DB_NAME]
    logger.info("Using local fallback MongoDB instance.")



async def close_mongo_connection():
    logger.info("Closing MongoDB connection...")
    if db_helper.client:
        db_helper.client.close()
    logger.info("MongoDB connection closed!")

def get_database():
    return db_helper.db
