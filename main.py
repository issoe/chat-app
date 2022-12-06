from kivy.app import App
from kivy.core.window import Window
from kivy.core.window import Window
from kivy.graphics import *
from screens.login import LoginScreen
from screens.manager import AppScreenManager
from screens.chat import ChatScreen

class ChatApp(App):
    manageScreen = AppScreenManager()

    def build(self):
        Window.size = (1000, 600)
        self.manageScreen.add_widget(LoginScreen(name='login'))
        self.manageScreen.add_widget(ChatScreen(name='main'))
        return self.manageScreen

    def on_stop(self):
        self.manageScreen.server.disconnect_all()
        self.manageScreen.server.stop_server()
           
if __name__ == '__main__':
    app = ChatApp()
    app.run()