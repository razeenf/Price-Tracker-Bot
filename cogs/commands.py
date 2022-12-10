import discord
from discord.ext import commands
from data import add, remove, view
from scraper import Scraper
import re

class commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def view(self, ctx):
        products = view(ctx.author.id)
        empty = True
        embed = discord.Embed(title="Products You're Currently Tracking:", color=discord.Color.orange())
        embed.set_footer(text='You can view up to 25 products.')
        await ctx.send("Fetching your products...")
        for doc in products:
            empty = False
            name = await Scraper().scrape('title', doc[0])    
            embed.add_field(name=f"{name}", value=f"Price: ${doc[1]} | [Product Page](https://www.amazon.ca/dp/{doc[0]})", inline=False)
        if empty:
            embed.add_field(name="You're not tracking any products.", value="Use `!track <email> <product link>` to start tracking a product.", inline=False)   
        await ctx.send(embed=embed)
    
    @commands.command()
    async def track(self, ctx, email, *, link):
        userID = ctx.author.id
        channelID = ctx.channel.id
        asin = await verify(link)   
        if asin is False:
            response = "Invalid link, make sure it's an Amazon.ca product page link."  
        elif '@' not in email or '.com' not in email:
            response = "Invalid email."
        else:
            output = await add(asin, email, userID, channelID)
            if output is False:
                response = "That product is not in stock so I cannot track it for price drops."
            else: response = "Your item is being tracked, you'll be notified via discord & email when the price drops!"
        await ctx.send(response)

    @commands.command()
    async def stop(self, ctx, link):
        asin = await verify(link)   
        if asin is False:
            response = "Invalid link, make sure it's an Amazon.ca product page link."          
        else:
            remove(ctx.author.id, asin) 
            response = "You are no longer tracking this item."
        await ctx.send(response)

    @commands.command()
    async def help(self, ctx):
        await ctx.send("To start tracking a product use:"
        +"```yaml\n!track <email address> <amazon link>```"
        +"To view your tracked products use:"
        +"```yaml\n!view```"
        +"To stop tracking a product use:"
        +"```yaml\n!stop <amazon link>```")

async def verify(link):
    if link.startswith("https://www.amazon.ca/") and 'B0' in link:
        asin = re.search(r'/[dg]p/([^/]+)', link, flags=re.IGNORECASE).group(1)
        if asin[:2] != 'B0':
            asin = re.search(r'/product/([^/]+)', link, flags=re.IGNORECASE).group(1)
        return asin
    else:
        return False

async def setup(bot):
    await bot.add_cog(commands(bot))