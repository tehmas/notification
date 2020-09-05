from flask import Flask
from flask_restful import Resource, Api
from flask_pymongo import PyMongo

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://mongo27017/notification'
mongo = PyMongo(app)
api = Api(app)

from app.controller import *