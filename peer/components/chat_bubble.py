from kivy.lang import Builder
from kivy.uix.label import Label

Builder.load_string(
    """
<ChatBubble>:
    padding: [dp(8), dp(8)]
    size_hint: None, None
    text_size: self.width, None
    height: self.texture_size[1]
    pos_hint: {'left': 1}
    font_size: 20
    width: 300

    canvas.before:
        Color:
            rgba: utils.get_color_from_hex('#4f46e5')
        RoundedRectangle:
            size: self.size
            pos: self.pos
            radius: 5,
"""
)

class ChatBubble(Label):
    def __init__(self, own=True, **kwargs):
        super().__init__(**kwargs)
        self.own = own
