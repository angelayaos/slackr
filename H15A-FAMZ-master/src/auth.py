from error import InputError
import pytest
from storage import data






def get_data():
    global data
    return data


def auth_login(email, password):
    for user in data['users']:
        
        if email == user['email'] and password == user['password']:
            return {
                'u_id': user['u_id'],
                'token': user['token']
            }
        
    raise InputError("Invalid email or password")

def auth_logout(token):
    for user in data['users']:
        if token == user['token']:
             return {
                'is_success': True,
            }
    
    raise InputError("Invlaid Token ")   
    


def auth_register(email,password, name_first, name_last):
  
    

    #testing for invlaid email
    if '@' not in email or '.' not in email:
        raise InputError("Invalid email")
    #test to see if user email is already registed 
    for user in data['users']:
        if email == user['email']:
            raise InputError("Email already registered")
     
    
    #testing for invalid password
    if len(password) < 6:
        raise InputError("Password too weak")
    
    #testing for invlid name_first and name_last
    if len(name_first) < 1 or len(name_first) > 50:
        raise InputError("Invalid First Name")
    if len(name_last) < 1 or len(name_last) > 50:
        raise InputError("Invlaid Last Name")
    
   
    
    
    
    #establish u_id and token
    U_ID = get_u_id()
    TOKEN = get_token(email)
    
    
    
    
    #establishing handle 
    HANDLE = get_handle(name_first, name_last)
    
    
    #making info for new user
    info = {
        'email': email,
        'password': password,
        'name_first': name_first,
        'name_last': name_last,
        'u_id': U_ID,
        'token': TOKEN,
        'handle': HANDLE,
        'permission': get_permission()
    } 
   
    
    #append our data of all users
    data['users'].append(info)
        
    #what we will return 
    ret = {
        'u_id': U_ID,
        'token': TOKEN
    }
    
    return(ret)
    
def get_permission():
    if data['count'] == 1:
        return 1
    return 2   
    
def get_u_id():
    data['count'] += 1
    
    U_ID = data['count']
    
    return(U_ID)
    
def get_token(email):
    
    return(email)
    
def get_handle(name_first, name_last):
    temp = name_first + name_last
    
    #if hadnel it more then 20 character long we will cut it down
    if len(temp) > 20:
        temp = temp[0:19]
          
    for user in data['users']:
        if temp == user['handle']:
            temp = temp + 'a'
    
    return(temp)


def auth_reset():
    global data
    data = {
        'users': [],  #'users' is a list where each element is a dictonary containing all the data about the user
    
        'messages': [],
   
        'channels': [],
    
        'members': [],
    
        'reacts': [],
    
  
    
        'count': 0,   #'count' is just a count of how many users there are
        'channels_info': [],
    }
    return 

     

    
     

