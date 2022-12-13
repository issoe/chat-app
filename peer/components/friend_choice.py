from kivy.uix.button import Button
from kivy.lang.builder import Builder
from kivy.utils import get_color_from_hex
from core.utils.color import teal
from kivy.graphics import *

Builder.load_string(
    """
<FriendChoice>
    text: 'Tony'
    size_hint: 1, None
    height: 50
    text_size: self.size
    padding: 20, 0
    halign: 'left'
    valign: 'center'
    canvas.before:
        Color:
            rgba: utils.get_color_from_hex('#52525b')
        RoundedRectangle:
            size: self.size
            pos: self.pos
            radius: 5,
    """
)

class FriendChoice(Button):
    def __init__(self, fid, name,**kwargs):
        super().__init__(**kwargs)
        self.fid = fid
        self.name = name