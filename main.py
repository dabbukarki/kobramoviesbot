from pyrogram import Client, filters
from config import Config
from pymongo import MongoClient
import random
# from spellchecker import SpellChecker # Commented out due to missing module
from dotenv import load_dotenv
import os
from flask import Flask
import threading
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Load environment variables from .env file
load_dotenv()

# Flask setup
app = Flask(__name__)

@app.route('/')
def home():
    return "Hello, World!"

def run_flask():
    try:
        port = int(os.environ.get("PORT", 5000))
        app.run(host='0.0.0.0', port=port)
    except Exception as e:
        logging.error("Error in Flask app: %s", e)

# Pyrogram setup
try:
    pyrogram_app = Client(
        "kobramoviesbot",
        api_id=os.getenv("API_ID"),
        api_hash=os.getenv("API_HASH"),
        bot_token=os.getenv("BOT_TOKEN")
    )
    logging.info("Pyrogram Client initialized successfully.")
except Exception as e:
    logging.error("Error initializing Pyrogram Client: %s", e)
    raise

try:
    mongo_client = MongoClient(os.getenv("DATABASE_URI"))
    db = mongo_client[os.getenv("DATABASE_NAME")]
    logging.info("MongoDB Client initialized successfully.")
except Exception as e:
    logging.error("Error initializing MongoDB Client: %s", e)
    raise

# spell = SpellChecker() # Commented out due to missing module

@pyrogram_app.on_message(filters.command(["start", "help"]))
async def start(client, message):
    user_id = message.from_user.id
    user = db['users'].find_one({"user_id": user_id})
    if not user:
        db['users'].insert_one({"user_id": user_id})
    await message.reply_text("Hello! I'm a movie search bot.\n\nCommands:\n/search <query> - Search for movies\n/broadcast <message> - Send a broadcast message\n/randompic - Get a random picture\n/stats - Get bot statistics\n/userinfo <user_id> - Get user info\n/spellcheck <word> - Check spelling\n/storefile <file_id> - Store a file")

@pyrogram_app.on_message(filters.command("search"))
async def search(client, message):
    if len(message.command) < 2:
        await message.reply_text("Usage: /search <query>")
        return
    
    query = message.command[1]
    results = db['files'].find({"caption": {"$regex": query, "$options": "i"}})
    if results.count() == 0:
        await message.reply_text("No results found.")
        return
    
    for result in results:
        await message.reply_text(f"Found: {result['caption']}")

@pyrogram_app.on_message(filters.command("broadcast") & filters.user(Config.ADMINS))
async def broadcast_message(client, message):
    if len(message.command) < 2:
        await message.reply_text("Usage: /broadcast <message>")
        return
    
    broadcast_text = message.text.split(" ", 1)[1]
    
    users = db['users'].find()
    for user in users:
        try:
            await client.send_message(chat_id=user['user_id'], text=broadcast_text)
        except Exception as e:
            logging.error("Failed to send message to %s: %s", user['user_id'], e)
    
    await message.reply_text("Broadcast message sent to all users.")

@pyrogram_app.on_message(filters.command("randompic"))
async def random_pic(client, message):
    pics = db['files'].find({"file_type": "image"})
    if pics.count() == 0:
        await message.reply_text("No pictures found.")
        return
    
    pic = random.choice(list(pics))
    await client.send_photo(chat_id=message.chat.id, photo=pic["file_id"], caption=pic["caption"])

@pyrogram_app.on_message(filters.command("stats") & filters.user(Config.ADMINS))
async def stats(client, message):
    user_count = db['users'].count_documents({})
    file_count = db['files'].count_documents({})
    await message.reply_text(f"Users: {user_count}\nFiles: {file_count}")

@pyrogram_app.on_message(filters.command("userinfo") & filters.user(Config.ADMINS))
async def user_info(client, message):
    if len(message.command) < 2:
        await message.reply_text("Usage: /userinfo <user_id>")
        return
    
    user_id = int(message.command[1])
    user = db['users'].find_one({"user_id": user_id})
    if user:
        await message.reply_text(f"User ID: {user['user_id']}")
    else:
        await message.reply_text("User not found.")

@pyrogram_app.on_message(filters.command("spellcheck"))
async def spell_check(client, message):
    if len(message.command) < 2:
        await message.reply_text("Usage: /spellcheck <word>")
        return
    
    word = message.command[1]
    # correction = spell.correction(word) # Commented out due to missing module
    # await message.reply_text(f"Correction: {correction}")
    await message.reply_text("Spellcheck feature is currently disabled.")

@pyrogram_app.on_message(filters.command("storefile"))
async def store_file(client, message):
    if len(message.command) < 2:
        await message.reply_text("Usage: /storefile <file_id>")
        return
    
    file_id = message.command[1]
    file = db['files'].find_one({"file_id": file_id})
    if file:
        await message.reply_text(f"File already indexed: {file['file_name'] or 'Image'}")
    else:
        db['files'].insert_one({"file_id": file_id, "file_name": None, "file_size": None, "file_type": "unknown", "caption": ""})
        await message.reply_text("File stored successfully.")

if __name__ == "__main__":
    try:
        threading.Thread(target=run_flask).start()
        pyrogram_app.run()
    except Exception as e:
        logging.error("Error running the bot: %s", e)
