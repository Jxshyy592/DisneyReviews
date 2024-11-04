from flask import make_response, jsonify, request
from decorators import jwt_required, admin_required
from flask import Blueprint
from bson import ObjectId
import jwt
import datetime
import bcrypt
import globals


auth_bp = Blueprint('auth_bp', __name__)

blacklist = globals.db.blacklist
users = globals.db.users



@auth_bp.route("/login", methods=['GET'])
def login():
    auth = request.authorization # Retrieves authorization credentials
    if auth:
        # Searches for the user by username in the database
        user = users.find_one({"username": auth.username})
        if user is not None:
            # Verifies the password using bcrypt
            if bcrypt.checkpw(bytes(auth.password, 'UTF-8'), user['password']):
                token = jwt.encode( {
                    'user' : auth.username, # jwt token gets generated with username, admin status and expiration time
                    'admin' : user['admin'],
                    'exp' : datetime.datetime.now( datetime.UTC ) + datetime.timedelta(minutes = 30)
                }, globals.secret_key, algorithm='HS256')
                print("Token successfully generated")
                return make_response(jsonify({'token' : token}), 200)
            else:
                # Error returned if password is incorrect
                return make_response(jsonify({'error': 'Invalid Password'}), 401)
        else:
            # Error returned if username is incorrect
            return make_response(jsonify({'error': 'Invalid Username'}), 401)
        # Error returned if authentication details are missing
    return make_response(jsonify({'message': 'Authentication Required'}), 401)


@auth_bp.route('/logout', methods=['GET'])
@jwt_required
def logout():
    token = request.headers['x-access-token'] # Retrieves token from header
    blacklist.insert_one({'token' : token}) # Inserts token to blacklist db
    return make_response(jsonify({'message': 'Logged out Successfully'}), 200) # Return message


@auth_bp.route('/register', methods=['POST'])
def create_users():
    # Checks all fields are present
    if not all(key in request.form for key in ['name', 'username', 'password', 'email']):
        return make_response(jsonify({'error' : 'All fields required (name, username, email, password)'}), 400) # If all fields aren't present

    password = request.form['password']
    user_password = bcrypt.hashpw(bytes(password, 'UTF-8'), bcrypt.gensalt()) # Hashes the password using bcrypt


    # Check to see if field already exists
    if users.find_one({"username": request.form['username']}) or users.find_one({"email": request.form['email']}):
        return make_response(jsonify({'error': 'Username or email already exists'}), 409)

    create_user = {
           'name' : request.form['name'],
           'username' : request.form['username'], # Creates a new user document
           'password' : user_password,
           'email' : request.form['email'],
           'admin' : False
    }
    new_user_id = users.insert_one(create_user) # Inserts new user into database users

    new_user_link = "http://localhost:5000/users/" \
                      + str(new_user_id.inserted_id)
    return make_response(jsonify({"url": new_user_link}), 201)


@auth_bp.route("/users/<string:u_id>", methods=['DELETE'])
@jwt_required
@admin_required
def delete_user_review(u_id):
    print(f"Received DELETE request for review ID: {u_id}")
    result = users.delete_one({"_id": ObjectId(u_id)})
    if result.deleted_count == 1:
        print("User successfully deleted.")
        return make_response(jsonify( {} ), 200)
    else:
        print("No user found with the provided ID.")
        return make_response(jsonify({"error" : "Invalid User ID"}), 404)

@auth_bp.route("/users/", methods=['GET'])
@jwt_required
@admin_required
def show_all_users():
    print("GET request received")
    page_num = request.args.get('pn', default=1, type=int)
    page_size = request.args.get('ps', default=10, type=int) # Using pagination to display users to the admins
    page_start = page_size * (page_num - 1)
    print("Requested page number:", page_num)
    print("Requested page size:", page_size)

    filter_query = {}

    # Filters the db for specific requests to username and email
    if 'username' in request.args:
        filter_query['username'] = request.args['username']
    if 'email' in request.args:
        filter_query['email'] = request.args['email']

    data_to_return = []
    try:
        # Searches for users with the specified filters and pagination, excluding the password field
        users_search = users.find(filter_query, {"password": 0}).skip(page_start).limit(page_size)
        for user in users_search:
            user['_id'] = str(user['_id'])  # Converts the ObjectId to a string for JSON compatibility
            data_to_return.append(user)

        if not data_to_return: #If no user is found
            return make_response(jsonify({"error" : "No users found"}), 404)
        return make_response(jsonify(data_to_return), 200)

    except Exception as e:
        print(f'Exception occurred while fetching users: {e}')
        return make_response(jsonify({"error" : "An error occurred while fetching users"}), 500)