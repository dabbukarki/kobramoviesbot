from pyrogram import Client, filters
from config import Config
from pymongo import MongoClient
import random
from spellchecker import SpellChecker
from dotenv import load_dotenv
import os
from flask import Flask
import threading

# Load environment variables from .env file
load_dotenv()

# Flask setup
app = Flask(__name__)

@app.route('/')
def home():
    return "Hello, World!"

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

# Pyrogram setup
pyrogram_app = Client(
    "kobramoviesbot",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN
)

mongo_client = MongoClient(Config.DATABASE_URI)
db = mongo_client[Config.DATABASE_NAME]
spell = SpellChecker()

# Command Handling

@pyrogram_app.on_message(filters.command(["start", "help"]))
async def start(client, message):
    help_text = (
        "Hello! I'm a movie search bot.\n\n"
        "Here are the available commands:\n\n"
        "/search <query> - Search for movies by caption\n"
        "/randompic - Get a random movie picture\n"
        "/spellcheck <word> - Check the spelling of a word\n"
        "/stats - Get bot statistics (admin only)\n"
        "/userinfo <user_id> - Get user information (admin only)\n"
        "/storefile <file_id> - Store a file by its ID\n\n"
        "Use these commands to interact with the bot and explore our movie database!"
    )
    await message.reply_text(help_text)

@pyrogram_app.on_message(filters.command("search"))
async def search(client, message):
    if len(message.command) < 2:
        await message.reply_text("Usage: /search <query>")
        return
    
    query = message.command[1].lower()
    results = db['files'].find({"caption": {"$regex": query, "$options": "i"}})
    
    if results.count() == 0:
        await message.reply_text("No results found for your query.")
    else:
        response = "Search results:\n\n"
        for file in results:
            response += f"- {file['file_name'] or 'Image'}: {file['caption']}\n"
        await message.reply_text(response)

@pyrogram_app.on_message(filters.command("randompic"))
async def random_pic(client, message):
    pics = db['files'].find({"file_type": "image"})
    pic = random.choice(list(pics))
    await client.send_photo(chat_id=message.chat.id, photo=pic["file_id"], caption=pic["caption"])

@pyrogram_app.on_message(filters.command("spellcheck"))
async def spell_check(client, message):
    if len(message.command) < 2:
        await message.reply_text("Usage: /spellcheck <word>")
        return
    
    word = message.command[1]
    correction = spell.correction(word)
    await message.reply_text(f"Correction: {correction}")

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

# Run Flask and Pyrogram clients in separate threads
if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    pyrogram_app.run()
