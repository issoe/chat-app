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

        self.response = ["Other: Hello!", "You: Hi!",
                         "Other: How are you?", "You: I'm fine. Thank you, and you?", "Other: I'm fine <3"]

    def build(self):
        Window.size = (600, 700)
        Builder.load_file('layout.kv')
        manageScreen = ScreenManager()
        manageScreen.add_widget(LoginPage(name='login'))
        manageScreen.add_widget(MainPage(name='main'))
        
        Clock.schedule_interval(self.update, 1)
        return manageScreen

    def on_press_button_send(self, inputFromUser):
        if not inputFromUser:
            print("You: ")
        else:
            self.response.append("You: " + inputFromUser)
            print(self.response)

    def on_press_button_choose_client(self, client):
        print("Client: " + client)

    def tester(self):
        pass
    
    def createGrid(self, *args):
        pass

    def myButtPress(self, butt):
        print(butt.text)
        self.popup.dismiss()
    
    def on_press_button_add_client(self, client):
        pass
    
    def update(self, *args):
        pass
    #     self.name.text = str(self.current_i)
    #     self.current_i += 1
    #     if self.current_i >= 50:
    #         Clock.unschedule(self.update)
    
    def refresh_callback(self, *args):
        """A method that updates the state of your application
        while the spinner remains on the screen."""

        def refresh_callback(interval):
            self.root.ids.box.clear_widgets()
            if self.x == 0:
                self.x, self.y = 15, 30
            else:
                self.x, self.y = 0, 15
            self.set_list()
            self.root.ids.refresh_layout.refresh_done()
            self.tick = 0

        Clock.schedule_once(refresh_callback, 1)
            
if __name__ == '__main__':
    app = ChatApp()
    app.run()
