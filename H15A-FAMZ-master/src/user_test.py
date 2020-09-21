from user import *
from auth import *
from error import *
from other import *
import pytest


def get_user():
    info =  auth_register('comp1531student@unsw.edu.au', 'testPassword', 'John', 'Smith')
    return(info['u_id'], info['token']) 

def get_user_extra():
    data = auth_register('comp1531tutor@unsw.edu.au', 'testPassword', 'Greg', 'Bob')
    return(data['u_id'], data['token'])

######### user_profile ###########
def test_user_profile_valid():    
  
    u_id, token = get_user()
        
    user_profile(token, u_id)
    

def test_profile_wrong_u_id():
    auth_reset()
    u_id, token = get_user()
    u_id_fake = u_id + 1
    
    with pytest.raises(InputError) as e:
        user_profile(token, u_id_fake)
        
def test_valid_user():
    auth_reset()
    u_id, token = get_user()
    
    user = user_profile(token, u_id)
    assert user['user']['u_id'] == u_id
    assert user['user']['name_first'] == 'John'
    assert user['user']['name_last'] == 'Smith'
    assert user['user']['email'] == 'comp1531student@unsw.edu.au'
            
def test_profile_invalid_u_id():
    auth_reset()
    u_id, token = get_user()
    u_id_invalid = 'h'
        
    with pytest.raises(InputError) as e:
        user_profile(token, u_id_invalid)   
    
######## user_profile_setname #########
'''
takes in: (token, name_first, name_last)
InputError when any of:
    name_first is not between 1 and 50 characters in length
    name_last is not between 1 and 50 characters in length
'''
def test_profile_setname():
    auth_reset()
    u_id, token = get_user()
    
    user = user_profile(token, u_id)
    
    user_profile_setname(token, 'Bob', 'Greg')
    
    # check that setname has worked
    user = user_profile(token, u_id)
    
    assert user['user']['name_first'] == 'Bob'
    assert user['user']['name_last'] == 'Greg'
    
def test_firstname_too_long():
    auth_reset()
    u_id, token = get_user()
        
    with pytest.raises(InputError) as e:
        user_profile_setname(token, 'B'*51, 'Greg')

def test_lastname_too_long():
    auth_reset()
    u_id, token = get_user()
    
    with pytest.raises(InputError) as e:
        user_profile_setname(token, 'Bob', 'G'*51)

def test_firstname_too_short():
    auth_reset()
    u_id, token = get_user()
    
    with pytest.raises(InputError) as e:
        user_profile_setname(token, '', 'Greg')

def test_lastname_too_short():
    auth_reset()
    u_id, token = get_user()
        
    with pytest.raises(InputError) as e:
        user_profile_setname(token, 'Bob', '')

########## user_profile_setemail ##########
'''
InputError when any of:
- Email entered is not a valid email using the method provided here (unless you feel you have a better method).
- Email address is already being used by another user
'''
def test_profile_setemail ():
    auth_reset()
    u_id, token = get_user()
    
    user_profile_setemail(token, 'newstudent@unsw.edu.au')  
    
    # new_token = 'newstudent@unsw.edu.au'
    
    user = user_profile(token, u_id)
    
    assert user['user']['email'] == 'newstudent@unsw.edu.au'
    
def test_invalid_token():    
    auth_reset()
    
    u_id, token = get_user()
    
    with pytest.raises(AccessError) as e:
        user_profile_setemail('invalid_token', 'newstudent1@unsw.edu.au')

def test_profile_setemail_invalid_email0():
    auth_reset()
    u_id, token = get_user()
    
    with pytest.raises(InputError) as e:
        user_profile_setemail(token, 'newstudent.edu.au')

def test_profile_setemail_invalid_email1():
    auth_reset()
    u_id, token = get_user()
    
    with pytest.raises(InputError) as e:
        user_profile_setemail(token, 'newstudent@unsw.eduau')

def test_profile_setemail_empty():
    auth_reset()
    u_id, token = get_user()
    
    with pytest.raises(InputError) as e:
        user_profile_setemail(token, '')    

def test_profile_setemail_email_in_use():
    auth_reset()
    u_id, token = get_user()
    user_profile_setemail(token, 'newstudent2@unsw.edu.au') 
    
    u_id1, token1 = get_user_extra()
    
    # no duplicates allowed
    with pytest.raises(InputError) as e:
        user_profile_setemail(token1, 'newstudent2@unsw.edu.au')    

########## user_profile_sethandle ##########

'''
InputError when any of:
- handle_str must be between 3 and 20 characters
- handle is already used by another user
'''

def test_profile_sethandle():
    auth_reset()
    u_id, token = get_user()

    user_profile_sethandle(token, 'GregEgg')
    user = user_profile(token, u_id)
    
    assert user['user']['handle_str'] == 'GregEgg'
    
def test_profile_handle_too_short():
    auth_reset()
    u_id, token = get_user()
    
    with pytest.raises(InputError) as e:
        user_profile_sethandle(token, 'G')

def test_profile_handle_empty():
    auth_reset()
    u_id, token = get_user()
    
    with pytest.raises(InputError) as e:
        user_profile_sethandle(token, '')

def test_profile_handle_too_long():
    auth_reset()
    u_id, token = get_user()
    
    with pytest.raises(InputError) as e:
        user_profile_sethandle(token, 'G'*21)

def test_profile_handle_invalid_token():
    auth_reset()
    u_id, token = get_user()
    
    with pytest.raises(AccessError) as e:
        user_profile_sethandle('invalid_token', 'Greg')

def test_profile_handle_in_use():
    auth_reset()
    u_id, token = get_user()
    user_profile_sethandle(token, 'Greg') 
    
    u_id1, token1 = get_user_extra()
    
    # no duplicates allowed
    with pytest.raises(InputError) as e:
        user_profile_sethandle(token1, 'Greg')  
    
########## users_all ##########

#returns a list of dictionaries containing everyone's info

def test_profile_all():
    auth_reset()
    u_id, token = get_user()
    
    users = users_all(token)
    assert users[1]['name_first'] == 'John'

def test_profile_all():
    auth_reset()
    u_id, token = get_user()
    
    with pytest.raises(AccessError) as e:
        users = users_all('invalid_token')

