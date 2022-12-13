import socket
import threading
import json
from .utils.mixins import DispatcherMixin
from .utils.events import Event, EVENTS_WITHOUT_BODY, FRIEND_EVENTS

CLOSE_KEY = ';.][.][.[;/.s;.cawew;.a'

class Client(DispatcherMixin):
    _actions = {
        Event.server_rejected: [],
        Event.server_aborted: [],

        Event.auth_fail: [],
        Event.auth_success: [],

        Event.friend_accept: [],
        Event.friend_request: [],
        Event.friend_online: [],
        Event.friend_offline: []
    }

    def __init__(self, server_address=(socket.gethostname(), 8000)):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_address = server_address
        self._mailbox_address = None
        self._connected = False
    
    def set_mailbox_address(self, mailbox_addr):
        self._mailbox_address = mailbox_addr

    def start(self):
        if not self._connected:
            raise Exception('Must connected to server to start')
        threading.Thread(target=self.listen_server_broadcast).start()

    def connect_server(self, token):
        if not self._mailbox_address:
            raise Exception('Mailbox address have not set')
        try:
            self._socket.connect(self._server_address)
            self._socket.send(bytes(json.dumps({
                'bearer': token,
                'address': str(self._mailbox_address)
            }), 'utf8'))
            self._connected = True
        except Exception as e:
            self._connected = False
            self.dispatch_actions(Event.server_rejected)
    
    def is_connected(self):
        return self._connected

    def listen_server_broadcast(self):
        while True:
            try:
                payload = self._socket.recv(1024).decode('utf8')
                if not payload: 
                    raise
            except Exception as e:
                self._connected = False
                self.dispatch_actions(Event.server_aborted, detail=str(e))
                break
            else:
                response = json.loads(payload)
                self.handle_response(response)
    
    def handle_response(self, resp):
        resp_event = resp['event']
        data = resp['body']
        print('receive ',resp_event)

        if resp_event in EVENTS_WITHOUT_BODY:
            self.dispatch_actions(resp_event)
        elif resp_event in FRIEND_EVENTS:
            self.dispatch_actions(resp_event,fid=data['friend_id'])
        elif resp_event == Event.friend_request:
            self.dispatch_actions(resp_event, fid=data['friend_id'], 
                                  fusername=data['username'])
        elif resp_event == Event.friend_accept:
            self.dispatch_actions(resp_event, fid=data['friend_id'], 
                                fusername=data['username'])
    def destroy_socket(self):
        self._socket.close()
    
    def new_socket(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)