from flask import make_response, jsonify, request, Blueprint
from decorators import jwt_required, admin_required
from bson import ObjectId
import globals

sub_reviews_bp = Blueprint('sub_reviews_bp', __name__)

reviews = globals.db.disneyReviews





@sub_reviews_bp.route("/reviews/<string:id>/reviews", methods=['POST'])
@jwt_required
def add_new_review(id):
    print(f"Received POST request to add review ID: {id}")
    #new review sub document
    new_review = {
        '_id' : ObjectId(),
        'name' : request.form['name'],
        'comment' : request.form['comment'], #create new review
        'stars' : request.form['stars']
    }
    update_review = reviews.update_one( #update main review
        {"_id": ObjectId(id)},
        {"$push" : {"review" : new_review }
    })
    if update_review.matched_count == 1: #check to see if update was successful
        update_review = reviews.find_one({"_id": ObjectId(id)})
        print(f"Updated review: {update_review}")

    new_review_link = "http://localhost:5000/reviews/" + id + "/reviews/" + str(new_review['_id'])
    return make_response(jsonify({"url" : new_review_link}), 201) #new review link


@sub_reviews_bp.route("/reviews/<string:b_id>/reviews", methods=['GET'])
@jwt_required
def fetch_all_reviews(b_id):
    data_to_return = []
    try:
        user_review = reviews.find_one({"_id": ObjectId(b_id)}, { "review" : 1, "_id" : 0 } ) #retrieve review by using ID and select review

        if not user_review:
            return make_response(jsonify({"error" : "Invalid review ID"}), 404)

        if 'review' not in user_review: #check to see it exists
            return make_response(jsonify({"error" : "No sub-review found"}), 404)

        for review_one in user_review['review']: #convert each sub-review ID and add it to the list
            review_one['_id'] = str(review_one['_id'])
            data_to_return.append(review_one)

        return make_response(jsonify(data_to_return), 200)

    except Exception as e:
        print(f'Exception occurred while fetching reviews: {e}')
        return make_response(jsonify({"error": "An error occurred while fetching reviews"}), 500)


@sub_reviews_bp.route("/reviews/<string:b_id>/reviews/<string:r_id>", methods=['GET'])
@jwt_required
def fetch_one_review(b_id, r_id):
    print(f"Received GET request to fetch review with Business ID: {b_id} and Review ID: {r_id}")
    review = reviews.find_one({"_id": ObjectId(b_id)}, { "review" : 1, "_id" : 0 } )

    if review is None: #check if main review was found
        print(f"No review found with ID: {r_id}")
        return make_response(jsonify({"error" : "Invalid Review or Business ID"}), 404)
    review['review'][0]['_id'] = str(review['review'][0]['_id']) #Convert the sub-review ID to a string for JSON serialization
    print(f"Successfully retrieved review: {review}")
    return make_response(jsonify(review['review'][0]), 200)


@sub_reviews_bp.route("/reviews/<string:b_id>/reviews/<string:r_id>", methods=['PUT'])
@jwt_required
def edit_one_review(b_id, r_id):
    # Create a dictionary with the updated fields for the sub-review
    edited_review = {
        "review.$.name" : request.form['name'],
        "review.$.comment" : request.form['comment'],
        "review.$.stars" : request.form['stars']
    }
    # Update the specific sub-review using its ID
    reviews.update_one( {
        "review._id" : ObjectId(r_id),
    }, {
        "$set" : edited_review
    })
    edited_review_url = "http://localhost:5000/reviews/" + b_id + "/reviews/" + r_id
    print(f"Review successfully updated: {edited_review_url}")
    return make_response(jsonify({"url" : edited_review_url}), 200)

@sub_reviews_bp.route("/reviews/<string:b_id>/reviews/<string:r_id>", methods=['DELETE'])
@jwt_required
@admin_required
def delete_one_review(b_id, r_id):
    print(f"Successfully Received DELETE request for review ID: {b_id} and Review ID: {r_id}")
    # Update the main review document by pulling the sub-review with the specified ID
    reviews.update_one({
        "_id": ObjectId(b_id),
    }, {
        "$pull" : {"review" : {"_id": ObjectId(r_id)}},
    })
    print(f"Successfully deleted review: {reviews.find_one({"_id": ObjectId(b_id)})}")
    return make_response(jsonify({}), 200)