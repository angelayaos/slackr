from datetime import datetime as dt, timedelta
import json
import requests
import urllib 
import pytest
import flask
from error import InputError, AccessError
from server import port

BASE_URL = f'http://127.0.0.1:{port}'

# set up 
register1 = requests.post(f"{BASE_URL}/auth/register", json={
    'email' : 'test@test.com',
    'password' : 'test_password',
    'name_first': 'John',
    'name_last': 'Smith'
})

register2 = requests.post(f"{BASE_URL}/auth/register", json={
    'email' : 'test1@test.com',
    'password' : 'test_password1',
    'name_first': 'Jane',
    'name_last': 'Doe'
})

register3 = requests.post(f"{BASE_URL}/auth/register", json={
    'email' : 'test2@test.com',
    'password' : 'test_password2',
    'name_first': 'First',
    'name_last': 'Last'
})

r_payload1 = register1.json()
r_payload2 = register2.json()
r_payload3 = register3.json()

create = requests.post(f"{BASE_URL}/channels/create", json={
    'token' : r_payload1['token'],
    'name' : 'My channel',
    'is_public': True,
})

c_payload = create.json()

join = requests.post(f"{BASE_URL}/channel/join", json={
        'token': r_payload2['token'],
        'channe_id': c_payload1['channel_id']
})
    
j_payload = join.json()

######### message_send ###########     
def test_message_send_valid():   
    r = requests.post(f"{BASE_URL}/message/send", json={
        'token': r_payload1['token'],
        'channel_id': c_payload1['channel_id'],
        'message': "first message"
    })
    payload = r.json()
    
    r2 = requests.post(f"{BASE_URL}/message/send", json={
        'token': r_payload2['token'],
        'channel_id': c_payload1['channel_id'],
        'message': "second message"
    })
    payload1 = r2.json()

    assert payload['messages'][0]['message'] == "first message"
    assert payload1['messages'][0]['message'] == "second message"
    
def test_message_too_long(): 
    with pytest.raises(requests.exceptions.HTTPError):
        r = requests.post(f"{BASE_URL}/message/send", json={
            'token': r_payload1['token'],
            'channel_id': c_payload1['channel_id'],
            'message': "first message" * 500
    }).raise_for_status()

def test_unauthorised_user():
    with pytest.raises(requests.exceptions.HTTPError):
        r = requests.post(f"{BASE_URL}/message/send", json={
        'token': r_payload2['token'],
        'channel_id': c_payload1['channel_id'],
        'message': "first message"
    }).raise_for_status()
    
######### message_sendlater ########### 
def test_message_sendlater_valid():
    r = requests.post(f"{BASE_URL}/message/sendlater", json={
        'token': r_payload1['token'],
        'channel_id': c_payload1['channel_id'],
        'message': "first messsage",
        'time_sent': dt.utcnow() + timedelta(minutes=10)
    })
    payload = r.json()
    
    assert payload['messages'][0]['message'] == "first message"
    assert payload['messages'][0]['time_created'] == dt.utcnow() + timedelta(minutes=10)
    
def test_message_sendlater_invalid_channel():  
    with pytest.raises(requests.exceptions.HTTPError):
        r = requests.post(f"{BASE_URL}/message/sendlater", json={
        'token': r_payload1['token'],
        'channel_id': 'invalid channel',
        'message': "first message",
        'time_sent': dt.utcnow() + timedelta(minutes=10)
    }).raise_for_status()  
    
def test_message_sendlater_too_long():  
    with pytest.raises(requests.exceptions.HTTPError):
        r = requests.post(f"{BASE_URL}/message/sendlater", json={
        'token' : r_payload1['token'],
        'channel_id' : c_payload1['channel_id'],
        'message' : "first message" * 500,
        'time_sent': dt.utcnow() + timedelta(minutes=10)
    }).raise_for_status()

def test_message_sendlater_invalid_time():    
    with pytest.raises(requests.exceptions.HTTPError):
        r = requests.post(f"{BASE_URL}/message/sendlater", json={
        'token': r_payload1['token'],
        'channel_id': c_payload1['channel_id'],
        'message': "first message",
        'time_sent': 'invalid time'
    }).raise_for_status()

