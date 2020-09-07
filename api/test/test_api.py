import pytest
import requests
import random
import string

url = 'http://localhost:5002'

def test_root():
    r = requests.get(url +'/')
    assert r.status_code == 404

def test_user_creation():
    payload = {"email":"test@email.com", \
        "firstName":"First Name", \
            "lastName": "LastName", \
                "language": "en-us"}
    post_response = requests.post(url +'/user',\
        json=payload)
    
    if (post_response.status_code != 200):
        assert False
    
    id = post_response.json()["Data"]["id"]

    get_response = requests.get(url + '/user?id='+id)

    if (get_response.status_code != 200):
        assert False
    
    delete_response = requests.delete(url + '/user?id='+id)

    assert delete_response.status_code == 200


    
