import json
import requests
import urllib 
import pytest
import flask
from channels_server import channel_reset
from auth import auth_register
from error import InputError
from storage import data
from server import port

BASE_URL = 'http://127.0.0.1:{port}'


def test_admin():

    requests.post(f"{BASE_URL}/auth/register", json={
        'email' : 'user_1@test.com',
        'password' : 'test_password',
        'name_first': 'user_1',
        'name_last': 'user_1'
    })
    
    
    r = requests.post(f"{BASE_URL}/auth/register", json={
        'email' : 'user__new_owner@test.com',
        'password' : 'test_password',
        'name_first': 'user_2',
        'name_last': 'user_2'
    })
    payload = r.json()
    u_id = payload['u_id']
    
    r = requests.post(f"{BASE_URL}/auth/register", json={
        'email' : 'user_0@test.com',
        'password' : 'test_password',
        'name_first': 'user_0',
        'name_last': 'user_0'
    })
    payload = r.json()
    u_id_1 = payload['u_id']
    
    requests.post(f"{BASE_URL}/admin/userpermission/change", json={
        'token': 'user_1@test.com',
        'u_id': u_id,
        'permission_id': 1,
    })
    
    requests.post(f"{BASE_URL}/admin/userpermission/change", json={
        'token': 'user_new_owner@test.com',
        'u_id': u_id_1,
        'permission_id': 1,
    })
    
    

def test_invalid_permission_id():
    r = requests.post(f"{BASE_URL}/auth/register", json={
        'email' : 'user_3@test.com',
        'password' : 'test_password',
        'name_first': 'user_3',
        'name_last': 'user_3'
    })
    payload = r.json()
    u_id = payload['u_id']
    
    with pytest.raises(requests.exceptions.HTTPError):  
        requests.post(f"{BASE_URL}/admin/userpermission/change", json={
            'token': 'user_1@test.com',
            'u_id': u_id,
            'permission_id': 3 ,
        }).raise_for_status()  

def test_invalid_u_id():

    with pytest.raises(requests.exceptions.HTTPError):  
            requests.post(f"{BASE_URL}/admin/userpermission/change", json={
                'token': 'user_1@test.com',
                'u_id': 'invlaid_u_id',
                'permission_id': 1 ,
            }).raise_for_status()   

def test_not_owner():

    with pytest.raises(requests.exceptions.HTTPError):  
        requests.post(f"{BASE_URL}/admin/userpermission/change", json={
            'token': 'user_3@test.com',
            'u_id': 'valid_u_id',
            'permission_id': 1 ,
        }).raise_for_status()       
    
def test_reset():
    requests.post(f"{BASE_URL}/workspace/reset")

    



