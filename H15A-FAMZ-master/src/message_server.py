from error import InputError, AccessError
import pytest
from datetime import datetime as dt
from json import dumps
import requests
import urllib
from flask import Flask, request
from storage import data
import pytz
import wikiquote

APP = Flask(__name__)

def get_data():
    global data
    return data

def message_send():
    info = request.get_json()
    token = info['token']
    channel_id = info['channel_id']
    message = info['message']

    u_id = get_uid_from_token(token)

    if user_in_channel(u_id, channel_id) is False:
        raise AccessError("User is not in this channel")

    if len(message) >= 1000:
        raise InputError("Message cannot be longer than 1000 characters")

    message_id = get_message_id()

    #Hangman Game
    if message == '/hangman':
        if data['channels_info'][int(channel_id) - 1]['hangman']['is_active'] == False:
            data['channels_info'][int(channel_id) - 1]['hangman']['is_active'] = True
            guess = list(wikiquote.random_titles(max_titles=1)[0])
            data['channels_info'][int(channel_id) - 1]['hangman']['guess_word'] = guess
            blank = data['channels_info'][int(channel_id) - 1]['hangman']['blank']

            #Fill in the blanks
            for char in guess:
                if char.isalpha() == True:
                    char = '_ '
                blank.append(char)
            data['channels_info'][int(channel_id) - 1]['hangman']['blank'] = blank

            message = 'Welcome to Hangman\n\nWord: {}'.format("".join(blank))

        else:
            raise InputError(description="An active game is already running for this channel")

    # pylint: disable=c0301
    if data['channels_info'][int(channel_id) - 1]['hangman']['is_active'] == True and message.startswith('/guess ') == True:
        guess = data['channels_info'][int(channel_id) - 1]['hangman']['guess_word']
        blank = data['channels_info'][int(channel_id) - 1]['hangman']['blank']
        flag = False

        if len(message) == 8:
            if message[7].isalpha() == True:
                mes = message[7].upper()

                #Duplicate case
                if mes in data['channels_info'][int(channel_id) - 1]['hangman']['guessed_letter']:
                    raise InputError(description="{} has already been guessed".format(mes))

                #Correct case
                for char in range(len(guess)):
                    # Covert blank to words
                    if mes == guess[char].upper():
                        flag = True
                        blank[char] = guess[char].upper()
                message = display_hangman(channel_id, blank, guess)

                #Update list
                data['channels_info'][int(channel_id) - 1]['hangman']['blank'] = blank
                data['channels_info'][int(channel_id) - 1]['hangman']['guessed_letter'].append(mes)

                #Hangman won case
                if '_ ' not in blank:
                    message = 'Word: {}\nCongratulations! You have won hangman.'.format("".join(guess))
                    data['channels_info'][int(channel_id) - 1]['hangman']['is_active'] = False
                    data['channels_info'][int(channel_id) - 1]['hangman']['blank'] = []
                    data['channels_info'][int(channel_id) - 1]['hangman']['guessed_letter'] = []
                    data['channels_info'][int(channel_id) - 1]['hangman']['guess_word'] = []
                    data['channels_info'][int(channel_id) - 1]['hangman']['wrong_letter'] = []

                #Incorrect case
                if flag == False:
                    data['channels_info'][int(channel_id) - 1]['hangman']['wrong_letter'].append(mes)
                    message = display_hangman(channel_id, blank, guess)
                    #Hangman lost case
                    if len(data['channels_info'][int(channel_id) - 1]['hangman']['wrong_letter']) == 10:
                        data['channels_info'][int(channel_id) - 1]['hangman']['is_active'] = False
                        data['channels_info'][int(channel_id) - 1]['hangman']['blank'] = []
                        data['channels_info'][int(channel_id) - 1]['hangman']['guessed_letter'] = []
                        data['channels_info'][int(channel_id) - 1]['hangman']['guess_word'] = []
                        data['channels_info'][int(channel_id) - 1]['hangman']['wrong_letter'] = []

            else:
                raise InputError(description="Usage: /guess (letter)")
        else:
            raise InputError(description="Usage: /guess (letter)")

    message_info = {
        'channel_id': channel_id,
        'message_id': message_id,
        'u_id': get_uid_from_token(token),
        'message': message,
        'time_created': dt.now(),
        'reacts': [{'react_id': 1, 'u_ids': [], 'is_this_user_reacted': False}],
        'is_pinned': False
    }

    data['messages'].append(message_info)

    return dumps({
        'message_id': message_id
        })

