from auth import *
from error import *
from other import *
import pytest
from storage import data

def get_data():
    global data
    return data

def user_profile(token, u_id):
    for user in data['users']:
        
        if token == user['token'] and u_id == user['u_id']:
            return {
                'user' : {
                    'u_id': user['u_id'],
                    'email': user['email'],
                    'name_first': user['name_first'],
                    'name_last': user['name_last'],
                    'handle_str': user['handle'],
                }
            }
    # InputError when u_id is not associated with a valid user
    raise InputError("u_id or token is not valid")

def user_profile_setname(token, name_first, name_last):
    
    # error checking - InputError when name is not within 1-50 characters inclusive 
    if len(name_first) < 1:
        raise InputError("name_first too short. must be 1-50 characters")
        
    if len(name_first) > 50:
        raise InputError("name_first too long. must be 1-50 characters")
    
    if len(name_last) < 1:
        raise InputError("name_last too short. must be 1-50 characters")
    
    if len(name_last) > 50:
        raise InputError("name_last too long. must be 1-50 characters")
    
    for user in data['users']:
    
        if token == user['token']:        
            user['name_first'] = name_first
            user['name_last'] = name_last       
            return {}
    
    # if token doesn't match any user, then the token is invalid 
    raise AccessError("Token is invalid")
    return {}

def user_profile_setemail(token, email):
    
    # testing for invalid email
    if '@' not in email or '.' not in email:
        raise InputError("Invalid email")
    if '.com' not in email and '.edu.au' not in email and '.net' not in email:
        raise InputError("Invalid email")
    
    # testing if user email is already registed 
    for user in data['users']:
        if email == user['email']:
            raise InputError("Email already in use")
    
    for user in data['users']:   
        if token == user['token']:
            user['email'] = email
            return {}
    
    # if token doesn't match any user, then the token is invalid 
    raise AccessError("Token is invalid")
    return {}

def user_profile_sethandle(token, handle_str):
    
    #testing if handle is invalid (not between 2-20 characters)
    if len(handle_str) < 2:
        raise InputError("Handle too short. Must be between 2-20 characters")
    if len(handle_str) > 20:
        raise InputError("Handle too long. Must be between 2-20 characters")
    
    for user in data['users']:
        if handle_str == user['handle']:
            raise InputError("Handle already in use")
    
    for user in data['users']:
        if token == user['token']:
            user['handle'] = handle_str
            return {}
    
    # if token doesn't match any user, then the token is invalid 
    raise AccessError("Token is invalid")
    return {}
