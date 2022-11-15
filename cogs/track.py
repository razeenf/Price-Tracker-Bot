import discord 
from discord.ext import commands
from discord.ext import tasks
from data import fetch_data
from scraper import scrape
from gmail import create_message

class track(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.run.start()
    
    @commands.command()
    async def mention(self, userID, channelID, sale_price, original_price, discount, asin, title, img):
        channel = self.bot.get_channel(channelID)
        embed = discord.Embed(title=f"{title}", url=f'https://www.amazon.ca/gp/product/{asin}', color=discord.Color.orange())
        embed.set_thumbnail(url=img)
        embed.add_field(name="Discount Amount:", value=f'{discount}%')
        embed.add_field(name="Original Price:", value=original_price)
        embed.add_field(name="Sale Price:", value=sale_price)
        embed.set_footer(text='This item is no longer being tracked.')
        await channel.send(f"Hey <@{userID}>, a product you're tracking is on sale!", embed=embed)

    async def notify(self, document, current_price, discount):
        details = await scrape('details', document["ASIN"])     
        for userInfo in document["user-info"]:
            await self.mention(userInfo["userID"], userInfo["channelID"], current_price, document["price"], discount, document["ASIN"], details[0], details[1])
            create_message(userInfo["email"], self.bot.get_user(userInfo["userID"]), details[0], current_price, document["price"], discount, document["ASIN"]) 
        fetch_data().delete_one({"entry.ASIN":document["ASIN"]}) 

    def compare_price(self, current_price, listed_price):
        if float(current_price) < listed_price:
            discount = int(((listed_price-float(current_price))/listed_price)*100)
            if discount >= 5:
                print("On sale.")
                return discount
        else:
            print("No sale.")

    @tasks.loop(minutes=30)
    async def run(self):
        for document in fetch_data().distinct("entry"):
            current_price = await scrape('price', document["ASIN"])
            discount = self.compare_price(current_price, document["price"])
            if discount: 
                print("Sending out emails")          
                await self.notify(document, current_price, discount)  
        
async def setup(bot):
    await bot.add_cog(track(bot))