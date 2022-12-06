from kivy.properties import StringProperty, ListProperty, DictProperty
from kivy.event import EventDispatcher
from kivy.uix.screenmanager import Screen
from components.friend_choice import FriendChoice
from components.chat_bubble import ChatBubble
from functools import partial
from kivy.clock import mainthread
from core.utils.mixins import (
    msg_received,
    msg_send_fail,
    connect_fail,
    post_connect,
    remote_fail
)
from core.utils.color import teal, pink_600
from core.utils.http import request
from kivy.lang.builder import Builder
import threading
from copy import copy

Builder.load_file('screens/chatscreen.kv')

class ChatManager(EventDispatcher):
    current_id = StringProperty()
    connections = ListProperty()

class ChatScreen(Screen):
    cookies = {}
    chat_manager = ChatManager()

    def on_enter(self, *args):
        """setup binding event, setup server, client manager
            setup UI
        """
        # store user credentials
        username = self.manager.user_credentials['username']
        self.ids.welcome.text = f'Welcome [color={teal}]{username}[/color]'
        
        friend_ids = self.manager.friends_chat.keys()
        for friend_id in friend_ids:
            choice = FriendChoice(text=friend_id)
            choice.on_press = partial(self.on_select, friend_id)
            self.ids.friend_list.add_widget(choice)

        # setup server thread
        server = self.manager.server
        client_manager = self.manager.client_manager
        self.setup_server(server)
        self.setup_client_manager(client_manager)
        
        # setup chat event
        self.chat_manager.bind(current_id=self.on_chat_switch)
        self.chat_manager.bind(connections=self.on_connections_event)
        server.start()
            
    def setup_server(self, server):
        """setup server event dispatcher"""
        friends_chat = self.manager.friends_chat
        if friends_chat:
            self.chat_manager.current_id = ''

        @server.register_event(msg_received)
        def add_msg_to_chat(friend_id, msg, **kwargs):
            self.on_receive_msg(friend_id, msg)
    
    def setup_client_manager(self, client_manager):
        
        @client_manager.register_event(msg_send_fail)
        def on_msg_fail(friend_id, **kwarg):
            self.on_sent_fail(friend_id)
            
        @client_manager.register_event(post_connect)
        def on_connect_success(friend_id, *args):
            self.on_connect_success(friend_id)
            
        @client_manager.register_event(connect_fail)
        def on_connect_fail(friend_id, *args):
            self.on_connect_fail(friend_id)
            
        @client_manager.register_event(remote_fail)
        def on_remote_fail(friend_id, *args):
            self.on_remote_fail(friend_id)

    def on_connections_event(self, *args):
        friend_id = self.chat_manager.current_id
        connections = self.chat_manager.connections
        button = self.ids.start_button
        
        if friend_id not in connections:
            button.text = 'Start chat'
        else: button.text = 'Connected'

    def on_chat_switch(self, chat_manager, friend_id):
        """
        """
        if not self.chat_manager.current_id == friend_id:
            return
        self.ids.chat_header.text = f'[color={pink_600}]{friend_id}[/color]'
        chats = self.manager.friends_chat[friend_id]
        chat_container = self.ids.chat
        chat_container.clear_widgets()
        
        for chat in chats:
            sender, msg = chat
            label = ChatBubble(text=msg, own=(sender=='self'))
            label.pos_hint = {'right': 1} if sender == 'self' else {'left': 1}
            chat_container.add_widget(label)

    def on_send_txt(self, message):
        """ add new message to screen, send msg through socket
        """
        if not self.chat_manager.current_id: return

        friend_id = self.chat_manager.current_id
        if friend_id not in self.chat_manager.connections:
            return

        client_manager = self.manager.client_manager
        client_manager.send_message(
            friend_id,
            message
            )
        self.manager.friends_chat[friend_id]\
            .append(('self', message))
        
        label = ChatBubble(text=message)
        label.pos_hint = {'right': 1}
        self.ids.chat.add_widget(label)

    def on_select(self, friend_id):
        self.chat_manager.current_id = friend_id

    def on_start_chat(self):
        # request BE to return friend new address
        # friend_id = copy(self.chat_manager.current_id)
        friend_id = self.chat_manager.current_id
        if not friend_id: 
            return
        def get_friend_address():
            url = f'http://localhost/p2p_chatapp/getfriendaddress.php/?friend={friend_id}'
            response = request.get(url)
            self.on_start_chat_response(response, friend_id)
            
        threading.Thread(target=get_friend_address).start()

    def on_add_friend(self, friend_id):
        
        def add_friend():
            url='http://localhost/p2p_chatapp/addfriend.php/'
            payload = {'friend': friend_id}
            print(request.cookies)
            response = request.post(url, data=payload)
            
            self.on_add_friend_response(response, friend_id)
            
        threading.Thread(target=add_friend).start()
        
    @mainthread
    def on_connect_success(self, friend_id):
        current_id = self.chat_manager.current_id
        if current_id == friend_id:
            self.ids.start_button.text='Connected'
        self.chat_manager.connections.append(friend_id)

    @mainthread
    def on_connect_fail(self, friend_id):
        current_id = self.chat_manager.current_id
        if current_id == friend_id:
            self.ids.start_button.text='Retry'
        
    @mainthread
    def on_remote_fail(self, friend_id):
        current_id = self.chat_manager.current_id
        connections = self.chat_manager.connections
        if current_id == friend_id:
            self.ids.start_button.text='Retry'
        if friend_id in connections:
            connections.remove(friend_id)
            
    @mainthread
    def on_add_friend_response(self, response, friend_id):
        if response.status_code == 400:
            pass
            return
            # already added
        if response.status_code == 404:
            pass
            return
            # friend not found
        self.manager.friends_chat[friend_id] = []
        choice = FriendChoice(text=friend_id)
        choice.on_press = partial(self.on_select, friend_id)
        self.ids.friend_list.add_widget(choice)

    @mainthread
    def on_start_chat_response(self, resp, friend_id):
        address = resp.json()['address'].split(',')
        if type(address[1]) == str:
            address[1] = int(address[1]) # string to int
        # self.chat_manager.connections.append(friend_id)
        address = tuple(address)
        self.manager.client_manager.new_connection(friend_id, address)
        
    @mainthread
    def on_sent_fail(self, friend_id):
        chat = self.manager.friends_chat[friend_id]
        i = None
        for i in reversed(range(len(chat))):
            if chat[i][0] == 'self': break
        del chat[i]

        to_delete = None
        labels = self.ids.chat.children
        for i in reversed(range(len(labels))):
            if labels[i].own:
                to_delete = labels[i]
                break
        del to_delete

    @mainthread
    def on_receive_msg(self, friend_id, msg):
        """ handle msg received outside mainthread, render messages
        """
        print(friend_id)
        if friend_id not in self.manager.friends_chat.keys():
            return

        self.manager.friends_chat[friend_id].append(('friend', msg))
        if not self.chat_manager.current_id == friend_id:
            return

        label = ChatBubble(text=msg, own=False)
        label.pos_hint = {'left': 1}
        self.ids.chat.add_widget(label)
