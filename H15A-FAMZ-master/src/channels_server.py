from error import InputError
import pytest
from json import dumps
import requests
import urllib
from auth import *
from flask import Flask, request
from storage import data

APP = Flask(__name__)


def get_data():
    global data
    return data
    

def channels_list():
    
    token = request.args.get('token')
     
    data = get_data()
    ret = []
    #test to see if token is valid
    for user in data['users']:
        if token == user['token']:
            for channel in data['channels_info']:
                for member in channel['all_members']:
                    if user['u_id'] == member['u_id']:
                        
                        temp = {
                            'channel_id': channel['channel_id'],
                            'name': channel['name']
                        }
                        ret.append(temp)
            return dumps({'channels': ret})
                        
            
        
            
    raise InputError("invalid token")



def channels_listall():
    
    token = request.args.get('token')
    ret = []
    data = get_data()
    #test to see if token is valid
    for user in data['users']:
        if token == user['token']:
            for channel in data['channels_info']:
                if True == channel['is_public']:
                    temp = {
                        'channel_id': channel['channel_id'],
                        'name': channel['name']
                    }
                    ret.append(temp)
            return dumps({'channels': ret})
    raise InputError("invalid token")



def channels_create():

    data = get_data()
    
    info = request.get_json()
    token = info['token']
    name = info['name']
    is_public = info['is_public']
    
   
    
    
    #testing to see if is_public is valid
    if is_public != True and is_public != False:
        raise InputError('Invalid is_public')
        
    #testing to see if name is too long
    if len(name) > 20:
        raise InputError('Channel name too long')
        
    #establishing our channel_id   
    CHANNEL_ID = get_channel_id()
    
    #test to see if token is valid
    for user in data['users']:
        if token == user['token']:
            
            
            channel_info = {
                'channel_id': CHANNEL_ID,
                'name': name,
            }  
            
            #appending our channels dictionary
            data['channels'].append(channel_info)
                                 
            channel_members_info = {
                'channel_id': CHANNEL_ID,
                'name': name,
                'owner_members': [], #a dictornary containing the owenrs information
                'all_members': [], #a list of dictionaries containing infmation abougnt all members
                'is_public': is_public,
                'standup': {
                    'is_active': False,
                    'time_finish' : 0, 
                    'messages' : []       
                },
                'hangman': {
                    'is_active': False,
                    'guess_word' : [],
                    'blank' : [],
                    'wrong_letter' : [],
                    'guessed_letter' : []
                },
            }
            

            
                  
            
                    
            owner_info = {
                'u_id': user['u_id'],
                'name_first' : user['name_first'],
                'name_last': user['name_last']
            
            }

            
            #appending to channel_members_info for owner_members and all_members
            channel_members_info['owner_members'].append(owner_info)
            channel_members_info['all_members'].append(owner_info)
            
            data['channels_info'].append(channel_members_info)
            
            
            return dumps({
                'channel_id': CHANNEL_ID 
            })   
    
    
    raise InputError("invalid token")



def get_channel_id():
    data = get_data()
    
    #establishing channel_id by simply finding how many channels there are in our
    #database and and adding 1 to that number to get our channel_id
    channel_id = len(data['channels']) + 1 
    
    return channel_id
   
def channel_reset():
    data = get_data()
    
    data['channels'] = []
    data['channel_id'] = []
    
    return
    

       
    
    
    
    
    
    
    

