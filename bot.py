import discord
from dotenv import load_dotenv
from os import getenv
from main import track, main
import re

async def verifyLink(message, link, username):
    if link.startswith("https://www.amazon.ca/"):
        asin = re.search(r'/[dg]p/([^/]+)', link, flags=re.IGNORECASE).group(1)
        if asin[:2] != 'B0':
            asin = re.search(r'/product/([^/]+)', link, flags=re.IGNORECASE).group(1)
        valid = await track(asin, "razeendrake@gmail.com", username)
        response = "Your item is being tracked, you'll be notified via email when the price drops!"
    else:
        response = "Invalid Link, type '!help' for list of commands."
    await message.channel.send(response)

load_dotenv('.env')
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

def run():    
    @client.event
    async def on_ready():
        print(f'{client.user} is now running!')

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return 
        if message.content.split()[0] == '!track':
            link = str(message.content.split()[1]) 
            username = str(message.author)
            await verifyLink(message, link, username)
        elif message.content == '!help':
            await message.channel.send("Try: !track (amazon link)")
        else: 
            return 
    client.run(getenv('TOKEN'))
    
run()
