from flask import Flask, make_response, jsonify, request
from pymongo import MongoClient
from bson import ObjectId
import random
app = Flask(__name__)


client = MongoClient("mongodb://127.0.0.1:27017")
db = client.mainData
reviews = db.disneyReviews



@app.route("/reviews/<string:review_id>", methods=['GET'])
def show_one_review(review_id):
    print("Received review_id:", review_id)
    review_id = review_id.strip()
    print(f"Processed review_id: '{review_id}'")
    try:
        review = reviews.find_one({"_id": ObjectId(review_id)})

        if not review:
            return make_response(jsonify({"error" : "Review not found"}), 404)

        review['_id'] = str(review['_id'])

        return make_response(jsonify(review), 200)
    except Exception as e:
        return make_response(jsonify({"error" : "Invalid ID field"}), 400)


@app.route("/reviews", methods=['GET'])
def show_all_reviews():
    page_num = request.args.get('pn', default=1, type=int)
    page_size = request.args.get('ps', default=10, type=int)
    page_start = page_size * (page_num - 1)

    data_to_return = []
    for review in reviews.find().skip(page_start).limit(page_size):
        review['_id'] = str(review['_id'])
        data_to_return.append(review)

    return make_response(jsonify(data_to_return), 200)


@app.route("/reviews", methods=['POST'])
def add_review():
    print("POST request received")
    if all(key in request.form for key in ['Rating', 'Reviewer_Location', 'Review', 'Branch', 'Year']):
        new_review = {
            'Rating' : request.form['Rating'],
            'Reviewer_Location' : request.form['Reviewer_Location'],
            'Review' : request.form['Review'],
            'Branch' : request.form['Branch'],
            'Year' : request.form['Year']
        }
        new_review_id = reviews.insert_one(new_review)
        new_review_link = "http://localhost:5000/reviews/" \
                          + str(new_review_id.inserted_id)
        return make_response(jsonify({"url" : new_review_link}), 201)
    else:
        return make_response(jsonify({"error" : "Missing Form Field"}), 400)


@app.route("/reviews/<string:id>", methods=['PUT'])
def edit_review(id):
    if all(key in request.form for key in ['Rating', 'Reviewer_Location', 'Review', 'Branch', 'Year']):
        result = reviews.find_one({"_id": ObjectId(id)}, {
                "$set" : {
                    "Rating" : request.form['Rating'],
                    "Reviewer_Location" : request.form['Reviewer_Location'],
                    "Review" : request.form['Review'],
                    "Branch" : request.form['Branch'],
                    "Year" : request.form['Year']
                }
        })
        if result.matched_count == 1:
            edited_review_link = "https://localhost:5000/reviews/" + id
            return make_response(jsonify({"url" : edited_review_link }), 200)
        else:
            return make_response(jsonify({"error" : "Invalid review ID"}), 404)
    else:
        return make_response(jsonify({"error" : "Missing Form Field"}), 404)





if __name__ == '__main__':
    app.run(debug=True)