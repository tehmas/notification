# from app import app

# if __name__=='__main__':
#     app.run(host='0.0.0.0', port=80)

import pika
import os
from functools import partial
import pymongo

def process_message(db, channel, method, header, body):
    print ('processing..')
    print (body)
    print ('processed.')
    channel.basic_ack(method.delivery_tag)

def on_conn_open(db, connection):
    print ('connection opened')
    connection.channel(on_open_callback=\
        partial(on_channel_open, db))

def on_channel_open(db, channel):
    print ('channel opened')
    channel.queue_declare(queue='notification_queue',\
            callback=partial(on_queue_declared,\
                db,\
                    channel),\
                        durable=True)

def on_queue_declared(db, channel, frame):
    print ('queue declared')
    # for fair dispatch
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='notification_queue',\
         on_message_callback=partial(process_message,\
             db))

def main():
    client = pymongo.MongoClient("mongodb://mongo:27017")
    db = client[os.environ["MONGO_DB_NAME"]]

    parameters = pika.URLParameters(os.environ['RABBITMQ_AMQP_URL'])
    connection = pika.SelectConnection(parameters, \
            on_open_callback=partial(on_conn_open, db))
    connection.ioloop.start()

if __name__ == '__main__':
    main()