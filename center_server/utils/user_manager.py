import socket
import json
import threading
from mysql.connector import Error as db_Error
from . import db
from .tokens import (
    JWT_ALGORITHM,
    JWT_SECRET,
    JWT_EXP_DELTA_SECONDS,
    get_user_from_token
)
from .events import Event



def get_client_request(client, timeout, is_json):
    if  timeout:
        client.settimeout(timeout)
    try:
        request = client.recv(1024).decode('utf8')
    except socket.timeout:
        raise socket.timeout('User dont send credentials')
    except Exception as e:
        client.settimeout(None)
        raise Exception(str(e))
    client.settimeout(None)
    if is_json:
        return json.loads(request)
    return request

def create_response(event, detail='', body={}):
    return {
        'event': event,
        'detail': detail,
        'body': body
    }

def send_json(client, json_data):
    client.send(bytes(json.dumps(json_data), 'utf8'))

class UserManager():

    def __init__(self, port=8000):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.bind((socket.gethostname(), port))
        self._address = self._socket.getsockname()

        self._users = {} # {user_id: {socket, address}}
        self._mutex = threading.Lock()
    
    def start(self):
        self._socket.listen()
        threading.Thread(target=self.reception, args=()).start()

    def reception(self):
        while True:
            client, _ = self._socket.accept()
            try:
                request = get_client_request(client, is_json=True, timeout=1)
                token = request['bearer']
                user_address = request['address']
                user = get_user_from_token(token)
                uid = user['id']
                print(user)

                if self.is_logged_in(uid):
                    raise Exception('User is logged in from some where')

                resp = create_response(event=Event.auth_success)
                send_json(client, resp)
                threading.Thread(target=self.accept_user, args=(uid, user_address, client)).start()

            except Exception as e:
                print(e)
                try:
                    resp = create_response(
                        event=Event.auth_fail,
                        detail=str(e)
                        )
                    send_json(client, resp)
                except Exception as e: 
                    print(e)
                finally:
                    client.close()
    
    def accept_user(self, uid, user_address, client):
        self._users[uid] = {
            'socket': client,
            'address': user_address
        }

        try:
            friends = db.get_user_friends(uid)
            fids = map(lambda friend: friend['id'], friends)
            noti = create_response(
                event=Event.friend_online,
                body={'friend_id': uid}
            )
            self.broadcast(fids, noti)
            threading.Thread(target=self.track_user, args=(client, uid)).start()
            
        except db_Error as e:
            print(e)
            pass

    def broadcast(self, ids, json_data):
        self._mutex.acquire()
        aborted_users = []
        for uid in ids:
            if uid in self._users.keys():
                try:
                    send_json(self._users[uid]['socket'], json_data)
                except Exception as e:
                    print(e)
                    aborted_users.append(uid)

        for uid in aborted_users:
            self.disconnect_user(uid)

        self._mutex.release()
        
    def disconnect_user(self, uid):
        user = self._users.pop(uid, None)
        if user:
            user['socket'].close()

    def is_logged_in(self, uid):
        if uid in self._users.keys():
            return True
        return False
    
    def track_user(self, client, uid):
        # Wait until user disconnected
        try: # Blocking
            client.recv(1024)
        except: pass
        self.disconnect_user(uid)

        try:
            friends = db.get_user_friends(uid)
       
            fids = map(lambda friend: friend['id'], friends)
            noti = create_response(
                event=Event.friend_offline,
                body={'friend_id': uid}
            )
            self.broadcast(fids, noti)
        except db_Error:
            return

    def send(self, uid, json_data):
        user = self._users.get(int(uid), None)
        if not user:
            print('not user')
            return False
        try:
            send_json(user['socket'], json_data)
            print('sended')
        except Exception as e:
            print(e)
            # User aborted
            self.disconnect_user(uid)
            return False

    def address_of(self, uid):
        user = self._users.get(int(uid), None)
        if not user:
            return None
        return user['address']

    def get_online_user(self):
        return list(self._users.keys())
        pass

if __name__ == '__main__': 
    manager = UserManager()
    manager.start()