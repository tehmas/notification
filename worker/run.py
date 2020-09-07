import pika
import os
from functools import partial
import pymongo
from bson.objectid import ObjectId
import re
import json

def process_message(db, channel, delivery, header, body):
    try:
        notificationId = body.decode("utf-8")
        notification = retrieve_notifcation(db, notificationId)
        users = retrieve_users(db,\
            notification['receivers'],\
                notification['groupFlag'])
        send_provider_requests(users, \
            notificationId, \
                notification["providers"], \
                    channel)

    except Exception as e:
        print ('Exception: {0}'.format(str(e)))

    channel.basic_ack(delivery.delivery_tag)

def send_provider_requests(users, notificationId, providers, channel):
    for u in users:
        msg = json.dumps(to_provider_request(u, notificationId))
        if ("SMS" in providers):
            print ("sending sms request")
            enqueue_message(channel, os.environ["SMS_QUEUE"], \
                msg, "application/json")
        if ("Email" in providers):
            enqueue_message(channel, os.environ["EMAIL_QUEUE"], \
                msg, "application/json")
        if ("Mobile" in providers):
            enqueue_message(channel, os.environ["MOBILE_QUEUE"], \
                msg, "application/json")  

def send_sms(db, channel, method, header, body):
    print ('sms sent')
    channel.basic_ack(method.delivery_tag)

def send_email(db, channel, method, header, body):
    print ('email sent')
    channel.basic_ack(method.delivery_tag)

def push_mobile_notification(db, channel, method, header, body):
    print ('mobile notification pushed')
    channel.basic_ack(method.delivery_tag)

def to_provider_request(user, notificationId):
    return {"notificationId":notificationId, \
        "userId":str(user["_id"]), \
            "email":user["email"],\
                "firstName": user["firstName"], \
                    "lastName": user["lastName"], \
                        "language": user["language"]}

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
        .find_one({'_id':ObjectId(id)})

def on_conn_open(db, connection):
    print ('connection opened')
    connection.channel(on_open_callback=\
        partial(on_channel_open, db))

def on_channel_open(db, channel):
    print ('channel opened')
    channel.queue_declare(queue=os.environ['NOTIFICATION_QUEUE'], \
        callback=partial(on_queue_declared, \
            db, channel, os.environ['NOTIFICATION_QUEUE'], \
                process_message), durable=True)
    channel.queue_declare(queue=os.environ['SMS_QUEUE'], \
        callback=partial(on_queue_declared, \
            db, channel, os.environ['SMS_QUEUE'], \
                send_sms), durable=True)
    channel.queue_declare(queue=os.environ['EMAIL_QUEUE'], \
        callback=partial(on_queue_declared, \
            db, channel, os.environ['EMAIL_QUEUE'], \
                send_email), durable=True)
    channel.queue_declare(queue=os.environ['MOBILE_QUEUE'], \
        callback=partial(on_queue_declared, \
            db, channel, os.environ['MOBILE_QUEUE'], \
                push_mobile_notification), durable=True)

def on_queue_declared(db, channel, queue_name, method, frame):
    print ('{0} declared'.format(queue_name))
    # for fair dispatch
    # channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=queue_name,\
         on_message_callback=partial(method,\
             db))

def enqueue_message(channel, routing_key, msg, content_type):
    channel.queue_declare(queue=routing_key, durable=True)
    channel.basic_publish(exchange='',\
        routing_key=routing_key,\
            body=msg,
            properties=pika.BasicProperties(\
                delivery_mode=2, \
                    content_type= content_type))

def main():
    client = pymongo.MongoClient("mongodb://mongo:27017")
    db = client[os.environ["MONGO_DB_NAME"]]

    parameters = pika.URLParameters(os.environ['RABBITMQ_AMQP_URL'])
    connection = pika.SelectConnection(parameters, \
            on_open_callback=partial(on_conn_open, db))
    connection.ioloop.start()

if __name__ == '__main__':
    main()