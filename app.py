from flask import Flask, make_response, jsonify, request
from pymongo import MongoClient
from bson import ObjectId
import random
import jwt
import datetime
from functools import wraps
import bcrypt
app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey'


client = MongoClient("mongodb://127.0.0.1:27017")
db = client.mainData
reviews = db.disneyReviews



def jwt_required(func):
    @wraps(func)
    def jwt_required_wrapper(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return make_response(jsonify({'message': 'Token is missing'}), 401)
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms='HS256')
        except:
            return make_response(jsonify({'message': 'Token is invalid'}), 401)
        return func(*args, **kwargs)
    return jwt_required_wrapper

@app.route("/reviews/<string:review_id>", methods=['GET'])
@jwt_required
def show_one_review(review_id):
    print("Received review_id:", review_id)
    review_id = review_id.strip()
    print(f"Processed review_id: '{review_id}'")

    data_to_return = []
    try:
        review = reviews.find_one({"_id": ObjectId(review_id)})

        if 'review' in review:
            for sub_review in review['review']:
                sub_review['_id'] = str(sub_review['_id'])

        data_to_return.append(review)

        if not review:
            return make_response(jsonify({"error" : "Review not found"}), 404)

        review['_id'] = str(review['_id'])

        return make_response(jsonify(review), 200)
    except Exception as e:
        return make_response(jsonify({"error" : "Invalid ID field"}), 400)


@app.route("/reviews", methods=['GET'])
def show_all_reviews():
    print("GET request received")
    page_num = request.args.get('pn', default=1, type=int)
    page_size = request.args.get('ps', default=10, type=int)
    page_start = page_size * (page_num - 1)
    print("Requested page number:", page_num)
    print("Requested page size:", page_size)

    data_to_return = []
    try:
        for review in reviews.find().skip(page_start).limit(page_size):
            review['_id'] = str(review['_id'])

            if 'review' in review:
                for sub_review in review['review']:
                    sub_review['_id'] = str(sub_review['_id'])

            data_to_return.append(review)

        if not data_to_return:
            return make_response(jsonify({"error" : "No reviews found"}), 404)
        return make_response(jsonify(data_to_return), 200)

    except Exception as e:
        print(f'Exception occurred while fetching reviews: {e}')
        return make_response(jsonify({"error" : "An error occurred while fetching reviews"}), 500)



@app.route("/reviews", methods=['POST'])
def add_review():
    print("POST request received")
    print("Received form data:", request.form)
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
        missing_fields = [key for key in ['Rating', 'Reviewer_Location', 'Review', 'Branch', 'Year'] if key not in request.form]
        print("Missing form fields:", missing_fields)
        return make_response(jsonify({"error" : "Missing Form Field(s)" + ", ".join(missing_fields)}), 400)


@app.route("/reviews/<string:id>", methods=['PUT'])
def edit_review(id):
    print(f"Received PUT request to edit review ID: {id}")
    if all(key in request.form for key in ['Rating', 'Reviewer_Location', 'Review', 'Branch', 'Year']):
        print("All required fields detected.")
        result = reviews.update_one({"_id": ObjectId(id)}, {
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
            print("Review successfully updated.")
            return make_response(jsonify({"url" : edited_review_link }), 200)
        else:
            return make_response(jsonify({"error" : "Invalid review ID"}), 404)
    else:
        missing_fields = [key for key in ['Rating', 'Reviewer_Location', 'Review', 'Branch', 'Year'] if key not in request.form]
        print(f"Missing form fields: {missing_fields}")
        return make_response(jsonify({"error : Missing Field Entry" : missing_fields}), 404)



@app.route("/reviews/<string:id>", methods=['DELETE'])
def delete_review(id):
    print(f"Received DELETE request for review ID: {id}")
    result = reviews.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 1:
        print("Review successfully deleted.")
        return make_response(jsonify( {} ), 200)
    else:
        print("No review found with the provided ID.")
        return make_response(jsonify({"error" : "Invalid Review ID"}), 404)


@app.route("/reviews/<string:id>/reviews", methods=['POST'])
def add_new_review(id):
    print(f"Received POST request to add review ID: {id}")
    new_review = {
        '_id' : ObjectId(),
        'name' : request.form['name'],
        'comment' : request.form['comment'],
        'stars' : request.form['stars']
    }
    update_review = reviews.update_one(
        {"_id": ObjectId(id)},
        {"$push" : {"review" : new_review }
    })
    if update_review.matched_count == 1:
        update_review = reviews.find_one({"_id": ObjectId(id)})
        print(f"Updated review: {update_review}")

    new_review_link = "http://localhost:5000/reviews/" + id + "/reviews/" + str(new_review['_id'])
    return make_response(jsonify({"url" : new_review_link}), 201)


@app.route("/reviews/<string:id>/reviews", methods=['GET'])
def fetch_all_reviews(id):
    data_to_return = []
    review = reviews.find_one({"_id": ObjectId(id)}, { "review" : 1, "_id" : 0 } )
    for review_one in review['review']:
        review_one['_id'] = str(review_one['_id'])
        data_to_return.append(review_one)
    return make_response(jsonify(data_to_return), 200)


@app.route("/reviews/<string:b_id>/reviews/<string:r_id>", methods=['GET'])
def fetch_one_review(b_id, r_id):
    print(f"Received GET request to fetch review with Business ID: {b_id} and Review ID: {r_id}")
    review = reviews.find_one({"_id": ObjectId(b_id)}, { "review" : 1, "_id" : 0 } )

    if review is None:
        print(f"No review found with ID: {r_id}")
        return make_response(jsonify({"error" : "Invalid Review or Business ID"}), 404)
    review['review'][0]['_id'] = str(review['review'][0]['_id'])
    print(f"Successfully retrieved review: {review}")
    return make_response(jsonify(review['review'][0]), 200)


@app.route("/reviews/<string:b_id>/reviews/<string:r_id>", methods=['PUT'])
def edit_one_review(b_id, r_id):
    edited_review = {
        "review.$.name" : request.form['name'],
        "review.$.comment" : request.form['comment'],
        "review.$.stars" : request.form['stars']
    }
    reviews.update_one( {
        "review._id" : ObjectId(r_id),
    }, {
        "$set" : edited_review
    })
    edited_review_url = "http://localhost:5000/reviews/" + b_id + "/reviews/" + r_id
    print(f"Review successfully updated: {edited_review_url}")
    return make_response(jsonify({"url" : edited_review_url}), 200)

@app.route("/reviews/<string:b_id>/reviews/<string:r_id>", methods=['DELETE'])
def delete_one_review(b_id, r_id):
    print(f"Successfully Received DELETE request for review ID: {b_id} and Review ID: {r_id}")
    reviews.update_one({
        "_id": ObjectId(b_id),
    }, {
        "$pull" : {"review" : {"_id": ObjectId(r_id)}},
    })
    print(f"Successfully deleted review: {reviews.find_one({"_id": ObjectId(b_id)})}")
    return make_response(jsonify({}), 200)

@app.route("/login", methods=['GET'])
def login():
    auth = request.authorization
    if auth and auth.password == 'password':
        token = jwt.encode( {
            'user' : auth.username,
            'exp' : datetime.datetime.now( datetime.UTC ) + datetime.timedelta(minutes = 30)
        }, app.config['SECRET_KEY'], algorithm='HS256')
        print("Token successfully generated")
        return make_response(jsonify({'token' : token}), 200)

    print("Incorrect password provided")
    return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm = "Login required"'})



if __name__ == '__main__':
    app.run(debug=True)