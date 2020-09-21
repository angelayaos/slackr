import sys
import threading
import json
import search_server
from json import dumps
from flask import Flask, request
from flask_cors import CORS
from standup_flask import *
from workspace import *
from admin_server import *
from channels_server import *
from channel_server import *
from message_server import *
from user_server import *
from users_server import * 
from error import InputError
from auth_server import *

port = 4243

def defaultHandler(err):
    response = err.get_response()
    print('response', err, err.get_response())
    response.data = dumps({
        "code": err.code,
        "name": "System Error",
        "message": err.get_description(),
    })
    response.content_type = 'application/json'
    return response

APP = Flask(__name__)
CORS(APP)

APP.config['TRAP_HTTP_EXCEPTIONS'] = True
APP.register_error_handler(Exception, defaultHandler)

# Example
@APP.route("/echo", methods=['GET'])
def echo():
    data = request.args.get('data')
    if data == 'echo':
   	    raise InputError(description='Cannot echo "echo"')
    return dumps({
        'data': data
    })


################## AUTH #############################################

@APP.route('/auth/register', methods=['POST'])
def register():
    save()
    return auth_register()
@APP.route('/auth/login', methods=['POST'])
def login():
    save()
    return auth_login()
@APP.route('/auth/logout', methods=['POST'])
def logout():    
    return auth_logout()
@APP.route('/auth/passwordreset/request', methods=['POST'])
def password_request():    
    return auth_passwordreset_request()   
@APP.route('/auth/passwordreset/reset', methods=['POST'])
def password_reset():    
    return auth_passwordreset_reset()   
##################### channel ########################################### 
@APP.route('/channel/invite', methods=['POST'])
def invite():
    return channel_invite()
@APP.route('/channel/details', methods=['GET'])
def details():
    return channel_details()
@APP.route('/channel/messages', methods=['GET'])
def messages():    
    return channel_messages()
@APP.route('/channel/leave', methods=['POST'])
def leave():
    return channel_leave()
@APP.route('/channel/join', methods=['POST'])
def join():
    return channel_join()
@APP.route('/channel/addowner', methods=['POST'])
def addowner():
    return channel_addowner()
@APP.route('/channel/removeowner', methods=['POST'])
def removeowner():
    return channel_removeowner() 
##################### channels ############################################
@APP.route('/channels/create', methods=['POST'])
def create():
    return channels_create()
@APP.route('/channels/listall', methods=['GET'])
def listall():
    return channels_listall()
@APP.route('/channels/list', methods=['GET'])
def channels_list_function():
    return channels_list()

######################## search ##########################################
@APP.route('/search', methods=['GET'])
def search_message():    
    return search_server.search()

##################### message ##########################################
@APP.route('/message/send', methods=['POST'])
def send():
    return message_send()
@APP.route('/message/sendlater', methods=['POST'])
def sendlater():
    return message_sendlater()
@APP.route('/message/react', methods=['POST'])
def react():
    return message_react()
@APP.route('/message/unreact', methods=['POST'])
def unreact():
    return message_unreact()
@APP.route('/message/pin', methods=['POST'])
def pin():
    return message_pin()
@APP.route('/message/unpin', methods=['POST'])
def unpin():
    return message_unpin()
@APP.route('/message/remove', methods=['DELETE'])
def remove():
    return message_remove()
@APP.route('/message/edit', methods=['PUT'])
def edit():
    return message_edit()

########################### user ##########################################
@APP.route('/user/profile', methods=['GET'])
def profile():
    return user_profile()
@APP.route('/user/profile/setname', methods=['PUT'])
def setname():
    return user_profile_setname()
@APP.route('/user/profile/setemail', methods=['PUT'])
def setemail():
    return user_profile_setemail()
@APP.route('/user/profile/sethandle', methods=['PUT'])
def sethandle():
    return user_profile_sethandle()
@APP.route('/users/all', methods=['GET'])
def all_user():
    return users_all()
@APP.route('/user/profile/uploadphoto', methods=['POST'])
def photo_upload():
    return user_profile_upload_photo()
    
################### Admin ##############################################
@APP.route('/admin/userpermission/change', methods=['POST'])
def change_permission():
    return admin_change_permission()

@APP.route('/admin/user/remove', methods=['DELETE'])
def remove_user():
    return admin_remove_user()


################### workspace #####################################
@APP.route('/workspace/reset', methods=['POST'])
def reset_workspace():
    return workspace_reset()
    
 
################## standup #################################
@APP.route('/standup/start', methods=['POST'])
def start():
    return standup_start()
@APP.route('/standup/active', methods=['GET'])
def active():
    return standup_active()
@APP.route('/standup/send', methods=['POST'])
def send_standup():
    return standup_send()


       
def save():
    with open('saved_data.json', 'w') as FILE:
        json.dump(data, FILE) 
        
    t = threading.Timer(4, save)
    t.start()  
   

def load():
    with open('saved_data.json', 'r') as JSON_FILE:
        data = json.load(JSON_FILE)


if __name__ == "__main__":
    #load()
    APP.run(port=(int(sys.argv[1]) if len(sys.argv) == 2 else 8080))

