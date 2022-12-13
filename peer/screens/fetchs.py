import threading
from kivy.clock import mainthread
from core.utils.http import request
from components.friend_choice import FriendChoice
from functools import partial
from kivy.utils import get_color_from_hex
from kivy.clock import Clock
from core.utils.color import teal, zinc_800

class FriendAPI:
    
    def fetch_friends(self):
        """Fetch friendlist api
        """
        def get_friend_list():
            response = request.get('http://127.0.0.1:5000/friend_list')
            self.friend_list_resp(response)
        threading.Thread(target=get_friend_list).start()
    
    def fetch_friend_requests(self):
        def get_friend_requests():
            response = request.get('http://127.0.0.1:5000/friend_requests')
            self.friend_requests_resp(response)
        threading.Thread(target=get_friend_requests).start()

    def handle_add_friend(self, text):
        if not text:
            return
        def add_friend():
            response = request.post(
                'http://127.0.0.1:5000/add_friend',
                data={'fusername': text}
            )
            self.add_friend_resp(response)
        threading.Thread(target=add_friend).start()

    @mainthread
    def add_friend_resp(self, resp):
        if resp.status_code >= 400:
            return

    @mainthread
    def friend_requests_resp(self, resp):
        data = resp.json()
        frequests = data['requests']
        print(frequests)
        for request in frequests:
            fid = str(request['id'])
            fusername = request['username']
            self.modal.add_request(fid, fusername)

    @mainthread
    def friend_list_resp(self, resp):

        """set friends chat"""
        data = resp.json()
        friends = data['friends']
        for friend in friends:
            fid = friend['id']
            fusername = friend['username']
            is_online = friend['is_online']
            self.friends_chat[str(fid)] = {
                'username': fusername,
                'is_online': is_online,
                'chats': []
            }
        for fid, friend in self.friends_chat.items():
            choice = FriendChoice(
                text=friend['username'],
                fid=str(fid),
                name=friend['username']
                )
            if friend['is_online']:
                choice.background_color = get_color_from_hex(teal)
            else:
                choice.background_color = get_color_from_hex(zinc_800)
            choice.on_press = partial(self.button_select_friend, fid)
            self.ids.friend_list.add_widget(choice)

    def handle_accept_friend(self, fid, username):
        self.modal.remove_request(fid)
        def accept_request():
            response = request.put(
                'http://127.0.0.1:5000/accept_friend',
                data={'friend_id': fid})
            self.accept_friend_resp(fid, username, response)
        threading.Thread(target=accept_request).start()

    @mainthread
    def accept_friend_resp(self, fid, username, resp):
        print(fid, username, resp)
        if resp.status_code >= 400:
            return
        resp = resp.json()
        is_online = resp['is_online']
        self.handle_accepted_friend(fid, username, is_online)
        
    