from behaviors.button import ButtonBehavior, ToggleButtonBehavior
from behaviors.touch_effecs import EffectBehavior

from kivy.uix.image import Image
from kivy.uix.anchorlayout import AnchorLayout

from kivy.properties import (
    ListProperty, StringProperty,
    ObjectProperty,
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
    sources = ListProperty([])
    radius_effect = ListProperty([dp(15), dp(15), dp(15), dp(15)])
    state_button = StringProperty('button')
    
    # used on KVInputs to dispatch events
    window_root = ObjectProperty(None)
    name = StringProperty('')

    def __init__(self, **kwargs):
        super(KVButtonIcon, self).__init__(**kwargs)
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
        if self.defaut_color != [1, 1, 1, 1]:
            self.icon_color = self.defaut_color

    def on_mouse_pos(self, *args):
        if not self.get_root_window():
            return
        if self.collide_point(*self.to_widget(*args[1])):
            # used on KVInputs to dispatch events
            if self.window_root:
                self.window_root.dispatch(f'on_{self.name}_pos')
                self.on_enter_pos = True
            if self.pos_color != [0, 0, 0, 0]:
                self.icon_color = self.pos_color
        else:
            if self.defaut_color != [1, 1, 1, 1]:
                self.icon_color = self.defaut_color
            if self.on_enter_pos:
                # used on KVInputs to dispatch events
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
            return super(KVButtonIcon, self).on_touch_down(touch)
        else:
            return False
    
    def on_touch_up(self, touch):
        if touch.grab_current is self:
            self.ripple_fade()
        return super(KVButtonIcon, self).on_touch_up(touch)

class KVToggleButtonIcon(ToggleButtonBehavior, KVButtonIcon):
    state_button = StringProperty('toggle')