def message_sendlater():
    info = request.get_json()
    token = info['token']
    channel_id = info['channel_id']
    message = info['message']
    time_sent = info['time_sent']

    u_id = get_uid_from_token(token)

    if type(time_sent) != dt:
        time_sent = dt.utcfromtimestamp(time_sent)

    if channel_exists(channel_id) is False:
        raise InputError("Channel is invalid")    
    
    if user_in_channel(u_id, channel_id) is False:
        raise AccessError("User is not in this channel")
 
    if len(message) >= 1000:
        raise InputError("Message cannot be longer than 1000 characters")

    if dt.utcnow() >= time_sent:
        raise InputError(description='Time must be set at a specified time in the future')
    
    time_sent = time_sent.replace(tzinfo=pytz.utc)
        
    message_id = get_message_id()

    message_info = {
        'channel_id': channel_id,
        'message_id': message_id,
        'u_id': get_uid_from_token(token),
        'message': message,
        'time_created': time_sent,
        'reacts': [{'react_id': 1, 'u_ids': [], 'is_this_user_reacted' : False}],
        'is_pinned': False
    }
    
    data['messages'].append(message_info)
    
    return dumps({
        'message_id': message_id
    })

def message_react():
    info = request.get_json()
    token = info['token']
    message_id = info['message_id']
    react_id = info['react_id']

    message_index = find_message(message_id)

    if message_index is None: 
        raise InputError("Not a valid message")

    u_id = get_uid_from_token(token)
    message = data['messages'][find_message(message_id)]
    channel_id = message['channel_id']

    if react_id != 1:
        raise InputError("Not a valid react")
        
    if u_id in message['reacts'][int(react_id) - 1]['u_ids']:
        raise InputError("Already reacted to this message")
            
    message['reacts'][int(react_id) - 1]['u_ids'].append(u_id)  
    return dumps({})

def message_unreact():
    info = request.get_json()
    token = info['token']
    message_id = info['message_id']
    react_id = info['react_id']

    message_index = find_message(message_id)
    if message_index is None: 
        raise InputError("Not a valid message")
   
    u_id = get_uid_from_token(token)
    message = data['messages'][find_message(message_id)]
    channel_id = message['channel_id']
        
    if react_id != 1:
        raise InputError("Not a valid react")
     
    if u_id not in message['reacts'][int(react_id) - 1]['u_ids']:
        raise InputError('Message already unreacted')
    
    message['reacts'][int(react_id) - 1]['u_ids'].remove(u_id)   
    return dumps({})

def message_pin():
    info = request.get_json()
    token = info['token']
    message_id = info['message_id']

    message_index = find_message(message_id)
    if message_index is None:
        raise InputError("Not a valid message")
        
    u_id = get_uid_from_token(token)
    user = data['users'][u_id - 1]

    message = data['messages'][message_index]

    if user['permission'] != 1:
        raise InputError("You are not the owner")

    if user_in_channel(u_id, message['channel_id']) is False:
        raise AccessError("You are not a member of this channel")

    if message['is_pinned'] is True:
        raise InputError("Message already pinned")

    message['is_pinned'] = True
    return dumps({})

def message_unpin():
    info = request.get_json()
    token = info['token']
    message_id = info['message_id']

    message_index = find_message(message_id)
    if message_index is None:
        raise InputError("Not a valid message")
        
    u_id = get_uid_from_token(token)
    user = data['users'][u_id - 1]

    message = data['messages'][message_index]

    if user['permission'] != 1:
        raise InputError("You are not the owner")

    if user_in_channel(u_id, message['channel_id']) is False:
        raise AccessError("You are not a member of this channel")

    if message['is_pinned'] is False:
        raise InputError("Message already unpinned")

    message['is_pinned'] = False
    return dumps({})

def message_remove():
    info = request.get_json()
    token = info['token']
    message_id = info['message_id']
    
    message_index = find_message(message_id)
    if message_index is None:
        raise InputError("Not a valid message")

    u_id = get_uid_from_token(token)
    user = data['users'][u_id - 1]
    
    message = data['messages'][message_index]
    
    if user['permission'] == 1 or user['u_id'] == message['u_id']:
        data['messages'].remove(message)
    else:
        raise AccessError("You are not authorised to remove message")
        
    return dumps({})

