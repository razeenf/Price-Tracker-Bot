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

async def scrape(asin):
    asession = AsyncHTMLSession() 
    page = await asession.get(f'https://www.amazon.ca/gp/product/{asin}')
    await page.html.arender(timeout = 20) 
    try:
        title = page.html.find('#productTitle')[0].text 
        price = page.html.find('.a-offscreen')[0].text.replace('$','').strip()
    except:
        whole = page.html.find('.a-price-whole')[0].text
        fraction = page.html.find('.a-price-fraction')[0].text
        price = whole+fraction
    await asession.close() 
    print(title, price)
    return price, title

async def track(asin, email, username):
    asinList = collection.distinct("entry.ASIN")
    usernameList = collection.distinct("entry.user-info.username")
    if asin in asinList and username not in usernameList:
        collection.update_one(
            {"entry.ASIN" : asin},
            {"$push": {
                    "entry.user-info": {
                        "username": f"{username}",
                        "email": f"{email}"
                    }
                }
            }
        )
    elif asin not in asinList:
        price = (await scrape(asin))[0]
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

def notify(document, title, price, listedPrice, discount):
    for userInfo in document["user-info"]:
        createMessage(userInfo["email"], userInfo["username"], title, price, listedPrice, discount, document["ASIN"]) 
    collection.delete_one({"entry.ASIN":document["ASIN"]}) #delete the doc where the entry.ASIN matches the ASIN of current open doc

def comparePrice(price_title, document):
    price = price_title[0]
    title = price_title[1]
    listedPrice = document["price"]
    if float(price) < listedPrice:
        discount = int(((listedPrice-float(price))/listedPrice)*100)
        print("On sale. Sending out emails...")
        notify(document, title, price, listedPrice, discount)
    else:
        print("No sale.")

async def main():
    for document in collection.distinct("entry"):
        price_title = await scrape(document["ASIN"])
        comparePrice(price_title, document)