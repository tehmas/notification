# from app import app

# if __name__=='__main__':
#     app.run(host='0.0.0.0', port=80)

import pika
import os
from functools import partial
import pymongo
from bson.objectid import ObjectId
import re

def process_message(db, channel, method, header, body):
    try:
        notification = retrieve_notifcation(db, body)
        users = retrieve_users(db,\
            notification['receivers'],\
                notification['groupFlag'])
    except Exception as e:
        print (str(e))

    channel.basic_ack(method.delivery_tag)

# TODO: Should move such methods to a repository
def retrieve_users(db, receivers, groupFlag):
    if (groupFlag=='Y'):
        return list(retrieve_users_by_groups(\
            db, receivers))   

    return list(retrieve_users_by_ids(\
        db, receivers))

# TODO: Project only specific properties
def retrieve_users_by_ids(db, userIds):
    return db.user.find(\
        get_id_filter_query(userIds))

# TODO: Project only specific properties
def retrieve_users_by_groups(db, groups):
    return db.user.find(\
        get_group_filter_query(groups))

def get_id_filter_query(ids):
    objectIdList = []
    for i in ids:
        objectIdList.append(ObjectId(i))
    print (objectIdList)
    return { "_id" : { "$in": objectIdList}}

def get_group_filter_query(groups):
    query = {}
    for g in groups:
        condition = re.split('[:]', g)
        query[condition[0]]=condition[1]
    return query

# TODO: A redis cache layer would be effective
def retrieve_notifcation(db, id):
    print ('retrieving notification')
    return db.notification\
        .find_one({'_id':ObjectId(\
            id.decode("utf-8"))})

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