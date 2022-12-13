from core.mailbox import MailBox 
from core.postman import PostmanManager
from core.client import Client
import socket
from kivy.uix.screenmanager import ScreenManager



class AppScreenManager(ScreenManager):
    user_credentials = {
        'username': None,
        'jwt': None
    }
    mailbox = MailBox()
    postman_manager = PostmanManager()
    client = Client((socket.gethostname(), 8000))
