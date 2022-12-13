import socket
import threading
from .utils.mixins import DispatcherMixin, CLOSE_KEY, BUFFER_SIZE
from .utils.events import Event

class MailBox(DispatcherMixin):
    _actions = {
        Event.new_msg: [],
        Event.friend_aborted: [],
        Event.chat_accepted: [],
    }
    def __init__(self):

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
        """mailbox start listenning, wait for connection
        """
        self.running = True
        self._socket.listen()
        self.mailbox_thread = threading.Thread(target=self.wait_to_connection, args=())
        self.mailbox_thread.start()
        return self

    def get_address(self):
        return self._address

    def wait_to_connection(self):
        while True:
            client, _ = self._socket.accept() # wait for new conection
            if not self.running:
                break
            # get user id from client.
            try:
                client.settimeout(0.1)
                fid = client.recv(1024).decode('utf8')
                if fid in self._clients:
                    print('already connected')
                    raise Exception('client connected')
            except (socket.timeout, Exception):
                client.close()
                print('client dont send his/her id')
                continue
            else:
                client.settimeout(None)
                self.dispatch_actions(Event.chat_accepted, fid=fid)
                self._clients[fid] = client
                threading.Thread(target=self.connection_accepted, args=(client, fid)).start()

        print(f'thread wait connection finish {threading.get_ident()}')

    def connection_accepted(self, client, fid):
        while True:
            try:
                msg = client.recv(BUFFER_SIZE).decode('utf8')
            except Exception as e:  # client aborted
                print(e)
                self.dispatch_actions(Event.friend_aborted, fid=fid)
                self.kill_client_connection(fid)
                break
            else:
                if msg == CLOSE_KEY:
                    self.dispatch_actions(Event.friend_aborted, fid=fid)
                    self.kill_client_connection(fid)
                    break
                # if not a Close request.
                self.dispatch_actions(Event.new_msg, msg=msg, fid=fid)

        print(f'thread accepted connection finish {threading.get_ident()}')

    def kill_client_connection(self, fid):
        self.mutex.acquire()

        client_socket = self._clients.pop(fid, None)
        if client_socket:
            # try:
                client_socket.close()
            # except: pass
        self.mutex.release()

    def disconnect_all(self):
        self.mutex.acquire()

        for fid in self._clients.keys():
            print(f'closing {fid}')
            self._clients[fid].close()

        self.mutex.release()
        self._clients = {}
    
    def stop_mailbox(self):
        if self.running:
            self.running = False
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(self._address)
            self._socket.close()

if __name__ == '__main__':
    mailbox = MailBox()
    print(mailbox.get_address())
    @mailbox.register_event(Event.new_msg)
    def handle_incoming_msg(msg, fid, *args, **kwargs):
        print(fid, ': ', msg)