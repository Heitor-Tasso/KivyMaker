from behaviors.touch_effecs import EffectBehavior
from behaviors.button import ButtonBehavior
from kivy.animation import Animation
from kivy.uix.label import Label

from kivy.core.window import Window
from kivy.lang import Builder
from kivy.clock import Clock

from kivy.properties import (
    ListProperty, NumericProperty,
)

Builder.load_string("""

<KVButtonEffect>:
    background_color:[1, 1, 1, 0]
    radius: [0, 0, 0, 0]
    canvas.before:
        Color:
            rgba:self.background
        RoundedRectangle:
            size:self.size
            pos:self.pos
            radius:self.radius[::-1]
        Color:
            rgba:self.background_line
        Line:
            rounded_rectangle:(self.pos + self.size + self.radius + [100])
            width:self.width_line

""", filename="KVButtons.kv")

class KVButtonEffect(EffectBehavior, ButtonBehavior, Label):
    #Colors
    background_line = ListProperty([0, 0, 0, 0])
    background = ListProperty([0, 0, 0, 0])
    color_background = ListProperty([[0.05, 0.0, 0.4, 1], [0.0625, 0.0, 0.5, 1]])
    color_line = ListProperty([[1, 1, 1, 1], [0.8, 0.925, 1, 1]])
    #Sizes
    width_line = NumericProperty(1.01)

    def __init__(self, **kwargs):
        super(KVButtonEffect, self).__init__(**kwargs)
        self.type_button = 'Rounded'
        Window.bind(mouse_pos=self.on_mouse_pos)
        Clock.schedule_once(self.set_colors)
    
    def set_colors(self, *args):
        self.background = self.color_background[0]
        self.background_line = self.color_line[0]

    def on_touch_down(self, touch):
        if touch.is_mouse_scrolling:
            return False
        elif self in touch.ud:
            return False

        if self.collide_point(*touch.pos):
            touch.grab(self)
            self.ripple_show(touch)
            return super(KVButtonEffect, self).on_touch_down(touch)
        else:
            return False

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)
            self.ripple_fade()
        return super(KVButtonEffect, self).on_touch_up(touch)

    def on_mouse_pos(self, window, mouse_pos):
        if self.collide_point(*self.to_widget(*mouse_pos)):
            anim = Animation(
                background=self.color_background[1],
                d=0.5, t='out_quad',
            )
            anim.start(self)
            self.background_line = self.color_line[1]
        else:
            anim = Animation(
                background=self.color_background[0],
                d=0.5, t='out_quad',
            )
            anim.start(self)
            self.background_line = self.color_line[0]
