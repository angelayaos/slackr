import pytest
from auth import auth_register
import channel
import channels
from message import message_send
from error import InputError, AccessError

@pytest.fixture
def get_multiple_user():  
    data0 = auth_register('data0@unsw,edu.au', 'testPassword', 'John', 'Smith')
    data1 = auth_register('data1@unsw,edu.au', 'testPassword', 'Adam', 'Leak')
    #data0 refers to the first register member of slackr, thereby the owner of the slackr
    #data1 refers to the second register member of slackr, thereby a member of the slakr
    return(data0['u_id'], data0['token'],data1['u_id'], data1['token'])

#*********************** details test ***************************** 

def test_channel_details(get_multiple_user):
    u_id0, token0, u_id1, token1 = get_multiple_user
    data = channels_create(token0, 'My channel', True)
    channel1 = channel_details(token0, data['channel_id'])
    
    assert channel1['name'] == 'My channel'
    assert channel1['owner_members'][0]['u_id'] == u_id0
    assert channel1['owner_members'][0]['name_first'] == 'John'
    assert channel1['owner_members'][0]['name_last'] == 'Smith'
    assert channel1['all_members'][0]['u_id'] == u_id0
    assert channel1['all_members'][0]['name_first'] == 'John'
    assert channel1['all_members'][0]['name_last'] == 'Smith'   

def test_details_invalid_channel_id(get_multiple_user):
    u_id0, token0, u_id1, token1 = get_multiple_user
    data = channels_create(token0, 'My channel', True) 
    with pytest.raises(InputError) as e:
        channel_details(token0, 'invalid_channel_id') 

def test_details_invalid_access(get_multiple_user):
    u_id0, token0, u_id1, token1 = get_multiple_user
    data = channels_create(token0, 'My channel', True) 
    with pytest.raises(AccessError) as e:
        channel_details(token1, data['channel_id'])      

#*********************** Join test *****************************

def test_channel_join(get_multiple_user):
    u_id0, token0, u_id1, token1 = get_multiple_user
    data = channels_create(token0, 'My channel', True) 
    channel_join(token1, data['channel_id'])
    channel1 = channel_details(token1, data['channel_id'])

    assert channel1['name'] == 'My channel' 
    assert len(channel_1['all_members']) == 2
    assert channel1['all_members'][1]['u_id'] == u_id1
    assert channel1['all_members'][1]['name_first'] == 'Adam'
    assert channel1['all_members'][1]['name_last'] == 'Leak'  


def test_join_invalid_channel_id(get_multiple_user):
    u_id0, token0, u_id1, token1 = get_multiple_user
    data = channels_create(token0, 'My channel', True) 
    with pytest.raises(InputError) as e:
        channel_join(token1, 'invalid_channel_id')

def test_member_join_private_channel(get_multiple_user):	
    u_id0, token0, u_id1, token1 = get_multiple_user
    data = channels_create(token0, 'My channel', False) 
    with pytest.raises(AccessError) as e:
        channel_join(token1, data['channel_id'])

def test_sowner_join_private(get_multiple_user):
    # check if the owner of the slackr can join a private channel
    # check if the owner of the slackr owner privileges when
    # he/she joins a channel
    u_id0, token0, u_id1, token1 = get_multiple_user
    data = channels_create(token1, 'My channel', False) 
    channel_join(token0, data['channel_id'])
    channel1 = channel_details(token1, data['channel_id'])

    assert channel1['name'] == 'My channel'
    assert len(channel1['owner_members']) == 2
    assert channel1['owner_members'][1]['u_id'] == u_id0
    assert channel1['owner_members'][1]['name_first'] == 'John'
    assert channel1['owner_members'][1]['name_last'] == 'Smith'
    assert len(channel1['all_members']) == 2
    assert channel1['all_members'][1]['u_id'] == u_id0
    assert channel1['all_members'][1]['name_first'] == 'John'
    assert channel1['all_members'][1]['name_last'] == 'Smith' 
 

#*********************** Invite test *****************************

def test_channel_invite(get_multiple_user):
    u_id0, token0, u_id1, token1 = get_multiple_user
    data = channels_create(token0, 'My channel', True)
    channel_invite(token0, data['channel_id'], u_id1)
    channel1 = channel_details(token1)

    assert 'My channel' == channel1['name']
    assert len(channel_1['all_members']) == 2
    assert channel1['all_members'][1]['u_id'] == u_id1
    assert channel1['all_members'][1]['name_first'] == 'Adam'
    assert channel1['all_members'][1]['name_last'] == 'Leak' 


