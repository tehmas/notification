from flask import Flask
from flask_restful import Resource, Api
from flask_pymongo import PyMongo
import os

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://mongo:27017/'+\
    os.environ['MONGO_DB_NAME']
mongo = PyMongo(app)
api = Api(app)

from app.controller import *