def test_message_sendlater_unauthorised_user():    
    with pytest.raises(requests.exceptions.HTTPError):
        r = requests.post(f"{BASE_URL}/message/sendlater", json={
        'token' : r_payload3['token'],
        'channel_id' : c_payload1['channel_id'],
        'message' : "first message",
        'time_sent': dt.utcnow() + timedelta(minutes=10)
    }).raise_for_status()

######### message_react ###########     
    r = requests.post(f"{BASE_URL}/message/send", json={
        'token': r_payload1['token'],
        'channel_id': c_payload1['channel_id'],
        'message': "first message"
    })
    payload = r.json()
    
    r1 = requests.post(f"{BASE_URL}/message/react", json={
        'token': r_payload1['token'],
        'message_id': payload['message_id'],
        'react_id': 1
    })
    payload1 = r1.json()
    
    assert len(payload1['messages'][0]['reacts'][0]['u_ids']) == 1
    
def test_message_react_invalid_message():  
    with pytest.raises(requests.exceptions.HTTPError):
        r = requests.post(f"{BASE_URL}/message/react", json={
        'token' : r_payload1['token'],
        'message_id' : 'invalid message_id',
        'react_id': 1
    }).raise_for_status()
    
def test_message_invalid_react_id():   
    r = requests.post(f"{BASE_URL}/message/send", json={
        'token': r_payload1['token'],
        'channel_id': c_payload1['channel_id'],
        'message': "first message"
    })
    payload = send.json()
    
    with pytest.raises(requests.exceptions.HTTPError):
        r = requests.post(f"{BASE_URL}/message/react", json={
        'token' : r_payload1['token'],
        'message_id' : payload['message_id'],
        'react_id': 'invalid react id'
    }).raise_for_status()   

def test_message_already_reacted():  
    ret = requests.post(f"{BASE_URL}/message/send", json={
        'token': r_payload1['token'],
        'channel_id': c_payload1['channel_id'],
        'message': "first message"
    })
    payload = ret.json()
    
    r1 = requests.post(f"{BASE_URL}/message/react", json={
        'token': r_payload1['token'],
        'message_id': payload['message_id'],
        'react_id': 1  
    })  
    payload1 = r1.json()
        
    with pytest.raises(requests.exceptions.HTTPError):
        r = requests.post(f"{BASE_URL}/message/react", json={
        'token' : r_payload1['token'],
        'message_id' : payload['message_id'],
        'react_id': 1
    }).raise_for_status() 
    
######### message_unreact ###########         
def test_message_unreact_valid():  
    ret = requests.post(f"{BASE_URL}/message/send", json={
        'token': r_payload1['token'],
        'channel_id': c_payload1['channel_id'],
        'message': "first message"
    })
    payload = ret.json()
    
    r1 = requests.post(f"{BASE_URL}/message/react", json={
        'token': r_payload1['token'],
        'message_id': s_payload['message_id'],
        'react_id': 1
    })
    payload1 = r1.json()
    
    assert len(payload1['messages'][0]['reacts'][0]['u_ids']) == 1
    
    r = requests.post(f"{BASE_URL}/message/unreact", json={
        'token': r_payload1['token'],
        'message_id': payload['message_id'],
        'react_id': 1
    })
    payload2 = r.json()
    
    assert len(payload2['messages'][0]['reacts'][0]['u_ids']) == 0
    
def test_message_unreact_invalid_message():   
    with pytest.raises(requests.exceptions.HTTPError):
        r = requests.post(f"{BASE_URL}/message/unreact", json={
        'token': r_payload1['token'],
        'message_id': 'invalid message_id',
        'react_id': 1
    }).raise_for_status()
    
def test_message_unreact_invalid_react_id():  
    ret = requests.post(f"{BASE_URL}/message/send", json={
        'token': r_payload1['token'],
        'channel_id': c_payload1['channel_id'],
        'message': "first message"
    })
    payload = ret.json()
    
    r1 = requests.post(f"{BASE_URL}/message/react", json={
        'token': r_payload1['token'],
        'message_id': payload['message_id'],
        'react_id': 1
    })
    payload1 = r1.json()
    
    with pytest.raises(requests.exceptions.HTTPError):
        r = requests.post(f"{BASE_URL}/message/unreact", json={
        'token': r_payload1['token'],
        'message_id': payload1['message_id'],
        'react_id': 'invalid react id'
    }).raise_for_status() 
    
