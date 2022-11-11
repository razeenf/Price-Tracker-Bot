from pymongo import MongoClient
import certifi
from dotenv import load_dotenv
from os import getenv
from scraper import scrape

load_dotenv('.env')
cluster = MongoClient(getenv('LOGIN'), tlsCAFile=certifi.where())
db = cluster["Amazon-Price-Tracker"]
collection = db["Entries"]

async def add(asin, email, userID, channelID):
    asinList = collection.distinct("entry.ASIN")
    if asin in asinList: 
        collection.update_one( 
            {"entry.ASIN" : asin},
            {"$addToSet": {
                    "entry.user-info": {
                        "email": f"{email}",
                        "userID": userID,
                        "channelID": channelID
                    }
                }
            }
        )
    elif asin not in asinList:
        price = await scrape('price', asin)
        entry = {"entry": 
            {
                "ASIN": f"{asin}",
                "price": float(price),
                "user-info": [
                {
                    "email":f"{email}",
                    "userID": userID,
                    "channelID": channelID
                }]
            }
        }
        collection.insert_one(entry)

def remove(userID, asin):
    asinList = collection.distinct("entry.ASIN")
    if asin in asinList: 
        collection.update_one(
            {"entry.ASIN" : asin},
            {"$pull": {
                    "entry.user-info": {
                        "userID": userID
                    }
                }
            }
        )
    collection.delete_one({ "entry.user-info.0":{"$exists":False}})

def fetch_data():
    return collection