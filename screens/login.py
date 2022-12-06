from kivy.uix.screenmanager import Screen
from kivy.network.urlrequest import UrlRequest
from kivy.lang.builder import Builder
from kivy.properties import BooleanProperty
from kivy.event import EventDispatcher
from kivy.clock import mainthread
from core.utils.http import request
import threading

Builder.load_file('screens/loginscreen.kv')

class LoadingTracker(EventDispatcher):
    value = BooleanProperty()

class LoginScreen(Screen):
    loading = LoadingTracker(value=False)
    mutex = threading.Lock()

    def on_enter(self, *args):
        # self.loading.value = False
        self.loading.bind(value=self.on_loading)

    def on_loading(self, lading_tracker, value):
        if value:
            self.ids.btn.text = 'Loading'
        else:
            self.ids.btn.text = 'Login'

    def login(self, username, password, widget=None):
        if self.loading.value: #disable button if loading
            return
        
        self.loading.value = True
        error_msg = self.ids.error_msg
        error_msg.text = ''

        if not username or not password:
            error_msg.text = '[color=#f87171]Input you credentials![/color]'
            self.loading.value = False
            return
        address = self.manager.server.get_address()
        def request_auth():
            # self.mutex.acquire()
            payload = {
                'username': username,
                'password': password,
                'ip': address[0],
                'port': str(address[1])
            }
            response = request.post(
                'http://localhost/p2p_chatapp/login.php/',
                data=payload,
            )

            self.on_response(username, password, response)

        threading.Thread(target=request_auth).start()

    @mainthread
    def on_response(self, username, password, response):
        
        if response.status_code >= 400:
            self.ids.error_msg.text = '[color=#f87171]Account not found![/color]'
            self.loading.value = False
            return

        self.manager.user_credentials = {
            'username': username,
            'password': password
        }

        friend_chat = self.manager.friends_chat

        data =  response.json()
        for friend in data:
            friend_chat[friend['clientname']] = []

        self.manager.transition.direction = 'left'
        self.manager.current = 'main'
        self.loading.value = False
        # 
        self.manager.client_manager.set_id(username)
