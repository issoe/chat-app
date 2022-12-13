from kivy.uix.popup import ModalView
from kivy.lang.builder import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from functools import partial

Builder.load_string(
    """
<RequestChoice>:

    orientation: 'horizontal'
    size_hint_y: None
    size: 0, 40
    
    Label:
        id: username
        text: ''
        text_size: self.size
        font_size: 20        
        size_hint: 0.5, 1
        halign: "left"
        valign: "center"
        markup: True 
    BoxLayout:
        id: buttonwrapper
        orientation: "horizontal"
        size_hint_x: None
        size: 80, 0


<FriendRequestModal>:
    size_hint: None, None
    size: 500, 500
    padding: 10, 10
    canvas.before:  
        Color:
            rgb: utils.get_color_from_hex('#1c1917')   
        RoundedRectangle:  
            size: self.size  
            pos: self.pos  
            
    BoxLayout:
        orientation: 'vertical'
        spacing: 5
        padding: 20, 20
        Label:
            text: 'Friend requests'
            size_hint_y: None
            size: 0 , 50
            
        BoxLayout:
            id: search
            padding: [0, 10]
            size_hint_y: None
            size: 0, 70
            
            TextInput:            
                id: search_txt
                hint_text: 'New Friend ... '
                multiline: False

            Button:
                id: search_btn
                text: "Add"
                size_hint_x: None
                size: 100, 0
                color: (0,0,0)
                background_color: utils.get_color_from_hex('#fde68a')
                background_normal: ''
                on_release:
                    root.add_friend(search_txt.text)
    
        ScrollView:
            id: request_dropdown
            do_scroll_x: False
            do_scroll_y: True

            canvas.before:
                Color: 
                    rgba: utils.get_color_from_hex('#27272a')
                RoundedRectangle:
                    radius: 15,
                    pos: self.pos
                    size: self.size
        
            GridLayout:
                id:request_list 
                cols: 1
                pos: 0, 0
                size_hint_y: None
                height: 1000
                spacing: 10
                padding: 15, 15
                height: self.minimum_height

    """
)

class RequestChoice(BoxLayout):
    def __init__(self, fid, text, handle_accept, **kwargs):
        super().__init__(**kwargs)
        button = Button(text='accept')
        button.on_press = lambda *args, **kwargs: handle_accept()
        self.ids.buttonwrapper.add_widget(button)
        self.ids.username.text = text
        self.fid = fid
        
class FriendRequestModal(ModalView):

    def __init__(self, handle_accept, handle_add_friend, **kwargs):
        super().__init__(**kwargs)
        self.accept_request = handle_accept
        self.add_friend = handle_add_friend
        
    def add_request(self, fid, username):
        print('add', fid)
        request_choice = RequestChoice(
            fid=fid,    
            text=username,
            handle_accept=partial(self.accept_request, fid, username)
        )
        self.ids.request_list.add_widget(request_choice)

    def remove_request(self, fid):
        to_delete = None
        for choice in self.ids.request_list.children:
            if choice.fid == fid:
                to_delete = choice
        self.ids.request_list.remove_widget(to_delete)
    