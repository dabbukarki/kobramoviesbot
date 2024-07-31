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

@pyrogram_app.on_message(filters.command(["start", "help"]))
async def start(client, message):
    user_id = message.from_user.id
    user = db['users'].find_one({"user_id": user_id})
    if not user:
        db['users'].insert_one({"user_id": user_id})
    await message.reply_text("Hello! I'm a movie search bot.")

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
            print(f"Failed to send message to {user['user_id']}: {e}")
    
    await message.reply_text("Broadcast message sent to all users.")

@pyrogram_app.on_message(filters.document | filters.video | filters.audio | filters.photo)
async def index_files(client, message):
    file_data = {
        "file_id": message.document.file_id if message.document else message.photo.file_id,
        "file_name": message.document.file_name if message.document else None,
        "file_size": message.document.file_size if message.document else None,
        "file_type": message.document.mime_type if message.document else "image",
        "caption": message.caption if message.caption else ""
    }
    db['files'].insert_one(file_data)
    await message.reply_text(f"Indexed file: {file_data['file_name'] or 'Image'}")

@pyrogram_app.on_inline_query()
async def inline_search(client, inline_query):
    query = inline_query.query.lower()
    results = []

    files = db['files'].find({"caption": {"$regex": query, "$options": "i"}})
    for file in files:
        result = {
            "type": "document" if file["file_type"] != "image" else "photo",
            "id": file["file_id"],
            "document_file_id": file["file_id"],
            "title": file["file_name"] or "Image",
            "description": file["caption"]
        }
        results.append(result)
    
    await inline_query.answer(results)

@pyrogram_app.on_message(filters.command("randompic"))
async def random_pic(client, message):
    pics = db['files'].find({"file_type": "image"})
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
    correction = spell.correction(word)
    await message.reply_text(f"Correction: {correction}")

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
