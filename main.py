from kivy.config import Config
Config.set('graphics', 'resizable', False)


import kivy
from kivy.app import App

from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.slider import Slider
from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.lang.builder import Builder
from kivy.uix.scrollview import ScrollView
from kivy.properties import ListProperty


clients = ["client_1", "client_2", "client_3", "client_4", "client_5", "client_6"]

# class Layout(Widget):
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)

#         # self.cols = 1

#         # lb = Label(text='What your name')
#         # self.add_widget(lb)

#         # self.inputText = TextInput(multiline=False)
#         # self.add_widget(self.inputText)

#         # self.btn = Button(text="this button")
#         # self.btn.bind(on_press=self.on_press_button)
#         # self.add_widget(self.btn)
#         layout = BoxLayout(spacing=10)
#         btn1 = Button(text='Hello', size_hint=(.7, 1))
#         btn2 = Button(text='World', size_hint=(.3, 1))
#         layout.add_widget(btn1)
#         layout.add_widget(btn2)
        
#     def on_press_button(self, instance):
#         print("Text: " + self.inputText.text)


class ChatApp(App):
    clients = []
    name = []
    response = []
    
    def __init__(self, **kw):
        super(ChatApp, self).__init__(**kw)
        self.clients = ["client_1", "client_2", "client_3", "client_4", "client_5", "client_6",
                        "client_7", "client_8", "client_9", "client_10", "client_11", "client_12",
                        "client_13", "client_14"]
        self.response = ["response_1", "response_2", "response_3", "response_4", "response_5"]
        self.name = "thisname"    
        
    def build(self):
        Window.size = (600, 700)
        return Builder.load_file('box.kv')
    
    
    

    
    def on_press_button_send(self, inputFromUser):
        if not inputFromUser:
            print("Text: ")
        else:
            print("Text: " + inputFromUser)

    def on_press_button_choose_client(self, client):
        pass
        
    def on_press_button_add_client(self, client):
        pass
    
    def process(self):
        text = self.root.ids.input.text
        print(text)

if __name__ == '__main__':
    app = ChatApp()
    app.run()
