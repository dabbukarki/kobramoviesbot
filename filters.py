from pyrogram import filters
from config import Config
from pymongo import MongoClient

mongo_client = MongoClient(Config.DATABASE_URI)
db = mongo_client[Config.DATABASE_NAME]
collection = db['movies']

async def auto_filter(client, message):
    query = message.text
    result = collection.find_one({"name": {"$regex": query, "$options": "i"}})
    if result:
        await message.reply_text(f"Found: {result['name']}\n\nLink: {result['link']}")
    else:
        await message.reply_text("No results found.")

app.add_handler(filters.text & filters.chat(Config.AUTH_CHANNEL), auto_filter)
