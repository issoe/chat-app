import socket
import threading
from .utils.mixins import DispatcherMixin, CLOSE_KEY
from .utils.events import Event



class PostmanManager(DispatcherMixin):
    _actions = {
        Event.chat_accepted: [],
        Event.msg_sent: [],
        Event.msg_sent_fail: [],
        Event.end_chat: [],
        Event.chat_rejected: [],
    }
    def __init__(self) -> None:
        self._connections = {}  # {fid: {socket, server_address}}
        self.mutex = threading.Lock()
        self.id = None
        
    def set_id(self, id):
        self.id = str(id)
        
    def new_connection(self, fid, address):
        if not self.id:
            raise Exception('Id not set')
        if fid in self._connections:
            return
        threading.Thread(
            target=self._start_new_connection,
            args=(fid, address)).start()

    def _start_new_connection(self, fid, address):
        """address = (host, port)"""
        sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sk.connect(address)
            sk.send(bytes(self.id, 'utf8'))
            self._connections[fid] = \
                self.connection_as_dict(sk, address)
            self.dispatch_actions(Event.chat_accepted, fid=fid)
        except Exception as e:
            print('start_new_connection exception', e)
            self.dispatch_actions(Event.chat_rejected, fid=fid)
    
    def connection_as_dict(self, socket, server_address):
        return {
            'socket': socket,
            'server_address': server_address
        }
    def send_message(self, fid, msg):
        threading.Thread(
            target=self._send_message,
            args=(fid, msg)).start()
    
    def _send_message(self, fid, msg):
        connection = self._connections.get(fid, None)
        print(connection)
        if connection:
            try:
                connection['socket'].send(bytes(msg, 'utf8'))
                self.dispatch_actions(Event.msg_sent, fid=fid, msg=msg)
                return True
            except Exception as e:
                print('send fail:', e)
                self.dispatch_actions(Event.msg_sent_fail, fid=fid)
                self.close_connection(fid)
                
        self.dispatch_actions(Event.msg_sent_fail, fid=fid)
        return False

    def close_connection(self, fid):
        connection = self._connections.pop(fid, None)
        if connection:
            try:
                connection['socket'].send(bytes(CLOSE_KEY, 'utf8'))
                connection['socket'].close()
            except: pass
        self.dispatch_actions(Event.end_chat, fid=fid)

    def disconnect_all(self):
        for connection in self._connections:
            try: # if server socket not close
                connection['socket'].send(bytes(CLOSE_KEY, 'utf8'))
                connection['socket'].close()
            except: pass
        self._connections = {}

