from behaviors.touch_effecs import EffectBehavior
from behaviors.button import ButtonBehavior
from kivy.animation import Animation
from kivy.uix.label import Label
from kivy.uix.image import Image

from kivy.metrics import dp
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.clock import Clock

from kivy.properties import (
    ListProperty, NumericProperty,
    StringProperty, ObjectProperty
)

Builder.load_string("""

<KVButtonEffect>:
    background_color:[1, 1, 1, 0]
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
<KVIconButton>:

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
        self.type_button = 'RoundedButton'
        self.radius = [15,15,15,15]
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

    def on_mouse_pos(self, *args):
        if not self.get_root_window():
            return
        if self.collide_point(*self.to_widget(*args[1])):
            Animation(background = self.color_background[1], d=0.5, 
                  t='out_quad').start(self)
            self.background_line = self.color_line[1]
        else:
            Animation(background = self.color_background[0], d=0.5, 
                  t='out_quad').start(self)
            self.background_line = self.color_line[0]

class KVIconButton(EffectBehavior, ButtonBehavior, Image):
    defaut_color = ListProperty([1, 1, 1, 1])
    pos_color = ListProperty([0, 0, 0, 0])
    sources = ListProperty([])
    state_button = StringProperty('')
    radius_effect = ListProperty([dp(15), dp(15), dp(15), dp(15)])
    window_root = ObjectProperty()
    name = StringProperty('')

    def __init__(self, **kwargs):
        super(KVIconButton, self).__init__(**kwargs)
        self.on_enter_pos = False
        self.type_button = 'RoundedButton'
        Window.bind(mouse_pos=self.on_mouse_pos)
        Clock.schedule_once(self.config)

    def config(self, *args):
        self.num = 0
        self.PosSource = False
        self.radius = self.radius_effect
        if len(self.sources) == 2:
            self.PosSource = True
        if self.sources:
            self.source = self.sources[0]
        self.color = self.defaut_color

    def on_mouse_pos(self, *args):
        if not self.get_root_window():
            return
        if self.collide_point(*self.to_widget(*args[1])):
            if self.window_root:
                self.window_root.dispatch(f'on_{self.name}_pos')
                self.on_enter_pos = True
            if self.pos_color != [0, 0, 0, 0]:
                self.color = self.pos_color
        else:
            self.color = self.defaut_color
            if self.on_enter_pos:
                if self.window_root:
                    self.window_root.dispatch(f'on_{self.name}_pos_release')
                    self.on_enter_pos = False

    def on_touch_down(self, touch):
        if touch.is_mouse_scrolling:
            return False
        elif self in touch.ud:
            return False

        if self.collide_point(*touch.pos):
            if self.color_effect:
                self.ripple_show(touch)
            return super(KVIconButton, self).on_touch_down(touch)
        else:
            return False
    
    def on_touch_up(self, touch):
        if touch.grab_current is self:
            self.ripple_fade()
        return super(KVIconButton, self).on_touch_up(touch)