def test_invite_invalid_channel_id(get_multiple_user):
    u_id0, token0, u_id1, token1 = get_multiple_user
    data = channels_create(token0, 'My channel', True) 
    with pytest.raises(InputError) as e:
        channel_invite(token0, 'invalid_channel_id', u_id)

def test_invite_invalid_u_id(get_multiple_user):
    u_id0, token0, u_id1, token1 = get_multiple_user
    data = channels_create(token0, 'My channel', True) 
    with pytest.raises(InputError) as e:
        channel_invite(token0, data['channel_id'], 'invalid_u_id')
 
def test_invite_invalid_access(get_multiple_user):
    u_id0, token0, u_id1, token1 = get_multiple_user
    data = channels_create(token0, 'My channel', True)
    data2 = auth_register('data2@unsw,edu.au', 'testPassword', 'Mary', 'Jones') 
    with pytest.raises(AccessError) as e:
        channel_invite(token1, data['channel_id'], data2['u_id'])

def test_invite_sowner(get_multiple_user):
    # check if the owner of the slackr can join a private channel
    # check if the owner of the slackr owner privileges when
    # he/she is invited a channel
    u_id0, token0, u_id1, token1 = get_multiple_user
    data = channels_create(token1, 'My channel', False) 
    channel_invite(token0, data['channel_id'], u_id0)
    channel1 = channel_details(token1, data['channel_id'])

    assert 'My channel' == channel1['name']
    assert len(channel_1['owner_members']) == 2
    assert channel1['owner_members'][1]['u_id'] == u_id0
    assert channel1['owner_members'][1]['name_first'] == 'John'
    assert channel1['owner_members'][1]['name_last'] == 'Smith'
    assert len(channel_1['all_members']) == 2
    assert channel1['all_members'][1]['u_id'] == u_id0
    assert channel1['all_members'][1]['name_first'] == 'John'
    assert channel1['all_members'][1]['name_last'] == 'Smith'

#*********************** Leave test ***************************** 

def test_channel_leave(get_multiple_user):
    u_id0, token0, u_id1, token1 = get_multiple_user
    data = channels_create(token0, 'My channel', True)
    channel_invite(token0, data['channel_id'], u_id1)
    channel_leave(token1, data['channel_id'])
    channel1 = channel_details(token0)
    
    assert len(channel_1['all_members']) == 1

def test_leave_invalid_channel_id(get_multiple_user):
    u_id0, token0, u_id1, token1 = get_multiple_user
    data = channels_create(token0, 'invalid_channel', True) 
    channel_invite(token0, data['channel_id'], u_id1)
    with pytest.raises(InputError) as e:
        channel_leave(token1, 'invalid_channel_id')   

def test_leave_invalid_access(get_multiple_user):
    u_id0, token0, u_id1, token1 = get_multiple_user
    data = channels_create(token0, 'My channel', True) 
    with pytest.raises(AccessError) as e:
        channel_leave(token1, data['channel_id']) 

def test_channel_leave_owner(get_multiple_user):
    u_id0, token0, u_id1, token1 = get_multiple_user
    data = channels_create(token0, 'My channel', True)
    channel_invite(token0, data['channel_id'], u_id1)
    channel_leave(token0, data['channel_id'])
    channel1 = channel_details(token1)
    
    # Leave channel will not remove owner status
    assert len(channel_1['all_members']) == 1
    assert len(channel_1['owner_members']) == 1  

#*********************** addowner test ***************************** 

def test_channel_addowner(get_multiple_user):
    u_id0, token0, u_id1, token1 = get_multiple_user
    data = channels_create(token0, 'My channel', True)
    channel_invite(token0, data['channel_id'], u_id1)
    channel_addowner(token0, data['channel_id'], u_id1)
    channel1 = channel_details(token1, data[channel_id])
    
    assert len(channel1['owner_members']) == 2
    assert channel1['owner_members'][1]['u_id'] == u_id1
    assert channel1['owner_members'][1]['name_first'] == 'Adam'
    assert channel1['owner_members'][1]['name_last'] == 'Leak' 

