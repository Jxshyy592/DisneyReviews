from flask import Flask, make_response, jsonify, request
from pymongo import MongoClient
from bson import ObjectId
import random
app = Flask(__name__)


client = MongoClient("mongodb://127.0.0.1:27017")
db = client.first
reviews = db.disneyReviews



@app.route("/", methods=['GET'])
def index():
    return make_response( "<h1>Lil dude running about<h1>", 200 )





if __name__ == '__main__':
    app.run(debug=True)