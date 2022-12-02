__author__ = 'Cheaterman'

from functools import partial
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.lang import Builder



kv = """
#:import Button kivy.uix.button.Button
<TestWidget>:
    BoxLayout:
        pos: 200, 500
        size: 200, 500
        on_parent:
            if not self.children: \
                [self.add_widget(Button(text=str(i))) for i in range(1, 10)]
"""

Builder.load_string(kv)

class TestWidget(Widget):
    pass

class TestApp(App):
    def build(self):
        return TestWidget()



if __name__ == '__main__':
    TestApp().run()