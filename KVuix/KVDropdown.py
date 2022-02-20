from kivy.lang import Builder
from kivy.properties import StringProperty

from kivy.uix.dropdown import DropDown
from kivy.uix.button import ButtonBehavior
from kivy.uix.label import Label

Builder.load_string("""

<ButtonDrop>:
    size_hint_y:None
    height:'40dp'
    name_image:''
    on_press:app.root2.change_screens(self.name_image)
    canvas.before:
        Color:
            rgba: [1, 0, 0, 1]
        Rectangle:
            size:self.size
            pos:self.pos
    canvas.after:
        Color:
            rgba: [1, 1, 1, 1]
        Line:
            rectangle:[*self.pos, *self.size]
            width:dp(1.5)

<PhonesDropDown>:
    auto_width:False
    auto_touch_dismiss:True
    width:'200dp'

""", filename = "KVDropdown.kv")

class ButtonDrop(ButtonBehavior, Label):
    name_image = StringProperty('')

class PhonesDropDown(DropDown):
    def __init__(self, names, dict, **kwargs):
        super().__init__(**kwargs)
        for name, key in zip(names, dict.keys()):
            self.add_widget(ButtonDrop(text=name, name_image=key))

