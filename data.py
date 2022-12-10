from pymongo import MongoClient
import certifi
from dotenv import load_dotenv
from os import getenv
from scraper import Scraper

load_dotenv('credentials/.env')
cluster = MongoClient(getenv('MONGO_URI'), tlsCAFile=certifi.where())
db = cluster["Amazon-Price-Tracker"]
collection = db["Entries"]

def fetch_data():
    return collection

def view(userID):    
    for doc in collection.find({"entry.user-info.userID": userID}):
        yield doc["entry"]["ASIN"], doc["entry"]["price"]          
    
async def add(asin, email, userID, channelID):
    exists = collection.find_one({"entry.ASIN" : asin})
    if exists: 
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
    elif not exists:
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
    document = collection.find_one({"entry.ASIN" : asin})
    if document is None:
        return False
    users = document["entry"]["user-info"]
    user = [user for user in users if user["userID"] == userID]
    if user:
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
        return True
    return False
