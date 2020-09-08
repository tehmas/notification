import pytest
import requests
import random
import string

url = 'http://localhost:5002'

def test_root():
    r = requests.get(url +'/')
    assert r.status_code == 404

def test_user_creation():
    payload = {"email":"sample@test.com", \
        "firstName":"First Name", \
            "lastName": "LastName", \
                "language": "en-us"}
    r = requests.post(url +'/user',\
        json=payload)
    
    assert r.status_code == 200

def test_user_retrieval():
    id = "5f5655f2e7c3c287ac3d45f2"
    r = requests.get(url + '/user?id=' + id)

    assert r.status_code == 200

def test_user_deletion():
    id = "5f5655f2e7c3c287ac3d45f2"
    r = requests.delete(url + '/user?id=' + id)

    assert r.status_code == 200

def test_notification_creation():
    payload = { "title": "test 1",\
        "message": "Hope you are enjoying the app", \
            "providers": ["SMS", "Email", "Mobile"], \
                "groupFlag": "Y", \
                    "receivers": ["location:Pakistan"], \
                        "language": "en-us"}
    r = requests.post(url +'/notification',\
        json=payload)
    
    assert r.status_code == 200
    
