from datetime import datetime as dt, timedelta
import pytest 
from error import InputError, AccessError
from message import *
from channels import channels_create, channel_reset
from channel import channel_join
from user import user_profile
from auth import auth_register, auth_reset
from storage import data
    
def get_user():
    data1 = auth_register('comp1531student@unsw.edu.au', 'testPassword', 'John', 'Smith')
    return(data1['u_id'], data1['token'])
    
def get_user_extra():
    data2 = auth_register('validemail@gmail.com', 'validPassword', 'First', 'Last')
    return(data2['u_id'], data2['token'])
    
######### message_send ###########    
def test_message_send_valid():
    u_id, token = get_user()
    u_id1, token1 = get_user_extra()
    
    channels_create(token, 'channel 1', True)
    channel_join(token1, 1)
    message_send(token, 1, "first message")
    message_send(token1, 1, "second message")
    
    assert data['messages'][0]['message'] == "first message"
    assert data['messages'][1]['message'] == "second message"

def test_message_too_long():   
    auth_reset()
    messages_reset()
    channel_reset()
    u_id, token = get_user()
    
    channels_create(token, 'channel 1', True)

    with pytest.raises(InputError):
        message_send(token, 1, "first message" * 500)

def test_unauthorised_user():
    auth_reset()
    channel_reset()
    messages_reset()
    u_id, token = get_user()
    token1 = get_user_extra() 
    
    channels_create(token, 'channel 1', True)

    with pytest.raises(AccessError):
        message_send(token1, 1, "first message")

######### message_sendlater ########### 
def test_message_sendlater_valid():
    auth_reset()
    channel_reset()
    messages_reset()
    u_id, token = get_user()
    
    channels_create(token, 'channel 1', True)
    time_sent_after = dt.utcnow() + timedelta(minutes=15)
    message_sendlater(token, 1, "first message", time_sent_after)
    
    assert data['messages'][0]['message'] == "first message"
    assert data['messages'][0]['time_created'] == time_sent_after

def test_message_sendlater_invalid_channel():  
    auth_reset()
    channel_reset()
    messages_reset()
    u_id, token = get_user()
    time_sent_after = dt.utcnow() + timedelta(minutes=15)
    
    with pytest.raises(InputError):
        message_sendlater(token, 2, "second message", time_sent_after)

def test_message_sendlater_too_long(): 
    auth_reset()
    channel_reset()
    messages_reset()
    u_id, token = get_user()
    time_sent_after = dt.utcnow() + timedelta(minutes=15)
    
    channels_create(token, 'channel 1', True)
    message_sendlater(token, 1, "first message", time_sent_after)
    
    with pytest.raises(InputError):
        message_sendlater(token, 1, "second message" * 500, time_sent_after)
        
def test_message_sendlater_invalid_time(): 
    auth_reset()
    channel_reset()
    messages_reset()
    u_id, token = get_user()
    time_sent_before = dt.utcnow() - timedelta(minutes=15)
    
    channels_create(token, 'channel 1', True)
    
    with pytest.raises(InputError):
        message_sendlater(token, 1, "first", time_sent_before)

def test_message_sendlater_unauthorised_user(): 
    auth_reset()
    u_id, token = get_user()
    user = auth_register('userextra@gmail.com','userextrapassword', 'FirstName', 'LastName')
    token1 = user['token']
    time_sent_after = dt.utcnow() + timedelta(minutes=15)
    
    channels_create(token, 'channel 1', True)

    with pytest.raises(AccessError):
        message_sendlater(token1, 1, "first", time_sent_after)
        
######### message_react ########### 
def test_message_react_valid():
    auth_reset()
    channel_reset()
    u_id, token = get_user()
    
    channels_create(token, 'channel 1', True)
    message_send(token, 1, "first message")
    message_react(token, 0, 1)

    assert len(data['messages'][0]['reacts'][0]['u_ids']) == 1

def test_message_react_invalid_message():
    auth_reset()
    channel_reset()
    messages_reset()
    u_id, token = get_user()  
    
    channels_create(token, 'channel 1', True)
    
    with pytest.raises(InputError):
        message_react(token, 0, 1)

def test_message_invalid_react_id():
    auth_reset()
    u_id, token = get_user()   
    channels_create(token, 'channel 1', True)
    message_send(token, 1, "first message")

    with pytest.raises(InputError):
        message_react(token, 1, 0)

def test_message_already_reacted():
    auth_reset()
    u_id, token = get_user()
    
    channels_create(token, 'channel 1', True)
    message_send(token, 1, "first message")
    message_react(token, 0, 1)

    with pytest.raises(InputError):
        message_react(token, 0, 1)
        
######### message_unreact ###########         
def test_message_unreact_valid():
    auth_reset()
    channel_reset()
    messages_reset()
    u_id, token = get_user()
    
    channels_create(token, 'channel 1', True)
    message_send(token, 1, "first message")
    message_react(token, 0, 1)
    
    assert len(data['messages'][0]['reacts'][0]['u_ids']) == 1
    message_unreact(token, 0, 1)
    assert len(data['messages'][0]['reacts'][0]['u_ids']) == 0

def test_message_unreact_invalid_message(): 
    auth_reset()
    channel_reset()
    messages_reset()
    u_id, token = get_user()
    
    channels_create(token, 'channel 1', True)
    
    with pytest.raises(InputError):
        message_unreact(token, 0, 1)

def test_message_unreact_invalid_react_id():  
    auth_reset()
    channel_reset()
    messages_reset()
    u_id, token = get_user()
    
    channels_create(token, 'channel 1', True)
    message_send(token, 1, "first message")
    message_react(token, 0, 1)
    
    with pytest.raises(InputError):
        message_unreact(token, 0, 0)

