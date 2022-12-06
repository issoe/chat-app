from kivy.uix.button import Button
from kivy.lang.builder import Builder

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
            rgba: utils.get_color_from_hex('#3f3f46')
        RoundedRectangle:
            size: self.size
            pos: self.pos
            radius: 5,
    """
)

class FriendChoice(Button):
    pass