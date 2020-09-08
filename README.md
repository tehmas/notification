# Notification

## Requirement
Docker is required to run this codebase. Visit https://www.docker.com/ to download and install it.

## Installation
Clone this repo and in command-prompt or terminal run:

`docker-compose up`

## Testing
`Python 3.8` and `Pytest 6.0.1` is required for testing the `api`. After running the codebase using `docker-compose up`, open up a separate command-prompt or terminal with working directory set to the `test` folder, type and run:
`pytest -v'. 

## APIs

### User Creation

**Endpoint:** /user\
**Request Type:** POST\
**Content-Type:** application/json

Field | Type | Description | Required
----- | ---- | ------------| --------
email | string | Unique email of the user | Y
firstName | string | First name of the user | Y
lastName | string | Last name of the user | N
language | string | Preffered language ISO 639-1 code | Y

Additional optional fields such as `location` can also be sent.

**Sample request:**
```json
{
    "email": "sample@notification.com",
    "firstName": "Fahad",
    "lastName": "Ejaz",
    "location": "Pakistan",
    "language": "ur"
}
```

**Sample response:**
```json
{
    "Data": {
        "id": "5f572071242533f07f204185"
    }
}
```

**Errors:**
Status Code | Message | Meaning
----------- | ------- | -------
500 | email is required | "email" has not been sent in the post request body
500 | firstName is required | "firstName" has not been sent in the post request body
500 | language is required | "language" has not been sent in the post request body
500 | Record already exists | A user with the same "email" already exists

### User Retrieval
**Endpoint:** /user\
**Query Parameter:** id - This is the id of the user\
**Request Type:** GET\
**Sample URL:** `/user?id=5f572071242533f07f204185`

**Sample Response:**
```json
{
    "email": "sample@notification.com",
    "firstName": "Fahad",
    "lastName": "Ejaz",
    "location": "Pakistan",
    "language": "ur",
    "id": "5f57251dfc3f9169cea2e678"
}
```

### User Deletion
**Query Parameter:** id - This is the id of the user\
**Request Type:** DELETE\
**Sample URL:** `/user?id=5f572071242533f07f204185`

**Response:**
```json
{
    "Message": "Sucesss"
}
```

### Send Notification

**Endpoint:** /notification\
**Request Type:** POST\
**Content-Type:** application/json

Field | Type | Description | Required
----- | ---- | ------------| --------
title | string | Title of the notification | Y
message | string | Actual message of the notification | Y
providers | array | Types of notifications to be sent. Possible values are "SMS", "Email", "Mobile". Sending at least one of the possible values is required | Y
groupFlag | string | Possible values are "Y" and "N". "Y" indicates the receivers are group. "N" indicates specific users as receivers. | Y
receivers | array | If groupFlag is "N", contains the ids of the users. Whereas if groupFlag is "Y", contains the names of groups e.g "location:Pakistan" indicates a group of users who have their location set to "Pakistan". | Y
language | string | Indicates the original language of the notification and value is according to the ISO 639-1 standard. | Y

**Sample Request**:
```json
{
    "title": "test 1",
    "message": "Hope you are enjoying the app",
    "providers": ["SMS", "Email", "Mobile"],
    "groupFlag": "Y",
    "receivers": ["location:Pakistan"],
    "language": "en-us"
}
```
## Process

- **Send Notification** api is hit, the notification schema is validated and saved in database. 
- The generated id of the notification is enqueued to a `notification_queue` **rabbitmq** queue and a success response is sent to the API consumer.
- **notifier** is running and listening over the `notification_queue` in another process. Upon receiving a message (notification id), it first retrieves the complete notification from the database. It checks the `groupFlag` and retrieves data of the users accordingly. It prepares notification message for each user on the basis of the providers (Email, SMS, Mobile) and enqueus them to `email_queue`, `sms_queue` and `mobile_queue` accordingly. On each queue, a consumer is listening. Currently, only a message is printed by the email, sms and mobile notification senders to indicate that the notification has been sent after assuming that it has been translated to the preffered language. Fair prefetching has be adopted for each queue to result in optimized consumption if multiple worker processes are running.

## Space for Improvement
- A redis cache layer would prove to be efficient. Currently to avoid passing the actual notification message in the queue, we have to retrieve it again and again from database. After immplementing a redis cache layer, we could simply access the notification from there. Similarly, we can temporarily store translated messages in redis to avoid translating message again if a message has been translated once. **Due to time constraint this has not been implemented but I also intended to use this for storing a common count or flag to know if the per minute limit of the provider has been reached and schedule the pending notifications for later accordingly.**
- Originally, I intended to have separate worker process for listening to `email_queue`, `sms_queue` and `mobile_queue`. This does seem an overkill for the current scope but it should be preferred.
- It should also be logged if a notification has been successfull sent. Moreover, this result should also be aggregated.
- A common module is needed to share common functionality such as for enqueueing message in a **rabbitmq**.

## Technology Selection
- **Mongo DB**: Relational databases are simpler but not expected to be used for such an open-ended scale. A NoSQL database seemed to be perfect for such a large scale.
- **RabbitMQ**: I did not want the API caller/consumer to wait until the notification has actually been sent. Running the actual notification sending code in a separate process made more sense for which I needed a message broker.

## Avoidance of Exclusive PaaS
Original intention was to use **Azure Functions** on *Consumption Plan* along with **Azure Service Bus** and **Azure Table Storage** to provide better scalability. However, the requirement that the application should be able to run using `docker-compose up` indicated that the application should be able to run on any platform. This is true that **Azure Functions** can be containerized but **Azure Service Bus** and **Azure Table Storage** are **Azure** exclusive so it would not be possible to directly run such an app on a different platform such as **AWS**. Morever, the real advantage of using serverless solutions such as Azure Functions or AWS Lambda seem to be consumption plan.