import socket
import threading
from .utils.mixins import Dispatcher, CLOSE_KEY
from .utils.mixins import (
    post_close,
    msg_sent,
    post_connect,
    connect_fail,
    msg_send_fail,
    pre_connect,
    remote_fail
)

class ClientManager(Dispatcher):
    def __init__(self, id=2) -> None:
        self._connections = {}  # {friend_id: {socket, server_address}}
        self.mutex = threading.Lock()
        self.id = id
        
    def set_id(self, id):
        self.id = id
        
    def new_connection(self, friend_id, address):
        threading.Thread(
            target=self._start_new_connection,
            args=(friend_id, address)).start()

    def _start_new_connection(self, friend_id, address):
        """address = (host, port)"""
        self.dispatch_actions(pre_connect, friend_id, address)

        sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sk.connect(address)
            sk.send(bytes(str(self.id), 'utf8'))
            self.mutex.acquire()
            self._connections[friend_id] = \
                self.connection_as_dict(sk, address)
            self.mutex.release()
            self.dispatch_actions(post_connect, friend_id)
            
        except Exception as e:
            print('start_new_connection exception', e)
            self.dispatch_actions(connect_fail, friend_id)
    
    def connection_as_dict(self, socket, server_address):
        return {
            'socket': socket,
            'server_address': server_address
        }
    def send_message(self, friend_id, msg):
        threading.Thread(
            target=self._send_message,
            args=(friend_id, msg)).start()
    
    def _send_message(self, friend_id, msg):
        connection = self._connections.get(friend_id, None)
        if connection:
            try:
                connection['socket'].send(bytes(msg, 'utf8'))
                self.dispatch_actions(msg_sent, friend_id=friend_id, msg=msg)
                return True
            except:
                self.dispatch_actions(remote_fail, friend_id)
                self.close_connection(self, friend_id)
                
        self.dispatch_actions(msg_send_fail, friend_id)
        return False

    def close_connection(self, friend_id):
        connection = self._connections.pop(friend_id, None)
        if connection:
            try:
                connection['socket'].send(bytes(CLOSE_KEY, 'utf8'))
                connection['socket'].close()
            except: pass
        self.dispatch_actions(post_close)

    def disconnect_all(self):
        for connection in self._connections:
            try: # if server socket not close
                connection['socket'].send(bytes(CLOSE_KEY, 'utf8'))
                connection['socket'].close()
            except: pass
        self._connections = {}

