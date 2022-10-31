import discord
from discord.ext import tasks
from dotenv import load_dotenv
from os import getenv
from main import track, main
import re

load_dotenv('.env')
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

async def verifyLink(message, link, email, username):
    if link.startswith("https://www.amazon.ca/") and 'B0' in link:
        asin = re.search(r'/[dg]p/([^/]+)', link, flags=re.IGNORECASE).group(1)
        if asin[:2] != 'B0':
            asin = re.search(r'/product/([^/]+)', link, flags=re.IGNORECASE).group(1)
        response = "Your item is being tracked, you'll be notified via email when the price drops!"
        await track(asin, email, username)
    else:
        response = "Invalid link, make sure it's an Amazon.ca product page link."
    await message.channel.send(response)

@tasks.loop(minutes=5)
async def checkPrices():
    await main()
    print("Price checking complete.")

@client.event
async def on_ready():
    checkPrices.start()
    print(f'{client.user} is now running!')

@client.event
async def on_message(message):
    if message.author == client.user:
        return 
    elif message.content.split()[0] == '!track':
        try:
            email = message.content.split()[1]
            link = str(message.content.split()[2]) 
            username = str(message.author)
            await verifyLink(message, link, email, username)
        except: 
            await message.channel.send("Invalid command, please follow this format: ```!track <email address> <amazon link>```")
    else: 
        return 
client.run(getenv('TOKEN'))