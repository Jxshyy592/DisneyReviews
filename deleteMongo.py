from pymongo import MongoClient
import random


client = MongoClient("mongodb://127.0.0.1:27017")
db = client.first
reviews = db.disneyReviews

for review in reviews.find():
    reviews.update_one(
        {"_id": review["_id"] },
        {"$unset": { "Year_Month" : "" } }
    )