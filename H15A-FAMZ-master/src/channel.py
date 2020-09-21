from error import InputError, AccessError
from storage import data

def get_data():
    global data
    return data

"""Given token, return user info"""
def helper_token(token):
    find_user = {}
    for user in data['users']:
        if token == user['token']:
            find_user['u_id'] = user['u_id']
            find_user['name_first'] = user['name_first']
            find_user['name_last'] = user['name_last']
            find_user['permission'] = user['permission']
    return find_user

"""Given u_id, return user info"""
def helper_u_id(u_id):
    find_user = {}
    for user in data['users']:
        if u_id == user['u_id']:
            find_user['u_id'] = user['u_id']
            find_user['name_first'] = user['name_first']
            find_user['name_last'] = user['name_last']
            find_user['permission'] = user['permission']
            find_user['token'] = user['token']
    return find_user

""" Given channel_id, return the amount of messages inside that channnel
and return 50 or less messages from the channel
"""
def get_messages(channel_id, start):
    channel_messages = []
    channel_messages_50 = []
    channel_messages_sorted = []
    for message in data['messages']:
        if message['channel_id'] == channel_id:
            channel_messages.append(message)
    if len(channel_messages) - 50 >= start:
        # more than 50 messages not yet return in channel
        for start in range(start, start + 50):
            channel_messages[start]['time_created'] = channel_messages[start]['time_created'].replace(tzinfo=timezone.utc).timestamp()
            channel_messages_50.append(channel_messages[start])
    else:
        for start in range(start, len(channel_messages)):
            channel_messages[start]['time_created'] = channel_messages[start]['time_created'].replace(tzinfo=timezone.utc).timestamp()
            channel_messages_50.append(channel_messages[start]) 
    channel_messages_sorted = sorted(channel_messages_50, key = lambda i: i['time_created'], reverse=True)
    return len(channel_messages), channel_messages_sorted

"""Given token and channel_id, check if channel_id is valid/ 
authorized user is in channel/ authroized user is an owner of the channel,
return channel info"""
def helper_channel(token, channel_id):
    data = get_data()
    valid_token = 0
    valid_channel_id = 0
    check_owner = 0
    channel_info = {}
    target = helper_token(token)
    for channel in data['channels_info']:
        # Check if the channel_id is a valid channel
        if channel['channel_id'] == int(channel_id):
            # Found channel
            valid_channel_id = 1 
            channel_info = channel
            for member in channel['all_members']:
                #Check if token(authorized user) is a member of the channel
                if member['u_id'] == target['u_id']:
                    valid_token = 1   
            for member in channel['owner_members']:
                if member['u_id'] == target['u_id']:
                    check_owner = 1                      
    return valid_channel_id, valid_token, channel_info, check_owner

def channel_invite(token, channel_id, u_id):
    data = get_data()
    channel_info = helper_channel(token, channel_id)
    target = helper_u_id(u_id)
    channel_info_target = helper_channel(target['token'], channel_id)

    if channel_info[0] == 0:
        raise InputError(description="Invalid channel_id")
    if target == {}:
        raise InputError(description="Invalid u_id")
    if channel_info[1] == 0:
        raise AccessError(description="Invalid token") 
    
    #Check if target already in channel
    if channel_info_target[1] == 0:
        del target['token']
        #slackr owner case
        if target['permission'] == 1:
            #delete permission key for output
            del target['permission']
            channel_info[2]['owner_members'].append(target)
            channel_info[2]['all_members'].append(target)
        else:
            #delete permission key for output
            del target['permission']
            channel_info[2]['all_members'].append(target)
    
    return {}

def channel_details(token, channel_id):
    data = get_data() 
    channel_info = helper_channel(token, channel_id)
    if channel_info[0] == 0:
        raise InputError(description="Invalid channel_id")
    if channel_info[1] == 0:
        raise AccessError(description="Invalid token")    
    
    return {
        'name': channel_info[2]['name'],
        'owner_members': channel_info[2]['owner_members'],
        'all_members': channel_info[2]['all_members'],
    }


def channel_messages(token, channel_id, start):
    data = get_data() 
    channel_info = helper_channel(token, channel_id)
    channel_messages = get_messages(channel_id, start)
    if channel_info[0] == 0:
        raise InputError(description="Invalid channel_id")
    if start >= channel_messages[0]:
        raise InputError(description="Start is greater than or equal to the total number of messages in the channel")
    if channel_info[1] == 0:
        raise AccessError(description="Invalid token")    
    
    new_list = [{k: v for k, v in d.items() if k != 'channel_id'} for d in channel_messages[1]]
    if len(channel_messages[1]) == 50:
        return dumps({
            # using sorted to return the most recent message first
            'messages': new_list,
            'start': start,
            'end': start + 50,
        })
    if len(channel_messages[1]) < 50:
        return dumps({
            'messages': new_list,
            'start': start,
            'end': -1,
        })

def channel_leave(token, channel_id):
    data = get_data() 
    channel_info = helper_channel(token, channel_id)
    target = helper_token(token)
    if channel_info[0] == 0:
        raise InputError(description="Invalid channel_id")
    if channel_info[1] == 0:
        raise AccessError(description="Invalid token")    
    
    del target['permission']
    channel_info[2]['all_members'].remove(target)

    return {}

def channel_join(token, channel_id):
    data = get_data() 
    channel_info = helper_channel(token, channel_id)
    target = helper_token(token)
    if channel_info[0] == 0:
        raise InputError(description="Invalid channel_id")
    if channel_info[2]['is_public'] == False and target['permission'] == 2:
        raise AccessError(description="Invalid token")
    
    #check if target already in channel
    if channel_info[1] == 0:
        #slackr owner case
        if target['permission'] == 1:
            #delete key permission for output
            del target['permission']
            channel_info[2]['all_members'].append(target)
            channel_info[2]['owner_members'].append(target)
        else:
            del target['permission']
            channel_info[2]['all_members'].append(target)

    return {}

def channel_addowner(token, channel_id, u_id):
    data = get_data() 
    channel_info = helper_channel(token, channel_id)
    user = helper_token(token)
    target = helper_u_id(u_id)
    channel_info_target = helper_channel(target['token'], channel_id)
    if channel_info[0] == 0:
        raise InputError(description="Invalid channel_id")
    if channel_info_target[3] == 1:
        #user with u_id already owner of channel
        raise InputError(description="user already owner")
    if channel_info[3] == 0 and user['permission'] == 2:
        raise AccessError(description="Invalid token") 
    
    #check if target in channel
    if channel_info_target[1] == 1:
        del target['permission']
        del target['token']
        channel_info[2]['owner_members'].append(target)
    
    return {}  

def channel_removeowner(token, channel_id, u_id):
    data = get_data()
    channel_info = helper_channel(token, channel_id)
    user = helper_token(token)
    target = helper_u_id(u_id)
    channel_info_target = helper_channel(target['token'], channel_id)
    if channel_info[0] == 0:
        raise InputError(description="Invalid channel_id")
    if channel_info_target[3] == 0:
        #user with u_id not owner of channel
        raise InputError(description="user not owner")
    if channel_info[3] == 0 and user['permission'] == 2:
        raise AccessError(description="Invalid token")
    
    if channel_info_target[1] == 1:
        del target['token']
        del target['permission']
        channel_info[2]['owner_members'].remove(target)
    
    return {}
