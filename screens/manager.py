from core.server import ServerPool
from core.client import ClientManager
from kivy.uix.screenmanager import ScreenManager



class AppScreenManager(ScreenManager):
    friends_chat = {}
    friend_addresses = {}
    user_credentials = {
        'username': None,
        'password': None
    }
    server = ServerPool()
    client_manager = ClientManager()