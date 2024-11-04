from pymongo import MongoClient

secret_key = 'mysecretkey'

client = MongoClient("mongodb://127.0.0.1:27017")
db = client.mainData