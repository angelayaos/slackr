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

BASE_URL = f"http://127.0.0.1:{port}"




def test_create_private():

    requests.post(f"{BASE_URL}/auth/register", json={
        'email' : 'test@test.com',
        'password' : 'test_password',
        'name_first': 'John',
        'name_last': 'Smith'
    })

    requests.post(f"{BASE_URL}/workspace/reset")

    requests.post(f"{BASE_URL}/auth/register", json={
        'email' : 'test@test.com',
        'password' : 'test_password',
        'name_first': 'John',
        'name_last': 'Smith'
    })

    
    ret = requests.post(f"{BASE_URL}/channels/create", json={
        'token' : 'test@test.com',
        'name': 'new_channel',
        'is_public' : False,
    })
    payload = ret.json()

    channel_id = payload['channel_id']
    
    assert channel_id == 1

def test_create_public():
    
    requests.post(f"{BASE_URL}/auth/register", json={
        'email' : 'test1@test.com',
        'password' : 'test_password',
        'name_first': 'John',
        'name_last': 'Smith'
    })


    ret = requests.post(f"{BASE_URL}/channels/create", json={
        'token' : 'test1@test.com',
        'name': 'new_channel_1',
        'is_public' : True,
    })
    payload = ret.json()

    channel_id = payload['channel_id']
    
    assert channel_id == 2  

def test_create_invlaid_name():  
    with pytest.raises(requests.exceptions.HTTPError):  
        ret = requests.post(f"{BASE_URL}/channels/create", json={
            'token' : 'test1@test.com',
            'name': 'a' * 21,
            'is_public' : True,
        }).raise_for_status()

def test_create_invalid_token():  
    with pytest.raises(requests.exceptions.HTTPError):  
        ret = requests.post(f"{BASE_URL}/channels/create", json={
            'token' : 'invlaid_token',
            'name': 'new_channel',
            'is_public' : True,
        }).raise_for_status()
        
def test_create_invalid_is_public():
    with pytest.raises(requests.exceptions.HTTPError):  
        ret = requests.post(f"{BASE_URL}/channels/create", json={
            'token' : 'test1@test.com',
            'name': 'new_channel',
            'is_public' : 'True False',
        }).raise_for_status()
        
def test_create_empty_input():
    with pytest.raises(requests.exceptions.HTTPError):  
        ret = requests.post(f"{BASE_URL}/channels/create", json={
            'token' : '' ,
            'name': '',
            'is_public': '', 
        }).raise_for_status()         


######################## LIST ############################################### 
def test_list():
    
    queryString = urllib.parse.urlencode({
        'token' : 'test@test.com'
    })
    r = requests.get(f"{BASE_URL}/channels/list?{queryString}")
    payload = r.json()
    
    assert payload =={'channels': [{'channel_id': 1, 'name': 'new_channel'}]}


def test_list_invalid_token():
    with pytest.raises(requests.exceptions.HTTPError):  
        queryString = urllib.parse.urlencode({
            'token' : 'invlaid_token'
        })
        requests.get(f"{BASE_URL}/channels/list?{queryString}").raise_for_status()             
  
def test_list_multiple_public_channel():  
    channel_reset()
    
    requests.post(f"{BASE_URL}/auth/register", json={
        'email' : 'test00@test.com',
        'password' : 'test_password',
        'name_first': 'John',
        'name_last': 'Smith'
    })
    
    requests.post(f"{BASE_URL}/auth/register", json={
        'email' : 'test01@test.com',
        'password' : 'test_password',
        'name_first': 'John',
        'name_last': 'Smith'
    })

    ret = requests.post(f"{BASE_URL}/channels/create", json={
        'token' : 'test00@test.com',
        'name': 'new_channel_00',
        'is_public' : False,
    })
    payload = ret.json()
    channel_id_00 = payload['channel_id']


    ret = requests.post(f"{BASE_URL}/channels/create", json={
        'token' : 'test01@test.com',
        'name': 'new_channel_01',
        'is_public' : False,
    })
    payload = ret.json()
    channel_id_01 = payload['channel_id']
   
    queryString = urllib.parse.urlencode({
        'token' : 'test00@test.com'
    })
    r = requests.get(f"{BASE_URL}/channels/list?{queryString}")
    payload_00 = r.json()
    
    queryString = urllib.parse.urlencode({
        'token' : 'test01@test.com'
    })
    r = requests.get(f"{BASE_URL}/channels/list?{queryString}")
    payload_01 = r.json()
    
    
    assert payload_00 == {'channels': [{'channel_id': 3, 'name': 'new_channel_00'}]}
    assert payload_01 == {'channels': [{'channel_id': 4, 'name': 'new_channel_01'}]}
   
    
   
   
   
######################## LISTALL #############################################  
            
def test_listall():

    queryString = urllib.parse.urlencode({
        'token' : 'test@test.com'
    })
    r = requests.get(f"{BASE_URL}/channels/listall?{queryString}")
    payload = r.json()
    
    assert payload == {'channels': [{'channel_id': 2, 'name': 'new_channel_1'}]}
    

def test_invalid_list_all():
    with pytest.raises(requests.exceptions.HTTPError):  
        queryString = urllib.parse.urlencode({
            'token' : 'invlaid_token'
        })
        requests.get(f"{BASE_URL}/channels/listall?{queryString}").raise_for_status()        
    
def test_reset():
    requests.post(f"{BASE_URL}/workspace/reset")
