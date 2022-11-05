from requests_html import AsyncHTMLSession
import asyncio
from gmail import createMessage
import pymongo
import certifi
from pymongo import MongoClient
from dotenv import load_dotenv
from os import getenv

load_dotenv('.env')
cluster = pymongo.MongoClient(getenv('LOGIN'), tlsCAFile=certifi.where())
db = cluster["Amazon-Price-Tracker"]
collection = db["Entries"]

async def scrape(asin, type):
    asession = AsyncHTMLSession() 
    page = await asession.get(f'https://www.amazon.ca/gp/product/{asin}')
    await page.html.arender(timeout = 20)  
    if type == 1:
        try:
            price = page.html.find('.a-offscreen')[0].text.replace('$','').strip()
        except IndexError:
            whole = page.html.find('.a-price-whole')[0].text
            fraction = page.html.find('.a-price-fraction')[0].text
            price = whole+fraction
        await asession.close() 
        print(price)
        return price
    elif type == 2:
        title = page.html.find('#productTitle')[0].text 
        await asession.close() 
        return title

async def add(asin, email, username):
    asinList = collection.distinct("entry.ASIN")
    if asin in asinList: 
        collection.update_one( 
            {"entry.ASIN" : asin},
            {"$addToSet": {
                    "entry.user-info": {
                        "username": f"{username}",
                        "email": f"{email}"
                    }
                }
            }
        )
    elif asin not in asinList:
        price = await scrape(asin, 1)
        entry = {"entry": 
            {
                "ASIN": f"{asin}",
                "price": float(price),
                "user-info": [
                {
                    "username":f"{username}",
                    "email":f"{email}"
                }]
            }
        }
        collection.insert_one(entry)

def remove(username, asin):
    asinList = collection.distinct("entry.ASIN")
    if asin in asinList: 
        collection.update_one(
            {"entry.ASIN" : asin},
            {"$pull": {
                    "entry.user-info": {
                        "username": f"{username}"
                    }
                }
            }
        )
    collection.delete_one({ "entry.user-info.0":{"$exists":False}})

async def notify(document, price, listedPrice, discount):
    title = await scrape(document["ASIN"], 2)     
    for userInfo in document["user-info"]:
        createMessage(userInfo["email"], userInfo["username"], title, price, listedPrice, discount, document["ASIN"]) 
    collection.delete_one({"entry.ASIN":document["ASIN"]}) 

async def compare(price, document):
    listedPrice = document["price"]
    if float(price) < listedPrice:
        discount = int(((listedPrice-float(price))/listedPrice)*100)
        if discount >= 5:
            print("On sale. Sending out emails...")
            await notify(document, price, listedPrice, discount)
    else:
        print("No sale.")

async def main():
    for document in collection.distinct("entry"):
        price = await scrape(document["ASIN"], 1)
        await compare(price, document)