from flask import make_response, jsonify, request
import jwt
from functools import wraps
import globals


blacklist = globals.db.blacklist


def jwt_required(func):
    @wraps(func)
    def jwt_required_wrapper(*args, **kwargs):
        token = None #Initialize token variable
        if 'x-access-token' in request.headers: #check for x-access-token in header
            token = request.headers['x-access-token']
        if not token:
            return make_response(jsonify({'message': 'Token is missing'}), 401)
        try:
            data = jwt.decode(token, globals.secret_key, algorithms='HS256') #decode the token using secret key and algorithm
        except: #if decoding fails
            return make_response(jsonify({'message': 'Token is invalid'}), 401)
        bl_token = blacklist.find_one({'token': token})
        if bl_token is not None: #if token is blacklisted
            return make_response(jsonify({'message': 'Token is no longer valid'}), 401)
        return func(*args, **kwargs)
    return jwt_required_wrapper


def admin_required(func):
    @wraps(func)
    def admin_required_wrapper(*args, **kwargs):
        token = request.headers['x-access-token'] #retrieve token from header
        data = jwt.decode(token, globals.secret_key, algorithms='HS256') #decode the token
        if data['admin']: #if admin then proceed
            return func(*args, **kwargs)
        else: #if not admin
            return make_response(jsonify({'message': 'Admin Required'}), 401)
    return admin_required_wrapper
