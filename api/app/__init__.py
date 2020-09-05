from flask import Flask
from flask_restful import Resource, Api
from flask_pymongo import PyMongo

app = Flask(__name__)
api = Api(app)

from app.controller import user_controller

api.add_resource(user_controller.UserController, '/')