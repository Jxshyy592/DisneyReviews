from flask import make_response, jsonify, request, Blueprint
from decorators import jwt_required, admin_required
from bson import ObjectId
import globals

reviews_bp = Blueprint('reviews_bp', __name__) #route variable for new bp

reviews = globals.db.disneyReviews #global variable for database access


@reviews_bp.route("/reviews/<string:review_id>", methods=['GET'])
@jwt_required
def show_one_review(review_id):
    print("Received review_id:", review_id)
    review_id = review_id.strip() #strip unwanted space in review_id
    print(f"Processed review_id: '{review_id}'")

    data_to_return = [] #empty list
    try:
        review = reviews.find_one({"_id": ObjectId(review_id)}) #find review

        if not review:
            return make_response(jsonify({"error" : "Review not found"}), 404) #if review is not found

        if 'review' in review: #check for review field
            for sub_review in review['review']: #Iterate over each sub-review within the 'review' field
                sub_review['_id'] = str(sub_review['_id']) #convert id to string

        data_to_return.append(review) #add review data to list for return

        if not review:
            return make_response(jsonify({"error" : "Review not found"}), 404)

        review['_id'] = str(review['_id']) #convert main review ID to string

        return make_response(jsonify(review), 200)
    except Exception as e:
        return make_response(jsonify({"error" : "Invalid ID field"}), 400)


@reviews_bp.route("/reviews", methods=['GET'])
def show_all_reviews():
    print("GET request received")
    page_num = request.args.get('pn', default=1, type=int)
    page_size = request.args.get('ps', default=10, type=int)
    page_start = page_size * (page_num - 1)
    print("Requested page number:", page_num)
    print("Requested page size:", page_size)

    data_to_return = []
    try:
        for review in reviews.find().skip(page_start).limit(page_size):# Query the database with pagination using skip and limit
            review['_id'] = str(review['_id'])

            if 'review' in review:
                for sub_review in review['review']:
                    sub_review['_id'] = str(sub_review['_id'])

            data_to_return.append(review)

        if not data_to_return: #no reviews found
            return make_response(jsonify({"error" : "No reviews found"}), 404)
        return make_response(jsonify(data_to_return), 200)

    except Exception as e:
        print(f'Exception occurred while fetching reviews: {e}')
        return make_response(jsonify({"error" : "An error occurred while fetching reviews"}), 500)



@reviews_bp.route("/reviews", methods=['POST'])
@jwt_required
def add_review():
    print("POST request received")
    print("Received form data:", request.form)
    if all(key in request.form for key in ['Rating', 'Reviewer_Location', 'Review', 'Branch', 'Year']):
        new_review = {
            'Rating' : request.form['Rating'],
            'Reviewer_Location' : request.form['Reviewer_Location'], #new form data
            'Review' : request.form['Review'],
            'Branch' : request.form['Branch'],
            'Year' : request.form['Year']
        }
        new_review_id = reviews.insert_one(new_review) #insert the review into the database
        new_review_link = "http://localhost:5000/reviews/" \
                          + str(new_review_id.inserted_id) #create a new link to review
        return make_response(jsonify({"url" : new_review_link}), 201)#return new review link
    else:
        missing_fields = [key for key in ['Rating', 'Reviewer_Location', 'Review', 'Branch', 'Year'] if key not in request.form] #identify which fields are missing
        print("Missing form fields:", missing_fields)
        return make_response(jsonify({"error" : "Missing Form Field(s)" + ", ".join(missing_fields)}), 400) #return this error along with missing fields for user to see


@reviews_bp.route("/reviews/<string:id>", methods=['PUT'])
@jwt_required
def edit_review(id):
    print(f"Received PUT request to edit review ID: {id}")
    if all(key in request.form for key in ['Rating', 'Reviewer_Location', 'Review', 'Branch', 'Year']): #check all fields
        print("All required fields detected.")
        result = reviews.update_one({"_id": ObjectId(id)}, { #new data to replace old data
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
            print("Review successfully updated.")                         #new review link
            return make_response(jsonify({"url" : edited_review_link }), 200)
        else:
            return make_response(jsonify({"error" : "Invalid review ID"}), 404)
    else:
        missing_fields = [key for key in ['Rating', 'Reviewer_Location', 'Review', 'Branch', 'Year'] if key not in request.form]
        print(f"Missing form fields: {missing_fields}")
        return make_response(jsonify({"error : Missing Field Entry" : missing_fields}), 404)



@reviews_bp.route("/reviews/<string:id>", methods=['DELETE'])
@jwt_required
@admin_required
def delete_review(id):
    print(f"Received DELETE request for review ID: {id}")
    result = reviews.delete_one({"_id": ObjectId(id)}) #delete review with provided ID
    if result.deleted_count == 1: #check if review was deleted
        print("Review successfully deleted.")
        return make_response(jsonify( {} ), 200)
    else:
        print("No review found with the provided ID.")
        return make_response(jsonify({"error" : "Invalid Review ID"}), 404)