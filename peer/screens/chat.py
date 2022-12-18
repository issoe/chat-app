from kivy.properties import StringProperty, ListProperty
from kivy.event import EventDispatcher
from kivy.uix.screenmanager import Screen
from components.friend_choice import FriendChoice
from components.chat_bubble import ChatBubble
from components.modal import FriendRequestModal
from functools import partial
from kivy.clock import mainthread
from core.utils.color import teal, pink_600, zinc_800
from core.utils.http import request
from kivy.lang.builder import Builder
from core.utils.events import Event
from .fetchs import FriendAPI
import threading
from ast import literal_eval as make_tuple
from kivy.utils import get_color_from_hex


Builder.load_file('screens/chatscreen.kv')

class ChatManager(EventDispatcher):
    current_id = StringProperty()
    connections = ListProperty()

class ChatScreen(Screen, FriendAPI):
    chat_manager = ChatManager()
    friends_chat = {
        # friendid : {
        #    'is_online': True
        #    'username': ...,
        #    'chats': ... 
        # }
    }
    modal = None
    def __init__(self, **kw):
        super().__init__(**kw)
        self.modal = FriendRequestModal(
            handle_accept=self.handle_accept_friend,
            handle_add_friend=self.handle_add_friend
            )

    def handle_accepted_friend(self, fid, username, is_online):
        choice = FriendChoice(
            text=username,
            fid=str(fid),
            name=username
            )
        if is_online:
            choice.background_color = get_color_from_hex(teal)
        else:
            choice.background_color = get_color_from_hex(zinc_800)
        choice.on_press = partial(self.button_select_friend, fid)
        self.ids.friend_list.add_widget(choice)
        self.friends_chat[str(fid)] = {
            'username': username,
            'chats': []
        }

    def on_enter(self, *args):
        """setup binding event, setup mailbox, client manager
            setup UI
        """
        # store user credentials
        username = self.manager.user_credentials['username']
        self.ids.welcome.text = f'Welcome [color={teal}]{username}[/color]'
        # Fetch and show friend_list 
        self.fetch_friends()
        self.fetch_friend_requests()

        # setup mailbox thread
        self.setup_mailbox()
        self.setup_postman_manager()
        self.setup_client()
        
        # setup chat event
        self.chat_manager.bind(current_id=self.track_chat_switch)
        self.chat_manager.bind(connections=self.track_connections_event)
    
    def setup_client(self):
        client = self.manager.client

        @client.register_event(Event.friend_online)
        def friend_online(fid):
            print('register online friend', fid)
            self.on_friend_online(str(fid))

        @client.register_event(Event.friend_offline)
        def friend_offline(fid):
            print('register offline friend', fid)
            self.on_friend_offline(str(fid))
            
        @client.register_event(Event.friend_request)
        def add_friend_request(fid, fusername):
            self.on_friend_request(str(fid), fusername)
        @client.register_event(Event.friend_accept)
        def friend_accepted_request(fid, fusername):
            self.on_friend_accepted_request(str(fid), fusername)

        credentials = self.manager.user_credentials
        mailbox = self.manager.mailbox
        client.set_mailbox_address(mailbox.get_address())
        client.connect_server(credentials['token'])
        client.start()
            
    def setup_mailbox(self):
        """setup mailbox event dispatcher"""
        mailbox = self.manager.mailbox
        @mailbox.register_event(Event.friend_aborted)
        def friend_aborted(fid):
            self.on_friend_aborted(fid)
        @mailbox.register_event(Event.new_msg)
        def on_received_msg(fid, msg):
            self.on_receive_msg(fid, msg)

        mailbox.start()

    def setup_postman_manager(self):
        postman_manager = self.manager.postman_manager
        @postman_manager.register_event(Event.chat_accepted)
        def chat_accepted(fid):
            self.on_chat_allowed(fid)
        @postman_manager.register_event(Event.msg_sent)
        def msg_sent(fid, msg):
            self.on_msg_sent(fid, msg)
        @postman_manager.register_event(Event.msg_sent_fail)
        def msg_sent_fail(fid):
            self.on_msg_sent_fail(fid)
        @postman_manager.register_event(Event.chat_rejected)
        def chat_rejected(fid):
            self.on_chat_rejected(fid)

    def track_connections_event(self, *args):
        friend_id = self.chat_manager.current_id
        connections = self.chat_manager.connections
        button = self.ids.start_button
        
        if friend_id not in connections:
            button.text = 'Start chat'
        else: button.text = 'Connected'

    def track_chat_switch(self, chat_manager, fid):
        """ on switch chat box
        """
        if not self.chat_manager.current_id == fid:
            return
        
        if str(fid) in self.chat_manager.connections:
            self.ids.start_button.text='Connected'
        else: 
            self.ids.start_button.text='Start chat'

        friend = self.friends_chat[fid]
        self.ids.chat_header.text = f"[color={pink_600}]{friend['username']}[/color]"
        chats = friend['chats']

        chat_container = self.ids.chat
        chat_container.clear_widgets()

        for chat in chats:
            sender, msg = chat
            label = ChatBubble(text=msg, own=(sender=='self'))
            label.pos_hint = {'right': 1} if sender == 'self' else {'left': 1}
            chat_container.add_widget(label)

    def input_send_txt(self, message):
        """ add new message to screen, send msg through socket
        """
        if not self.chat_manager.current_id: return

        fid = self.chat_manager.current_id
        if fid not in self.chat_manager.connections:
            return

        postman_manager = self.manager.postman_manager
        postman_manager.send_message(
            fid,
            message
            )
        self.friends_chat[fid]['chats']\
            .append(('self', message))
        
        label = ChatBubble(text=message)
        label.pos_hint = {'right': 1}
        self.ids.chat.add_widget(label)

    def button_select_friend(self, fid):
        self.chat_manager.current_id = fid

    def button_start_chat(self):
        # request BE to return friend new address
        # friend_id = copy(self.chat_manager.current_id)
        fid = self.chat_manager.current_id
        if not fid: 
            return
        def get_friend_address():
            url = f'http://127.0.0.1:5000/get_address?friend_id={fid}'
            response = request.get(url)
            self.on_start_chat_response(response, fid)
        threading.Thread(target=get_friend_address).start()

    def button_open_frequests_modal(self):
        self.modal.open()

    # client event
    @mainthread
    def on_friend_online(self, fid):
        print('online', fid)
        for choice in self.ids.friend_list.children:
            if str(choice.fid) == str(fid):
                choice.background_color = get_color_from_hex(teal)
    @mainthread
    def on_friend_offline(self, fid):
        print('offline', fid)
        
        if fid == self.chat_manager.current_id:
            self.ids.start_button.text='Retry'

        for choice in self.ids.friend_list.children:
            if str(choice.fid) == str(fid):
                choice.background_color = get_color_from_hex(zinc_800)
        
    @mainthread
    def on_friend_request(self, fid, fusername):
        print(fusername)
        self.modal.add_request(fid, fusername) 
    @mainthread
    def on_friend_accepted_request(self, fid, fusername):
        print(fusername)
        choice = FriendChoice(
            text=fusername,
            fid=str(fid),
            name=fusername
        )
        choice.on_press = partial(self.button_select_friend, fid)
        choice.background_color =  get_color_from_hex(teal)
        self.ids.friend_list.add_widget(choice)
        self.friends_chat[fid] = {
            'username': fusername,
            'chats': []
        }

    # postman event
    @mainthread
    def on_chat_allowed(self, fid):
        current_id = self.chat_manager.current_id
        if current_id == fid:
            self.ids.start_button.text='Connected'
        self.chat_manager.connections.append(fid)

    @mainthread
    def on_endchat(self, friend_id):
        current_id = self.chat_manager.current_id
        connections = self.chat_manager.connections

        if current_id == friend_id:
            self.ids.start_button.text='Retry'
        if friend_id in connections:
            connections.remove(friend_id)
    @mainthread
    def on_msg_sent(self, fid, msg):
        pass
    @mainthread
    def on_msg_sent_fail(self, fid):
        chats = self.friends_chat[fid]['chats']
        pos = None
        for i in reversed(range(len(chats))):
            if chats[i][0] == 'self': 
                pos = i
                break
        if pos:
            del chats[i]

        to_delete = None
        labels = self.ids.chat.children
        for i in reversed(range(len(labels))):
            if labels[i].own:
                to_delete = labels[i]
                break
        if to_delete:
            del to_delete
    @mainthread
    def on_chat_rejected(self, friend_id):
        current_id = self.chat_manager.current_id
        if current_id == friend_id:
            self.ids.start_button.text='Retry'
    # Http response of add friend

    @mainthread
    def on_start_chat_response(self, resp, friend_id):
        if resp.status_code == 400:
            # Handle later
            return

        self.chat_manager.connections.append(friend_id)
        address = make_tuple(resp.json()['address'])
        address = tuple(address)
        self.manager.postman_manager.new_connection(friend_id, address)
        
    # mailbox event
    @mainthread
    def on_receive_msg(self, fid, msg):
        """ handle msg received outside mainthread, render messages
        """
        print(fid, msg, 'received')
        print(self.friends_chat.keys())
        if fid not in self.friends_chat.keys():
            return

        print('adding to chat')
        self.friends_chat[fid]['chats'].append(('friend', msg))
        if not self.chat_manager.current_id == fid:
            return

        print('adding text to screen')
        label = ChatBubble(text=msg, own=False)
        label.pos_hint = {'left': 1}
        self.ids.chat.add_widget(label)

    @mainthread
    def on_friend_aborted(self, fid): 
        pass