def test_addowner_invalid_channel_id(get_multiple_user):
    u_id0, token0, u_id1, token1 = get_multiple_user
    data = channels_create(token0, 'My channel', True) 
    channel_invite(token0, data['channel_id'], u_id1)
    with pytest.raises(InputError) as e:
       channel_addowner(token0, 'invalid_channel_id', u_id1)   

def test_addowner_already_owner(get_multiple_user):
    u_id0, token0, u_id1, token1 = get_multiple_user
    data = channels_create(token0, 'My channel', True) 
    with pytest.raises(InputError) as e:
        channel_addowner(token0, data[channel_id], u_id0)  

def test_addowner_invalid_access(get_multiple_user):
    u_id0, token0, u_id1, token1 = get_multiple_user
    data = channels_create(token0, 'My channel', True) 
    with pytest.raises(AccessError) as e:
        channel_addowner(token1, data[channel_id], u_id1)

def test_addowner_invalid_access_member(get_multiple_user):
    u_id0, token0, u_id1, token1 = get_multiple_user
    data = channels_create(token0, 'My channel', True) 
    channel_invite(token0, data['channel_id'], u_id1)
    with pytest.raises(AccessError) as e:
        channel_addowner(token1, data[channel_id], u_id1)

def test_addowner_sowner(get_multiple_user):
    # check if the owner of slackr can addowner to a channel he/she does not join
    u_id0, token0, u_id1, token1 = get_multiple_user
    data = channels_create(token1, 'My channel', True) 
    data2 = auth_register('data2@unsw,edu.au', 'testPassword', 'Mary', 'Jones')
    channel_invite(data2['token'], data['channel_id'], data2['u_id'])
    channel_addowner(token0, data[channel_id], data2['u_id'])
    channel1 = channel_details(token1, data[channel_id])
    
    assert len(channel1['owner_members']) == 2
    assert channel1['owner_members'][1]['u_id'] == data2['u_id']
    assert channel1['owner_members'][1]['name_first'] == 'Mary'
    assert channel1['owner_members'][1]['name_last'] == 'Jones'

#*********************** removeowner test ***************************** 

def test_channel_removeowner(get_multiple_user):
    u_id0, token0, u_id1, token1 = get_multiple_user
    data = channels_create(token0, 'My channel', True)
    channel_invite(token0, data['channel_id'], u_id1)
    channel_addowner(token0, data['channel_id'], u_id1)
    channel_removeowner(token0, data['channel_id'], u_id1)
    channel1 = channel_details(token1, data[channel_id])
    
    assert len(channel1['owner_members']) == 1

def test_removeowner_invalid_channel_id(get_multiple_user):
    u_id0, token0, u_id1, token1 = get_multiple_user
    data = channels_create(token0, 'My channel', True) 
    channel_invite(token0, data['channel_id'], u_id1)
    channel_addowner(token0, data['channel_id'], u_id1)
    with pytest.raises(InputError) as e:
       channel_removeowner(token0, 'invalid_channel_id', u_id1)   

def test_removeowner_not_owner(get_multiple_user):
    u_id0, token0, u_id1, token1 = get_multiple_user
    data = channels_create(token0, 'My channel', True) 
    channel_invite(token0, data['channel_id'], u_id1)
    with pytest.raises(InputError) as e:
        channel_removeowner(token0, data['channel_id'], u_id1)  

def test_removeowner_invalid_access_member(get_multiple_user):
    u_id0, token0, u_id1, token1 = get_multiple_user
    data = channels_create(token0, 'My channel', True)
    channel_invite(token0, data['channel_id'], u_id1) 
    with pytest.raises(AccessError) as e:
        channel_removeowner(token1, data['channel_id'], u_id0) 

def test_removeowner_invalid_access(get_multiple_user):
    u_id0, token0, u_id1, token1 = get_multiple_user
    data = channels_create(token0, 'My channel', True)
    with pytest.raises(AccessError) as e:
        channel_removeowner(token1, data['channel_id'], u_id0)

