import discord
from discord.ext import tasks
from dotenv import load_dotenv
from os import getenv
from main import add, main, remove
import re

load_dotenv('.env')
intents = discord.Intents.all()
intents.messages = True
client = discord.Client(intents=intents)

async def verify(link):
    if link.startswith("https://www.amazon.ca/") and 'B0' in link:
        asin = re.search(r'/[dg]p/([^/]+)', link, flags=re.IGNORECASE).group(1)
        if asin[:2] != 'B0':
            asin = re.search(r'/product/([^/]+)', link, flags=re.IGNORECASE).group(1)
        return asin
    else:
        return False

async def track(message, asin, email, username):
    if asin is False:
        response = "Invalid link, make sure it's an Amazon.ca product page link."  
    elif '@' and '.com' not in email:
        response = "Invalid email."
    else:
        await add(asin, email, username)
        response = "Your item is being tracked, you'll be notified via email when the price drops!"
    await message.channel.send(response)

async def stop(message, asin, username):
    if asin is False:
        response = "Invalid link, make sure it's an Amazon.ca product page link."          
    else:
        remove(username, asin) 
        response = "You are no longer tracking this item."
    await message.channel.send(response)

@tasks.loop(minutes=30)
async def checkPrices():
    await main()
    print("Price checking complete.")

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Amazon Prices"))
    checkPrices.start()
    print(f'{client.user} is now running!')

@client.event
async def on_message(message):
    if message.author == client.user:
        return 

    if message.content.startswith('!track'):
        try:
            email = message.content.split()[1]
            link = str(message.content.split()[2]) 
            username = str(message.author)
            await track(message, await verify(link), email, username)
        except IndexError: 
            await message.channel.send("Invalid Command, Try: !commands")
    elif  message.content.startswith('!stop'):
        try:
            link = str(message.content.split()[1]) 
            username = str(message.author)
            await stop(message, await verify(link), username)
        except IndexError: 
            await message.channel.send("Invalid Command, Try: !commands")
    elif message.content.startswith('!commands'):
        await message.channel.send("```!track <email address> <amazon link>```" +"```!stop <amazon link>```")
    else:
        return

client.run(getenv('TOKEN'))