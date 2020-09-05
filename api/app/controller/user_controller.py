from flask_restful import Resource

class UserController(Resource):
    def get(self):
        return ["dummy"]