def test_channel_removeowner_sowner(get_multiple_user):
    ## check if the owner of slackr can remove an owner even not in the channel
    u_id0, token0, u_id1, token1 = get_multiple_user
    data = channels_create(token1, 'My channel', True)
    data2 = auth_register('data2@unsw,edu.au', 'testPassword', 'Mary', 'Jones')
    channel_invite(token1, data['channel_id'], data2['u_id'])
    channel_addowner(token1, data['channel_id'], data2['u_id'])
    channel_removeowner(token0, data['channel_id'], u_id1)
    channel1 = channel_details(token1, data[channel_id])
    
    assert len(channel1['owner_members']) == 1 
    assert channel1['owner_members'][0]['u_id'] == data2[u_id]
    assert channel1['owner_members'][0]['name_first'] == 'Mary'
    assert channel1['owner_members'][0]['name_first'] == 'Jones'      

#*********************** messages test ***************************** 

def test_channel_massages(get_multiple_user):
    u_id0, token0, u_id1, token1 = get_multiple_user
    data = channels_create(token0, 'My channel', True)
    for message in range(50):
        message_send(token0, data['channel_id'], "This is message " + str(message))
    messages_dict = channel_messages(token0, data['channel_id'], 0)
    
    assert messages_dict['start'] == 0
    assert messages_dict['end'] == 50
    assert messages_dict['messages'][0]['messages'] == 'This is message 49'
    assert messages_dict['messages'][50]['messages'] == 'This is message 0'

def test_channel_massages_less_50(get_multiple_user):
    u_id0, token0, u_id1, token1 = get_multiple_user
    data = channels_create(token0, 'My channel', True)
    for message in range(30):
        message_send(token0, data['channel_id'], "This is message " + str(message))
    messages_dict = channel_messages(token0, data['channel_id'], 0)
    
    assert messages_dict['start'] == 0
    assert messages_dict['end'] == -1
    assert messages_dict['messages'][0]['messages'] == 'This is message 29'
    assert messages_dict['messages'][30]['messages'] == 'This is message 0'

def test_channel_massages_more_50(get_multiple_user):
    u_id0, token0, u_id1, token1 = get_multiple_user
    data = channels_create(token0, 'My channel', True)
    for message in range(80):
        message_send(token0, data['channel_id'], "This is message " + str(message))
    messages_dict = channel_messages(token0, data['channel_id'], 50)
    
    assert messages_dict['start'] == 50
    assert messages_dict['end'] == -1
    assert messages_dict['messages'][0]['messages'] == 'This is message 79'
    assert messages_dict['messages'][29]['messages'] == 'This is message 50'    

def test_channel_massages_multiple_senders(get_multiple_user):
    u_id0, token0, u_id1, token1 = get_multiple_user
    data = channels_create(token0, 'My channel', True)
    channel_invite(token1, data[channel_id], u_id1)
    for message in range(25):
        message_send(token0, data['channel_id'], "This is message " + str(message))
    for message_1 in range(10):
        message_send(token0, data['channel_id'], "This is message " + str(message_1 + 25))
    messages_dict = channel_messages(token0, data['channel_id'], 0)
    
    assert messages_dict['start'] == 0
    assert messages_dict['end'] == -1
    assert messages_dict['messages'][0]['u_id'] == u_id1
    assert messages_dict['messages'][0]['messages'] == 'This is message 34'
    assert messages_dict['messages'][34]['u_id'] == u_id0
    assert messages_dict['messages'][34]['messages'] == 'This is message 0'

def test_massages_invalid_channel_id(get_multiple_user):
    u_id0, token0, u_id1, token1 = get_multiple_user
    data = channels_create(token0, 'My channel', True)
    for message in range(30):
        message_send(token0, data['channel_id'], "This is message " + str(message))
    with pytest.raises(InputError) as e:        
        channel_messages(token0, 'invalid_channel_id', 0)      
    
def test_massages_invalid_start(get_multiple_user):
    u_id0, token0, u_id1, token1 = get_multiple_user
    data = channels_create(token0, 'My channel', True)
    for message in range(30):
        message_send(token0, data['channel_id'], "This is message " + str(message))
    with pytest.raises(InputError) as e:        
        channel_messages(token0, 'invalid_channel_id', 50)

def test_messages_invalid_access(get_multiple_user):
    u_id0, token0, u_id1, token1 = get_multiple_user
    data = channels_create(token0, 'My channel', True)
    for message in range(30):
        message_send(token0, data['channel_id'], "This is message " + str(message))
    with pytest.raises(AccessError) as e:
        channel_messages(token1, data0['channel_id'], 0)
