from flask_restful import Resource
from flask import request, jsonify
from app import api, mongo
from marshmallow import Schema, fields, ValidationError
import pika
import os
from functools import partial
import json

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
            notification_id = str(result.inserted_id)
            self.enqueue_notification(notification_id)
            return {'Data':{'id':notification_id}}, 200
        except:
            return {'Error':'Could not send notification'}, 400

    # TODO: A common utility class is needed
    def enqueue_notification(self, notification_id):
        parameters = pika.URLParameters(os.environ['RABBITMQ_AMQP_URL'])
        connection = pika.SelectConnection(parameters, \
            on_open_callback=partial(self.on_conn_open, notification_id))
        connection.ioloop.start()
    
    def on_conn_open(self, notification_id, connection):
        connection.channel(on_open_callback=\
            partial(self.on_channel_open, notification_id, connection))

    def on_channel_open(self, notification_id, connection, channel):
        channel.queue_declare(queue='notification_queue',\
            callback=partial(self.on_queue_declared,\
                channel, connection, notification_id))

    def on_queue_declared(self, channel, connection, notification_id, frame):
        channel.basic_publish(exchange='',\
            routing_key='notification_queue',\
                body=notification_id,
                properties=pika.BasicProperties(\
                    delivery_mode=2, \
                        content_type= 'text/plain'))
        connection.close()
        connection.ioloop.stop()

def add_resources(api):
    api.add_resource(NotificationController, '/notification')

add_resources(api)
