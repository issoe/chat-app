
class Event:
    # listen to server event 
    friend_online = 'FRIEND_ONLINE'
    friend_offline = 'FRIEND_OFFLINE'
    friend_request = 'FRIEND_REQUEST'
    friend_accept = 'FRIEND_ACCEPT'

    server_aborted = 'SERVER_ABORTED'
    server_rejected = 'SERVER_REJECTED'

    auth_fail = 'AUTH_FAIL'
    auth_success = 'AUTH_SUCCESS'

    # mailbox event
    friend_aborted = 'FRIEND_ABORTED'
    new_msg = 'NEW_MSG'

    # postman event
    msg_sent = 'MSG_SENT'
    msg_sent_fail = 'MSG_SENT_FAIL'
    end_chat = 'END_CHAT'
    chat_rejected = 'CHAT_REJECTED'

    # mailbox and postman
    chat_accepted = 'CHAT_ACCEPTED'

EVENTS_WITHOUT_BODY = [
    Event.auth_fail, 
    Event.auth_success, 
    Event.server_aborted, 
    Event.server_rejected
]

FRIEND_EVENTS = [
    Event.friend_offline,
    Event.friend_online,
]

