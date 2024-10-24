from flask import Flask, make_response, jsonify, request
from pymongo import MongoClient
from bson import ObjectId
import random
app = Flask(__name__)


client = MongoClient("mongodb://127.0.0.1:27017")
db = client.first
reviews = db.disneyReviews








@app.route("/api/v1.0/reviews", methods=["GET"])
def show_all_reviews():
    return make_response(jsonify(reviews), 200)


@app.route("/api/v1.0/reviews", methods=['GET'])
def get_all_reviews():
    page_num, page_size = 1, 10
    if request.args.get("pn"):
        page_num = int(request.args.get("pn"))
    if request.args.get("ps"):
        page_size = int(request.args.get("ps"))
    page_start = (page_num - 1) * page_size

    data_to_return = []
    for review in reviews.find().skip(page_start).limit(page_size):
        review['_id'] = str(review['_id'])
        for text in review['reviews']:
            text['_id'] = str(text['_id'])
        data_to_return.append(review)

    return make_response(jsonify(data_to_return), 200)



@app.route("/api/v1.0/reviews/<string:id>", methods=['GET'])
def show_one_review(id):
    review = reviews.find_one({'_id': ObjectId(id)})
    if review is not None:
        review['_id'] = str(review['_id'])
        for text in review['reviews']:
            text['_id'] = str(text['_id'])
        return make_response(jsonify (review), 200)
    else:
        return make_response(jsonify({ "error" : "Invalid review ID"}), 404)




if __name__ == '__main__':
    app.run(debug=True)