from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

client = AsyncIOMotorClient(settings.MONGO_URI)
db = client[settings.DB_NAME]

tickets_collection = db["tickets"]
kb_collection = db["knowledge_base"]
software_collection = db["software_catalog"]


async def ping_db():
    await client.admin.command("ping")
    return True