def test_message_no_react_id(): 
    ret = requests.post(f"{BASE_URL}/message/send", json={
        'token': r_payload1['token'],
        'channel_id': c_payload1['channel_id'],
        'message': "first message"
    })
    payload = ret.json()
    
    with pytest.raises(requests.exceptions.HTTPError):
        r = requests.post(f"{BASE_URL}/message/unreact", json={
        'token' : r_payload1['token'],
        'message_id': payload['message_id'],
        'react_id': 1
    }).raise_for_status() 
    
######### message_pin ###########  
def test_message_pin_valid():  
    ret = requests.post(f"{BASE_URL}/message/send", json={
        'token': r_payload1['token'],
        'channel_id': c_payload1['channel_id'],
        'message': "first message"
    })
    payload = ret.json()
    
    r = requests.post(f"{BASE_URL}/message/pin", json={
        'token': r_payload1['token'],
        'message_id': payload['message_id']
    })
    payload1 = r.json()
    
    assert payload1['messages'][0]['is_pinned'] == True
    
def test_message_pin_invalid_message():   
    with pytest.raises(requests.exceptions.HTTPError):
        r = requests.post(f"{BASE_URL}/message/pin", json={
        'token': r_payload1['token'],
        'message_id': 'invalid message'
    }).raise_for_status() 

def test_message_already_pinned():     
    ret = requests.post(f"{BASE_URL}/message/send", json={
        'token': r_payload1['token'],
        'channel_id': c_payload1['channel_id'],
        'message': "first message"
    })
    payload = ret.json()
    
    r1 = requests.post(f"{BASE_URL}/message/pin", json={
        'token': r_payload1['token'],
        'message_id': payload['message_id']
    })
    payload1 = r1.json()
    
    with pytest.raises(requests.exceptions.HTTPError):
        r = requests.post(f"{BASE_URL}/message/pin", json={
        'token': r_payload1['token'],
        'message_id': payload1['message_id']
    }).raise_for_status() 
    
def test_message_pin_not_owner():    
    ret = requests.post(f"{BASE_URL}/message/send", json={
        'token': r_payload1['token'],
        'channel_id': c_payload1['channel_id'],
        'message': "first message"
    })
    payload = ret.json()

    with pytest.raises(requests.exceptions.HTTPError):
        r = requests.post(f"{BASE_URL}/message/pin", json={
        'token': r_payload2['token'],
        'message_id': payload['message_id']
    }).raise_for_status()
    
def test_message_pin_not_member():    
    ret = requests.post(f"{BASE_URL}/message/send", json={
        'token': r_payload1['token'],
        'channel_id': c_payload1['channel_id'],
        'message': "first message"
    })
    payload = ret.json()
    
    with pytest.raises(requests.exceptions.HTTPError):
        r = requests.post(f"{BASE_URL}/message/pin", json={
        'token': r_payload3['token'],
        'message_id': payload['message_id']
    }).raise_for_status()
    
######### message_unpin ###########           
def test_message_unpin_valid(): 
    r = requests.post(f"{BASE_URL}/message/send", json={
        'token': r_payload1['token'],
        'channel_id': c_payload1['channel_id'],
        'message': "first message"
    })
    payload = r.json()
    
    r1 = requests.post(f"{BASE_URL}/message/pin", json={
        'token': r_payload1['token'],
        'message_id': s_payload['message_id']
    })
    payload1 = r1.json()
    
    r2 = requests.post(f"{BASE_URL}/message/unpin", json={
        'token': r_payload1['token'],
        'message_id': s_payload['message_id']
    })
    payload2 = r2.json()
    
    assert payload2['messages'][0]['is_pinned'] == False
    
def test_message_unpin_invalid_message():      
    with pytest.raises(requests.exceptions.HTTPError):
        r = requests.post(f"{BASE_URL}/message/unpin", json={
        'token': r_payload1['token'],
        'message_id': 'invalid message'
    }).raise_for_status()

