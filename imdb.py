import requests
from config import Config

OMDB_API_KEY = "your_omdb_api_key"

async def imdb_search(query):
    url = f"http://www.omdbapi.com/?t={query}&apikey={OMDB_API_KEY}"
    response = requests.get(url).json()
    if response['Response'] == "True":
        title = response['Title']
        year = response['Year']
        imdb_rating = response['imdbRating']
        plot = response['Plot']
        return f"Title: {title}\nYear: {year}\nIMDB Rating: {imdb_rating}\nPlot: {plot}"
    else:
        return "Movie not found."

@app.on_message(filters.command("imdb"))
async def imdb_command(client, message):
    query = message.text.split(' ', 1)[1]
    result = await imdb_search(query)
    await message.reply_text(result)
