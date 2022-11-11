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
    async def mention(self, userID, channelID, discount, asin):
        channel = self.bot.get_channel(channelID)
        await channel.send(f"Hey <@{userID}>, A product your tracking is on sale for **{discount}%** off! Buy it here: https://www.amazon.ca/dp/{asin}")

    async def notify(self, document, current_price, discount):
        title = await scrape('title', document["ASIN"])     
        for userInfo in document["user-info"]:
            await self.mention(userInfo["userID"], userInfo["channelID"], discount, document["ASIN"])
            create_message(userInfo["email"], self.bot.get_user(userInfo["userID"]), title, current_price, document["price"], discount, document["ASIN"]) 
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