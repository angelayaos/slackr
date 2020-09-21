'''
implementation of the standup functions, allowing the user create a standup in a channel
'''
# server packages
from json import dumps
import requests
import urllib
from flask import Flask, request
from storage import data
# other packages/files
from user import *
from auth import *
from error import *
from other import *
import pytest
import storage
import datetime

def get_data():
    global data
    return data

# helper functions
# given a token, this function returns the u_id associated with that user
def u_id_from_token(token):
    for user in data['users']:
        if token == user['token']:
            return user['u_id']
    raise AccessError("Token is invalid")
# given a channel_id, this function returns the channel associated with that id
def channel_from_channel_id(channel_id):
    valid = False
    for channel in data['channels_info']:
        if channel_id == channel['channel_id']:
            return channel
            valid = True
    if valid == False:
        raise InputError("Invalid channel_id")
# given a channel, this functions checks if a standup is active
def standup_time_check(channel):
    time_now = datetime.timedelta(datetime.datetime.now())
    time_finish = datetime.timedelta(channel['standup']['time_finish'])
    time_difference = time_finish - time_now
    
    if time_difference <= 0:
        return 0
    if time_difference > 0:
        return time_difference

#standup_start function allows the user to start a standup
def standup_start():
    # getting data
    info = request.get_json()
    token = info['token']
    channel_id = info['channel_id']
    length = info['length']
    
    u_id = u_id_from_token(token)  
    channel = channel_from_channel_id(channel_id)    
    channel_valid = False
    token_valid = False
    # check if token is valid
    for user in data['users']:
        if token == user['token']:
            token_valid = True
    if token_valid == False:
        raise AccessError("Token is invalid")
    # search through channels to see if a channel_id matches  
    for channel_now in data['channels_info']:
        if channel_id == channel_now['channel_id']:
            channel_valid = True
            current_channel = channel_now
    if channel_valid == False:
        raise InputError("Channel_id is invalid")
    # check if user is in channel
    for member in current_channel['all_members']:
        if u_id == member['u_id']:
            valid_token = True
    if valid_token == False:
        raise AccessError("User is not a member of this channel")
    # check if standup is already running
    time_to_finish = standup_time_check(current_channel)
    if current_channel['standup']['is_active'] == True and time_to_finish > 0:
        raise InputError("Standup is currently running in this channel")
    # if no other errors, start standup
    current_channel['standup']['is_active'] = True
    
    time_finish = datetime.timedelta(seconds = length) + datetime.timedelta(datetime.datetime.now())
    
    return {
    'time_finish': time_finish,
    }

# standup_active function determines whether a standup is happening within a given channel
def standup_active():
    # getting data
    token = request.args.get('token')
    channel_id = request.args.get('channel_id')
    
    active = False
    channel_valid = False
    token_valid = False
    # check if token is valid
    for user in data['users']:
        if token == user['token']:
            token_valid = True
    if token_valid == False:
        raise AccessError("Token is invalid")
    #search through channels to see if a channel_id matches  
    for channel_now in data['channels_info']:
        if channel_id == channel_now['channel_id']:
            channel_valid = True
            current_channel = channel_now
            time_to_finish = standup_time_check(channel)
            if channel['standup']['is_active'] == True and time_to_finish > 0:
                active = True
    if channel_valid == False:
        raise InputError("Channel_id is invalid")
    # if standup is not active in a given channel
    if active == False:
        x = None
        return {
            'is_active': active,
            'time_finish': x,
        }
    # if standup is active in a given channel
    return {
        'is_active': active,
        'time_finish': time_finish,
    }

# standup_send function allows user to send a message during a standup
def standup_send():
    # getting data
    info = request.get_json()
    token = info['token']
    channel_id = info['channel_id']
    message = info['message']
    
    valid_token = False
    # check if message is >1000 characters
    if len(message) > 1000:
        raise InputError("Message must be less than 1000 characters")
    # check if token is invalid (member is not in channel)
    u_id = u_id_from_token(token)
    channel = channel_from_channel_id(channel_id)
    for member in channel['all_members']:
        if u_id == member['u_id']:
            valid_token = True
    if valid_token == False:
        raise AccessError("User is not a member of this channel")
    # check if standup is running 
    time_to_finish = standup_time_check(channel)
    if channel['standup']['is_active'] == True and time_to_finish > 0:
        lis = channel['standup']['messages']
        lis.append(message)
    # if standup is inactive, raise an InputError and set everything back to normal
    channel['standup']['is_active'] = False
    channel['standup']['time_finish'] = 0
    raise InputError("Active standup is not currently running")    
   
    return {}
   