def test_message_already_unpinned():  
    ret = requests.post(f"{BASE_URL}/message/send", json={
        'token': r_payload1['token'],
        'channel_id': c_payload1['channel_id'],
        'message': "first message"
    })
    payload = ret.json()
    
    r1 = requests.post(f"{BASE_URL}/message/pin", json={
        'token': r_payload1['token'],
        'message_id': s_payload['message_id']
    })
    payload1 = r1.json()
    
    r2 = requests.post(f"{BASE_URL}/message/unpin", json={
        'token': r_payload1['token'],
        'message_id': s_payload['message_id']
    })
    payload2 = r2.json()
    
    with pytest.raises(requests.exceptions.HTTPError):
        r = requests.post(f"{BASE_URL}/message/unpin", json={
        'token': r_payload1['token'],
        'message_id': payload2['message_id']
    }).raise_for_status()

def test_message_unpin_not_owner():
    ret = requests.post(f"{BASE_URL}/message/send", json={
        'token': r_payload1['token'],
        'channel_id': c_payload1['channel_id'],
        'message': "first message"
    })
    payload = ret.json()
    
    r1 = requests.post(f"{BASE_URL}/message/pin", json={
        'token': 'test@test.com',
        'message_id': s_payload['message_id']
    })
    payload1 = r1.json()

    with pytest.raises(requests.exceptions.HTTPError):
        r = requests.post(f"{BASE_URL}/message/unpin", json={
        'token': r_payload2['token'],
        'message_id': payload1['message_id']
    }).raise_for_status()

def test_message_unpin_not_member():   
    ret = requests.post(f"{BASE_URL}/message/send", json={
        'token': r_payload1['token'],
        'channel_id': c_payload1['channel_id'],
        'message': "first message"
    })
    payload = ret.json()
    
    with pytest.raises(requests.exceptions.HTTPError):
        r = requests.post(f"{BASE_URL}/message/unpin", json={
        'token': r_payload3['token'],
        'message_id': payload['message_id']
    }).raise_for_status()

######### message_remove ###########     
def test_message_remove_valid():
    ret = requests.post(f"{BASE_URL}/message/send", json={
        'token': r_payload2['token'],
        'channel_id': c_payload1['channel_id'],
        'message': "first message"
    })
    payload = ret.json()
    
    r = requests.post(f"{BASE_URL}/message/remove", json={
        'token': r_payload2['token'],
        'message_id': payload['message_id']
    })
    payload1 = r.json()

    assert len(payload1['messages']) == 0
    
def test_message_remove_valid_owner():    
    ret = requests.post(f"{BASE_URL}/message/send", json={
        'token': r_payload2['token'],
        'channel_id': c_payload1['channel_id'],
        'message': "first message"
    })
    payload = ret.json()

    r = requests.post(f"{BASE_URL}/message/remove", json={
        'token': r_payload1['token'],
        'message_id': payload['message_id']
    })
    payload1 = r.json()
    
    assert len(payload1['messages']) == 0
    
def test_message_remove_invalid_message():
    with pytest.raises(requests.exceptions.HTTPError):
        r = requests.post(f"{BASE_URL}/message/remove", json={
        'token': r_payload1['token'],
        'message_id': 'invalid message'
    }).raise_for_status()

######### message_edit ###########  
def test_message_edit_valid():
    ret = requests.post(f"{BASE_URL}/message/send", json={
        'token': r_payload2['token'],
        'channel_id': c_payload1['channel_id'],
        'message': "first message"
    })
    payload = ret.json()
    
    r = requests.post(f"{BASE_URL}/message/edit", json={
        'token': r_payload2['token'],
        'message_id': payload['message_id'],
        'message': "new first message"
    })
    payload1 = r.json()
    
    assert payload1['messages'][0]['message'] == "new first message"
    
    r1 = requests.post(f"{BASE_URL}/message/edit", json={
        'token': r_payload3['token'],
        'message_id': payload1['message_id'],
        'message': "newer first message"
    })
    payload2 = r1.json()
    
    assert payload2['messages'][0]['message'] == "newer first message"
    
def test_message_edit_invalid():
    ret = requests.post(f"{BASE_URL}/message/send", json={
        'token': r_payload1['token'],
        'channel_id': c_payload1['channel_id'],
        'message': "first message"
    })
    payload = ret.json()
    
    with pytest.raises(requests.exceptions.HTTPError):
        r = requests.post(f"{BASE_URL}/message/edit", json={
        'token': r_payload2['token'],
        'message_id': payload['message_id'],
        'message': "new first messsage"
    }).raise_for_status()

def test_reset():
    requests.post(f"{BASE_URL}/workspace/reset")