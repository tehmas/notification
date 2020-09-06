from flask_restful import Resource
from flask import request, jsonify
from bson.objectid import ObjectId
from app import api, mongo
from pymongo import errors

class UserController(Resource):
    def get(self):
        return str(mongo.db.user\
            .find_one({'_id':ObjectId(request.args['id'])}))
    
    def post(self):
        inputModel = request.get_json()
        
        (isValid, errorMsg) = validate_user_payload(inputModel)
        if (isValid == False):
            return errorMsg, 400

        try:
            result = mongo.db.user.insert_one(inputModel)
            return {'Data':{'id':str(result.inserted_id)}}, 200
        except errors.DuplicateKeyError:
            return {'Error':'Record already exists'}, 500

def validate_user_payload(payload):
    if ('email' not in payload):
        return False, {'Error': 'email is required'}
    if ('firstName' not in payload):
        return False, {'Error': 'firstName is required'}
    return True, None

def add_resources(api):
    api.add_resource(UserController, '/user')

def setup_indexes():
    mongo.db.user.create_index("email", unique=True)

setup_indexes()
add_resources(api)