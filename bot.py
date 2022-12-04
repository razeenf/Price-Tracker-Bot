import discord
from discord.ext import commands
import os 
import asyncio
from dotenv import load_dotenv
from os import getenv

load_dotenv('credentials/.env')
intents = discord.Intents.all()
intents.members = True
activity = discord.Activity(type=discord.ActivityType.watching, name="Amazon Prices")
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None, activity=activity)

async def load():
    for file in os.listdir('./cogs'):
        if file.endswith('.py'):
            await bot.load_extension(f'cogs.{file[:-3]}')

@bot.event
async def on_ready():
    print(f'\nLogged in as: {bot.user.name}\nVersion: {discord.__version__}\n')

async def main():
    await load()
    await bot.start(getenv('TOKEN'))

asyncio.run(main())