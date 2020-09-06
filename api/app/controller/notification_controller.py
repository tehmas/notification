from flask_restful import Resource
from flask import request, jsonify
from app import api, mongo
from marshmallow import Schema, fields, ValidationError

class NotificationSchema(Schema):
    title = fields.String(required=True)
    message = fields.String(required=True)
    providers = fields.List(fields.String(),\
         required=True)

class NotificationController(Resource):
    def post(self):
        inputModel = request.get_json()

        is_schema_invalid = bool(NotificationSchema()\
            .validate(inputModel))
        
        if (is_schema_invalid == True):
            return {"Error":"invalid schema"}, 500
        
        try:
            result = mongo.db.notification.insert_one(inputModel)
            return {'Data':{'id':str(result.inserted_id)}}, 200
        except:
            return {'Error':'Could not send notification'}, 400

def add_resources(api):
    api.add_resource(NotificationController, '/notification')

add_resources(api)
