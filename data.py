from pymongo import MongoClient
import certifi
from dotenv import load_dotenv
from os import getenv
from scraper import Scraper

load_dotenv('credentials/.env')
cluster = MongoClient(getenv('MONGO_URI'), tlsCAFile=certifi.where())
db = cluster["Amazon-Price-Tracker"]
collection = db["Entries"]

def view(userID):    
    for doc in collection.find({"entry.user-info.userID": userID}):
        yield doc.get("entry").get("ASIN"), doc.get("entry").get("price")
    
async def add(asin, email, userID, channelID):
    asin_list = collection.distinct("entry.ASIN")
    if asin in asin_list: 
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
    elif asin not in asin_list:
        price = await Scraper().scrape('price', asin)
        if price is None:
            return False
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
    asin_list = collection.distinct("entry.ASIN")
    if asin in asin_list: 
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