def test_message_no_react_id(): 
    auth_reset()
    channel_reset()
    messages_reset()
    u_id, token = get_user()
    
    channels_create(token, 'channel 1', True)
    message_send(token, 1, "first")

    with pytest.raises(InputError):
        message_unreact(token, 0, 1)

######### message_pin ###########  
def test_message_pin_valid():
    auth_reset()
    channel_reset()
    messages_reset()
    u_id, token = get_user()
    
    channels_create(token, 'channel 1', True)
    message_send(token, 1, "first message")
    message_pin(token, 0)
    
    assert data['messages'][0]['is_pinned'] == True

def test_message_pin_invalid_message():  
    auth_reset()
    channel_reset()
    messages_reset()
    u_id, token = get_user()
    
    channels_create(token, 'channel 1', True)

    with pytest.raises(InputError):
        message_pin(token, 0)

def test_message_already_pinned():
    auth_reset()  
    channel_reset()
    messages_reset()
    u_id, token = get_user()
    
    channels_create(token, 'channel 1', True)
    message_send(token, 1, "first message")
    message_pin(token, 0)
    
    with pytest.raises(InputError):
        message_pin(token, 0)
    
def test_message_pin_not_owner(): 
    auth_reset()
    channel_reset()
    messages_reset()
    u_id, token = get_user()
    u_id1, token1 = get_user_extra()
    
    channels_create(token, 'channel 1', True)
    channel_join(token1, 1)
    message_send(token, 1, "first message")

    with pytest.raises(InputError):
        message_pin(token1, 0)

def test_message_pin_not_member():
    auth_reset()
    channel_reset()
    messages_reset()
    u_id, token = get_user()
    user = auth_register('userextra@gmail.com','userextrapassword', 'FirstName', 'LastName')
    token1 = user['token']
    
    channels_create(token, 'channel 1', True)
    message_send(token, 1, "first message")

    with pytest.raises(AccessError):
        message_pin(token1, 0)   
        
######### message_unpin ###########           
def test_message_unpin_valid(): 
    auth_reset()
    channel_reset()
    messages_reset()
    u_id, token = get_user()
    
    channels_create(token, 'channel 1', True)
    message_send(token, 1, "first message")
    message_pin(token, 0)
    message_unpin(token, 0)
    
    assert data['messages'][0]['is_pinned'] == False

def test_message_unpin_invalid_message(): 
    auth_reset() 
    channel_reset()
    messages_reset()
    u_id, token = get_user()

    channels_create(token, 'channel 1', True)
    
    with pytest.raises(InputError):
        message_unpin(token, 0)

def test_message_already_unpinned(): 
    auth_reset()
    channel_reset()
    messages_reset()
    u_id, token = get_user()
    
    channels_create(token, 'channel 1', True)
    message_send(token, 1, "first message")
    message_pin(token, 0)
    message_unpin(token, 0)
    
    with pytest.raises(InputError):
        message_unpin(token, 0)

def test_message_unpin_not_owner(): 
    auth_reset()
    channel_reset()
    messages_reset()
    u_id, token = get_user()
    u_id1, token1 = get_user_extra()
    
    channels_create(token, 'channel 1', True)
    channel_join(token1, 1)
    message_send(token, 1, "first message")

    with pytest.raises(InputError):
        message_unpin(token1, 0)

def test_message_unpin_not_member(): 
    auth_reset()
    channel_reset()
    messages_reset()
    u_id, token = get_user()
    user = auth_register('userextra@gmail.com','userextrapassword', 'FirstName', 'LastName')
    token1 = user['token']
    
    channels_create(token, 'channel 1', True)
    message_send(token, 1, "first message")
    
    with pytest.raises(AccessError):
        message_unpin(token1, 0)       

######### message_remove ###########     
def test_message_remove_valid():
    auth_reset()
    channel_reset()
    messages_reset()
    u_id, token = get_user()
    
    channels_create(token, 'channel 1', True)
    message_send(token, 1, "first message")
    message_remove(token, 0)

    assert len(data['messages']) == 0
    
def test_message_remove_valid_owner():
    auth_reset()
    channel_reset()
    messages_reset()
    u_id, token = get_user()
    u_id1, token1 = get_user_extra()
    
    channels_create(token, 'channel 1', True)
    channel_join(token1, 1)
    message_send(token1, 1, "first message")
    message_remove(token, 0)

    assert len(data['messages']) == 0

def test_message_remove_invalid_message():
    auth_reset()
    channel_reset()
    messages_reset()
    u_id, token = get_user()

    message_send(token, 1, "first message")
    message_remove(token, 0)
    
    with pytest.raises(InputError):
        message_remove(token, 0)
        
######### message_edit ###########  
def test_message_edit_valid():
    auth_reset()
    channel_reset()
    messages_reset()
    u_id, token = get_user()
    u_id1, token1 = get_user_extra()

    channels_create(token, 'channel 1', True)
    channel_join(token1, 1)
    message_send(token1, 1, "first message")
    message_edit(token, 0, "new first message")
    
    assert data['messages'][0]['message'] == "new first message"
    
    message_edit(token1, 0, "newer first message")
    assert data['messages'][0]['message'] == "newer first message"

def test_message_edit_invalid():
    auth_reset()
    channel_reset()
    messages_reset()
    u_id, token = get_user()
    u_id1, token1 = get_user_extra()

    channels_create(token, 'channel 1', True)
    message_send(token, 1, "first message")
    
    with pytest.raises(AccessError):
        message_edit(token1, 0, "You are not authorised to edit this message")

        
