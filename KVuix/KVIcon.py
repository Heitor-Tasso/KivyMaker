from behaviors.button import ButtonBehavior, ToggleButtonBehavior
from behaviors.touch_effecs import EffectBehavior

from kivy.uix.image import Image
from kivy.uix.anchorlayout import AnchorLayout

from kivy.properties import (
    ListProperty, StringProperty,
)
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.metrics import dp

Builder.load_string('''

<KVAnchorIcon>:
    size_hint_x:None
    width:'70dp'
    anchor_x:'center'
    anchor_y:'center'

<-KVButtonIcon>:
    icon_color:[1, 1, 1, 1]
    size_hint:None, None
    size:'40dp', '40dp'
    mipmap:True
    allow_strech:True
    keep_ratio:False
    canvas:
        Clear
        Color:
            rgba:self.icon_color
        Rectangle:
            texture:self.texture
            pos:self.pos
            size:self.size

<KVToggleButtonIcon>:
    size:'30dp', '30dp'

''', filename="KVIcons.kv")

class KVAnchorIcon(AnchorLayout):
    pass

class KVButtonIcon(EffectBehavior, ButtonBehavior, Image):
    defaut_color = ListProperty([1, 1, 1, 1])
    pos_color = ListProperty([0, 0, 0, 0])
    pos_sources = ListProperty([])
    state_sources = ListProperty([])
    radius_effect = ListProperty([dp(15), dp(15), dp(15), dp(15)])
    enter_pos = False
    
    def __init__(self, **kwargs):
        self.register_event_type('on_mouse_inside')
        self.register_event_type('on_mouse_outside')
        self.bind(
            pos_sources=self.config,
            state_sources=self.config,
            radius_effect=self.config,
            defaut_color=self.config,
        )
        super(KVButtonIcon, self).__init__(**kwargs)
        self.type_button = 'RoundedButton'
        Window.bind(mouse_pos=self.on_mouse_pos)
        Clock.schedule_once(self.config)

    def config(self, *args):
        self.radius = self.radius_effect
        if len(self.pos_sources) == 2:
            self.source = self.pos_sources[0]
        if len(self.state_sources) == 2:
            self.source = self.state_sources[0]
        if self.defaut_color != [1, 1, 1, 1]:
            self.icon_color = self.defaut_color
    
    def on_state(self, widget, state):
        if len(self.state_sources) == 2:
            if state == 'normal':
                self.source = self.state_sources[0]
            elif state == 'down':
                self.source = self.state_sources[1]

    def on_mouse_pos(self, window, mouse_pos):
        if self.collide_point(*self.to_widget(*mouse_pos)):
            self.enter_pos = True
            self.dispatch('on_mouse_inside')

            if len(self.pos_sources) == 2:
                self.source = self.pos_sources[1]
            if self.pos_color != [0, 0, 0, 0]:
                self.icon_color = self.pos_color
            return None

        if len(self.pos_sources) == 2:
            self.source = self.pos_sources[0]
        if self.defaut_color != [1, 1, 1, 1]:
            self.icon_color = self.defaut_color
        if self.enter_pos:
            self.enter_pos = False
            self.dispatch('on_mouse_outside')

    def on_touch_down(self, touch):
        if touch.is_mouse_scrolling:
            return False
        elif self in touch.ud:
            return False

        if self.collide_point(*touch.pos):
            if self.effect_color:
                self.ripple_show(touch)
            return super(KVButtonIcon, self).on_touch_down(touch)
        else:
            return False
    
    def on_touch_up(self, touch):
        if touch.grab_current is self:
            self.ripple_fade()
        return super(KVButtonIcon, self).on_touch_up(touch)
    
    def on_mouse_inside(self):
        pass
    def on_mouse_outside(self):
        pass

class KVToggleButtonIcon(ToggleButtonBehavior, KVButtonIcon):
    state_button = StringProperty('toggle')