def message_edit():
    info = request.get_json()
    token = info['token']
    message_id = info['message_id']
    message = info['message']

    u_id = get_uid_from_token(token)
    user = data['users'][u_id - 1]
    msg = data['messages'][find_message(message_id)]
    
    if user['permission'] != 1 and msg['u_id'] != user['u_id']:
        raise AccessError("You are not authorised to remove message")
    
    if message == "":
        message_remove(token, message_id)
    else:
        msg['message'] = message
        
    return dumps({})
    
# helper functions
def get_channel_info(channel_id):
    for channel in data['channels_info']:
        if channel['channel_id'] == int(channel_id):
            return channel
    raise InputError("Channel not found")
    
def user_in_channel(u_id, channel_id):
    channel = get_channel_info(channel_id)
    for member in channel['all_members']:
        if u_id == member['u_id']:
            return True
    return False
        
def get_message_id():
    if len(data['messages']) == 0:
        return 0
    return int(data['messages'][len(data['messages']) - 1]['message_id']) + 1

def get_uid_from_token(token):
    for user in data['users']:
        if token == user['token']:
            return user['u_id']
    raise AccessError("u_id is invalid")
    
def channel_exists(channel_id):
    for channel in data['channels_info']:
        if channel['channel_id'] == int(channel_id):
            return True
    return False
    
def find_message(message_id):
    i = 0
    for message in data['messages']:
        if message['message_id'] == message_id:
            return i
        i += 1
    return None
   
def messages_reset():
    
    data['messages'] = []
    data['reacts'] = []
    
    return {}

def display_hangman(channel_id, blank, guess):
    """ Given channel_id, blank and guess, return message output for hangman game """
    wrong = data['channels_info'][int(channel_id) - 1]['hangman']['wrong_letter']
    message = ''
    if not wrong:
        message = 'Word: {}\nYou have guessed: {}'.format(" ".join(blank), " ".join(wrong))
    if len(wrong) == 1:
        # pylint: disable=c0301
        message = 'Word: {}\n============\nYou have guessed: {}'.format(" ".join(blank), " ".join(wrong))
    elif len(wrong) == 2:
        # pylint: disable=c0301
        message = 'Word: {}\n|\n|\n|\n|\n============\nYou have guessed: {}'.format(" ".join(blank), " ".join(wrong))
    elif len(wrong) == 3:
        # pylint: disable=c0301
        message = 'Word: {}\n+-------------\n|\n|\n|\n|\n============\nYou have guessed: {}'.format(" ".join(blank), " ".join(wrong))
    elif len(wrong) == 4:
        # pylint: disable=c0301
        message = 'Word: {}\n+-------------\n|           |\n|\n|\n|\n============\nYou have guessed: {}'.format(" ".join(blank), " ".join(wrong))
    elif len(wrong) == 5:
        # pylint: disable=c0301
        message = 'Word: {}\n+-------------\n|           |\n|           O\n|\n|\n============\nYou have guessed: {}'.format(" ".join(blank), " ".join(wrong))
    elif len(wrong) == 6:
        # pylint: disable=c0301
        message = 'Word: {}\n+-------------\n|           |\n|           O\n|           |\n|\n============\nYou have guessed: {}'.format(" ".join(blank), " ".join(wrong))
    elif len(wrong) == 7:
        # pylint: disable=c0301
        message = 'Word: {}\n+-------------\n|           |\n|           O\n|         / |\n|\n============\nYou have guessed: {}'.format(" ".join(blank), " ".join(wrong))
    elif len(wrong) == 8:
        # pylint: disable=c0301
        message = 'Word: {}\n+-------------\n|           |\n|           O\n|         / | \\ \n|\n============\nYou have guessed: {}'.format(" ".join(blank), " ".join(wrong))
    elif len(wrong) == 9:
        # pylint: disable=c0301
        message = 'Word: {}\n+-------------\n|           |\n|           O\n|         / | \\ \n|        / \n============\nYou have guessed: {}'.format(" ".join(blank), " ".join(wrong))
    elif len(wrong) == 10:
        # pylint: disable=c0301
        message = 'Word: {}\nYou lost!\n+-------------\n|           |\n|           O\n|         / | \\ \n|          /  \\ \n============\nYou have guessed: {}'.format("".join(guess), " ".join(wrong))

    return message
