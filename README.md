# Notification

## Requirement
Docker is required to run this codebase. Visit https://www.docker.com/ to download and install it.

## Installation:
Clone this repo and in command-prompt or terminal run:

`docker-compose up`

## APIs

### User Creation

**Endpoint:** /user
**Request Type:** POST
**Content-Type:** application/json

Field | Type | Description | Required
----- | ---- | ------------| --------
email | string | Unique email of the user | Y
firstName | string | First name of the user | Y
lastName | string | Last name of the user | N
language | string | Preffered language ISO 639-1 code | Y

Additional optional fields such as `location` can also be sent.

**Sample json:**
```json
{
    "email": "sample@notification.com",
    "firstName": "Fahad",
    "lastName": "Ejaz",
    "location": "Pakistan",
    "language": "ur"
}
```

**Errors**
Status Code | Message | Meaning
----------- | ------- | -------
500 | email is required | "email" has not been sent in the post request body
500 | firstName is required | "firstName" has not been sent in the post request body
500 | language is required | "language" has not been sent in the post request body


