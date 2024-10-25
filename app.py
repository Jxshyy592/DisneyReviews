from flask import Flask, make_response, jsonify, request
from pymongo import MongoClient
from bson import ObjectId
import random
app = Flask(__name__)


client = MongoClient("mongodb://127.0.0.1:27017")
db = client.mainData
reviews = db.disneyReviews



#@app.route("/", methods=['GET'])
#def index():
 #   return make_response( "<h1>Lil dude running about<h1>", 200 )

@app.route("/reviews", methods=['GET'])
def show_one_review():
    review_id = request.args.get("id", type=int)
    data_to_return = [ review for review in reviews if review['id'] == review_id ]

    if not data_to_return:
        return make_response( jsonify({"error": "Review not found"}), 200 )



if __name__ == '__main__':
    app.run(debug=True)