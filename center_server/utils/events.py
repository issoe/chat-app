

class Event:
    friend_online = 'FRIEND_ONLINE'
    friend_offline = 'FRIEND_OFFLINE'
    friend_request = 'FRIEND_REQUEST'
    friend_accept = 'FRIEND_ACCEPT'

    server_aborted = 'SERVER_ABORTED'
    server_rejected = 'SERVER_REJECTED'

    auth_fail = 'AUTH_FAIL'
    auth_success = 'AUTH_SUCCESS'

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