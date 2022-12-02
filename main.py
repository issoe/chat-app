from kivy.config import Config
Config.set('graphics', 'resizable', False)

import kivy
from kivy.app import App
from kivy.properties import ListProperty
from kivy.uix.scrollview import ScrollView
from kivy.lang.builder import Builder
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.lang import Builder
from kivy.uix.slider import Slider
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.uix.list import OneLineListItem
# from kivy.properties import ObjectProperty
from kivy.factory import Factory
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.clock import Clock


class MainPage(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)    

    def tester(self):
        pass

class LoginPage(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def validate_user(self):
        user = self.ids.username_field
        pwd = self.ids.pwd_field
        info = self.ids.info

        uname = user.text
        passwd = pwd.text

        if uname == '' or passwd == '':
            info.text = '[color=#FF0000]Username and Password are required[/color]'
            return 0
        else:
            if uname == 'admin' and passwd == 'admin':
                info.text = '[color=#00FF00]Logged in successfully!!![/color]'
                return 1
            else:
                info.text = '[color=#FF0000]Invalid Username and Password[/color]'
                return -1


class ChatApp(App):
    clients = []
    name = []
    response = []

    def __init__(self, **kw):
        super(ChatApp, self).__init__(**kw)
        self.clients = ["client_1", "client_2", "client_3", "client_4", "client_5", "client_6",
                        "client_7", "client_8", "client_9", "client_10", "client_11", "client_12",
                        "client_13", "client_14"]

        self.response = ["Other: Hello!", 
                         "You: Hi!",
                         "Other: How are you?", 
                         "You: I'm fine. Thank you, and you?", 
                         "Other: I'm fine <3"]

    def build(self):
        Window.size = (600, 700)
        Builder.load_file('layout.kv')
        manageScreen = ScreenManager()
        manageScreen.add_widget(LoginPage(name='login'))
        manageScreen.add_widget(MainPage(name='main'))
        
        return manageScreen

    def on_press_button_send(self, inputFromUser):
        if not inputFromUser:
            print("You: ")
        else:
            self.response.append("You: " + inputFromUser)
            print(self.response)

    def on_press_button_choose_client(self, client):
        print("Client: " + client)
    
    def on_press_button_add_client(self, client):
        pass
    
            
if __name__ == '__main__':
    app = ChatApp()
    app.run()
