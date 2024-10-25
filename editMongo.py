from pymongo import MongoClient
import random

client = MongoClient("mongodb://127.0.0.1:27017")
db = client.mainData
reviews = db.disneyReviews

for review in reviews.find():
    reviews.update_one(
        {"_id": review["_id"] },
        {
            "$set": {
                "Year" : random.randint(2013, 2020),
                "dummy" : "test!"

        }

    }
)