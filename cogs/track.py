import discord 
from discord.ext import commands
from discord.ext import tasks
from data import fetch_data
from scraper import Scraper
from gmail import create_message

class track(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.run.start()
    
    @commands.command()
    async def mention(self, userID, channelID, sale_price, original_price, discount, asin, title, img):
        embed = discord.Embed(title=f"{title}", url=f'https://www.amazon.ca/dp/{asin}', color=discord.Color.orange())
        embed.set_thumbnail(url=img)
        embed.add_field(name="Discount Amount:", value=f'{discount}%')
        embed.add_field(name="Original Price:", value=original_price)
        embed.add_field(name="Sale Price:", value=sale_price)
        embed.set_footer(text='This item is no longer being tracked.')
        
        if self.bot.get_channel(channelID) is not None:
            channel = self.bot.get_channel(channelID)
        elif self.bot.get_user(userID) is not None:
            print("Channel not found.")
            channel = await self.bot.fetch_user(userID)
        else: return

        await channel.send(f"Hey <@{userID}>, a product you're tracking is on sale!", embed=embed)

    async def notify(self, document, current_price, discount):    
        img = await Scraper().scrape('img', document["ASIN"]) 
        for userInfo in document["user-info"]:
            await self.mention(userInfo["userID"], userInfo["channelID"], current_price, document["price"], discount, document["ASIN"], document["title"], img)
            create_message(userInfo["email"], self.bot.get_user(userInfo["userID"]), document["title"], current_price, document["price"], discount, document["ASIN"]) 
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
            print("\nScraping", document["ASIN"])
            current_price = await Scraper().scrape('price', document["ASIN"])
            if current_price is not None:
                discount = self.compare_price(current_price, document["price"])
                if discount: 
                    print("Sending out emails...")          
                    await self.notify(document, current_price, discount)  
        
async def setup(bot):
    await bot.add_cog(track(bot))