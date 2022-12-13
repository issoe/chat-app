import socket
import threading
import json
from utils.dispatcher import DispatcherMixin
from utils.events import Event, EVENTS_WITHOUT_BODY, FRIEND_EVENTS

CLOSE_KEY = ';.][.][.[;/.s;.cawew;.a'

class Client(DispatcherMixin):
    _actions = {
        Event.server_rejected: [],
        Event.server_aborted: [],

        Event.auth_fail: [],
        Event.auth_success: [],

        Event.friend_accept: [],
        Event.friend_request: [],
        Event.friend_oneline: [],
        Event.friend_offline: []
    }

    def __init__(self, mailbox_address, server_address=(socket.gethostname(), 8000)):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_address = server_address
        self._mailbox_address = mailbox_address
        self._connected = False

    def start(self):
        if not self._connected:
            raise Exception('Must connected to server to start')
        threading.Thread(target=self.listen_server_broadcast).start()

    def connect_server(self, token):
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
        

    def listen_server_broadcast(self):
        while True:
            try:
                payload = self._socket.recv(1024).decode('utf8')
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

        if resp_event in EVENTS_WITHOUT_BODY:
            self.dispatch_actions(resp_event)
        elif resp_event in FRIEND_EVENTS:
            self.dispatch_actions(resp_event, friend_id=data['friend_id'])
    
    def destroy_socket(self):
        self._socket.close()
    
    def new_socket(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    
    
client = Client(('127.0.0.1', 9480))
@client.register_event(Event.server_rejected)
def handle(detail):
    print(detail)
    pass
client.connect_server('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJleHAiOjE2NzkzNzYyMTEsInR5cGUiOiJhY2Nlc3MifQ.iXJ4GZ46suHT_JyiZJznAH8MWm3IbudG3jacbziFvF4')
# client.connect_server('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoyLCJleHAiOjE2Nzk0Nzg0MzksInR5cGUiOiJhY2Nlc3MifQ.lsRzgS7NDNnGJ1_eSQ1lKOoGF5zngmIgjejDMNZ-EoI')
client.start()
