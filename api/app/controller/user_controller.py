from flask_restful import Resource
from app import api

class UserController(Resource):
    def get(self):
        return ["dummy"]

def addResources(api):
    api.add_resource(UserController, '/')

addResources(api)