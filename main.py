from pyrogram import Client, filters
from config import Config
from pymongo import MongoClient

app = Client(
    "kobramoviesbot",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN
)

mongo_client = MongoClient(Config.DATABASE_URI)
db = mongo_client[Config.DATABASE_NAME]

@app.on_message(filters.command(["start", "help"]))
async def start(client, message):
    await message.reply_text("Hello! I'm a movie search bot.")

# Define additional handlers for the bot's functionality

if __name__ == "__main__":
    app.run()



