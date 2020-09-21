from error import InputError
from auth import auth_register
from auth import auth_login
from auth import auth_logout
#from auth import auth_reset
import pytest

#************************** REGISTER TESTS ***********************************
def test_register():
    
    auth_register('comp1531student@unsw.edu.au', 'testpassword', 'John', 'Smith')
    auth_register('comp1531stgudent@unsw.edu.au', 'testpassword', 'John', 'Smith')
def test_register_invalid_password():
    
    with pytest.raises(InputError) as e:
        auth_register('comp1531stugdent@unsw.edu.au', '1', 'John', 'Smith')

def test_register_invalid_first_name():
    
    with pytest.raises(InputError) as e:
           auth_register('compd1531student@unsw.edu.au', 'testpassword', 'John' * 51 , 'Smith')

def test_register_invalid_last_name():
    
    with pytest.raises(InputError) as e:
           auth_register('comp1531student@funsw.edu.au', 'testpassword', 'John', 'Smith' * 51)

def test_register_invalid_first_empty_name():
    
    with pytest.raises(InputError) as e:
           auth_register('comp1531student@ungsw.edu.au', 'testpassword', '', 'Smith')

def test_register_invalid_last_empty_name():
    
    with pytest.raises(InputError) as e:
           auth_register('comp1531sstudent@unsw.edu.au', 'testpassword', 'John', '')

def test_register_invalid_at_email():
    
    with pytest.raises(InputError) as e:
           auth_register('coamp15s31studentunsw.edu.au', 'testpassword', 'John', 'Smith')

def test_register_invalid_period_email():
    
    with pytest.raises(InputError) as e:
           auth_register('1comp1531student@unsweduau', 'testpassword', 'John', 'Smith')
  
def test_register_empty_input():

    with pytest.raises(InputError) as e:
           auth_register('', '', '', '')    

def test_register_twice():

    
    auth_register('comp1531shhtudent@unsw.edu.au', 'testpassword', 'John', 'Smith') 
    with pytest.raises(InputError) as e:
        auth_register('comp1531shhtudent@unsw.edu.au', 'testpassword', 'John', 'Smith') 

           
                   

#*********************** LOGIN TESTS ******************************************
def test_login():
    
    result_register = auth_register('comp153student@unsw.edu.au', 'testPassword', 'John', 'Smith')
    u_id_register = result_register['u_id']
    token_register = result_register['token']
    

    result_login = auth_login('comp153student@unsw.edu.au', 'testPassword')

    u_id_login = result_login['u_id']
    token_login = result_login['token']
    
    assert u_id_register == u_id_login
    
    assert token_register == token_login
    
def test_login_invalid_password():
    
    auth_register('comphell1531student@unsw.edu.au', 'testPassword', 'John', 'Smith')
   
    with pytest.raises(InputError) as e:
        auth_login('comphell1531student@unsw.edu.au', 'wrongPassword')
        
def test_login_non_registered_email():
    
    auth_register('compyoyo1531student@unsw.edu.au', 'testPassword', 'John', 'Smith')
   
    with pytest.raises(InputError) as e:
        auth_login('non_registered_user@unsw.edu.au', 'testPassword')
        
def test_login_invalid_email():
    
    auth_register('compwhatup1531student@unsw.edu.au', 'testPassword', 'John', 'Smith')
   
    with pytest.raises(InputError) as e:
        auth_login('compwhatup1531studnetunsw.edu.au', 'testPassword')

def test_login_empty_email():
    
    auth_register('compkk1531student@unsw.edu.au', 'testPassword', 'John', 'Smith')
   
    with pytest.raises(InputError) as e:
        auth_login('', 'testPassword')

def test_login_empty_password():
    
    auth_register('comphh1531student@unsw.edu.au', 'testPassword', 'John', 'Smith')
   
    with pytest.raises(InputError) as e:
        auth_login('comphh1531student@unsw.edu.au', '')
        
#*********************** LOGOUT TESTS ******************************************

#Assume that register and login are sucessful 
def test_logout():
    
    result_register = auth_register('goodcomp1531student@unsw.edu.au', 'testPassword', 'John', 'Smith')
    token_register = result_register['token']
    

    result_login = auth_login('goodcomp1531student@unsw.edu.au', 'testPassword')

    token_login = result_login['token']
    
    assert token_register == token_login    
    
    valid_token = token_login
    
    auth_logout(valid_token)


def test_logout_invalid_token():
    with pytest.raises(InputError) as e:
        auth_logout('invalid token')


