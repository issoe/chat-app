import threading

pre_close = 'PRE_CLOSE'
post_close = 'POST_CLOSE'
post_accept = 'POST_ACCEPT'
msg_received = 'MSG_RECEIVED'
post_disconnect = 'POST_DISCONNECT'
msg_sent = 'MSG_SENT'
post_connect = 'POST_CONNECT'
connect_fail = 'CONNECT_FAIL'
msg_send_fail = 'SEND_FAIL'
pre_connect = 'PRE_CONNECT'
remote_fail = 'REMOTE_FAIL'

class Dispatcher():
    _actions = {
        pre_close: [],
        post_close: [],
        post_accept: [],
        pre_connect: [],
        post_connect: [],
        post_disconnect: [],
        msg_sent: [],
        msg_received: [],
        connect_fail: [],
        msg_send_fail: [],
        remote_fail: []
    }
    mutex = threading.Lock()
        # chil class must have self._actions = {{action_type}: [], ...} - dict
    def dispatch_actions(self, action_type, *args, **kwargs):
        print(f'{action_type} callback with: {args} and {kwargs}')
        self.mutex.acquire()
        for action in self._actions[action_type]:
            action(*args, **kwargs)
        self.mutex.release()
        
    def register_event(self, action_type):
        def decorator(function):
                self._actions[action_type].append(function)
        return decorator

CLOSE_KEY = '*./,/.{quit}*'
BUFFER_SIZE = 1024