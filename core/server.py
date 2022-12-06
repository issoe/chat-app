import socket
import threading
from .utils.mixins import Dispatcher, CLOSE_KEY, BUFFER_SIZE
from .utils.mixins import (
    post_accept,
    post_disconnect,
    msg_received
)


class ServerPool(Dispatcher):
    
    def __init__(self, port=8000):
        host = socket.gethostbyname(socket.gethostname())

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.bind((host, 0))
        self._address = self._socket.getsockname()

        print(self._address)
        self._clients = {
            
        }
        self.mutex = threading.Lock()

        self.running = False
    
    def start(self):
        """server start listenning, wait for connection
        """
        self.running = True
        self._socket.listen()
        self.server_thread = threading.Thread(target=self.wait_to_connection, args=())
        self.server_thread.start()
        return self
    
    def get_address(self):
        return self._address

    def wait_to_connection(self):
        
        while True:
            client, client_address = self._socket.accept() # wait for new conection
            if not self.running:
                break
            # get user id from client.
            try:
                client.settimeout(0.001)
                friend_id = client.recv(1024).decode('utf8')
            except socket.timeout:
                client.close()
                print('client dont send his/her id')
                continue
            else:
                self.dispatch_actions(post_accept, friend_id)
                client.settimeout(None)
                self._clients[friend_id] = client
                threading.Thread(target=self.connection_accepted, args=(client, friend_id)).start()

        print(f'thread wait connection finish {threading.get_ident()}')

    def connection_accepted(self, client, friend_id):
        cli_side_error_reconizer = []
        while True:
            try:
                msg = client.recv(BUFFER_SIZE).decode('utf8')
            except Exception as e:  # client aborted
                self.dispatch_actions(post_disconnect)
                self.kill_client_connection(friend_id)
                break
            else:
                if msg == CLOSE_KEY or msg == '':
                    self.dispatch_actions(post_disconnect)
                    self.kill_client_connection(friend_id)
                    break
                # if not a Close request.
                self.dispatch_actions(msg_received, msg=msg, friend_id=friend_id, client_socket=client)

        print(f'thread accepted connection finish {threading.get_ident()}')

    def kill_client_connection(self, friend_id):
        self.mutex.acquire()

        client_socket = self._clients.pop(friend_id, None)
        if client_socket:
            # try:
                client_socket.close()
            # except: pass
        self.mutex.release()

    def disconnect_all(self):
        self.mutex.acquire()

        for friend_id in self._clients.keys():
            print(f'closing {friend_id}')
            self._clients[friend_id].close()

        self.mutex.release()
        self._clients = {}
    
    def stop_server(self):
        if self.running:
            self.running = False
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(self._address)
            self._socket.close()
