__all__ = ['KVIconInput', 'MyTextInput']

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.metrics import dp, sp
from kivy.properties import (ListProperty, NumericProperty,
                            ObjectProperty, StringProperty)
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.textinput import TextInput

from KVuix.KVIcon import KVToggleButtonIcon, KVButtonIcon, KVAnchorIcon

Builder.load_string("""

<KVIconInput>:
    hide:False
    padding:'10dp'
    size_hint_y:None
    height:'60dp'
    BoxLayout:
        id:box
        canvas:
            Color:
                rgba:root.color_line
            Line:
                rounded_rectangle:(self.pos + self.size + root.radius + [100])
                width:root.line_width
        canvas.before:
            Color:
                rgba:root.background_color
            RoundedRectangle:
                size:self.size
                pos:self.pos
                radius:root.radius
        KVAnchorIcon:
            id:anchor_left
            width:root.icon_left_size[0]+dp(30)
        AnchorLayout:
            id:anchor_input
            padding: '1dp'
            BoxLayout:
                orientation:'vertical'
                Widget:
                    size_hint_y:'0.11dp'
                MyTextInput:
                    on_kv_post: root.text_input = self
                    window_root:root
                    background_color:(1, 1, 1, 0)
                    password:root.hide
                    foreground_color:root.text_input_color
                    multiline:False
        KVAnchorIcon:
            padding: [dp(-1), dp(1), dp(7), dp(1)]
            width:root.icon_left_size[0]+dp(30)
            id:anchor_right
    FloatLayout:
        id:float_lbl
        size_hint_x:None
        width:'200dp'
        Label:
            id:lbl
            text:root.label_text
            font_size:root.label_font_size
            color:root.label_defaut_color

""", filename="KVInputs.kv")

class MyTextInput(TextInput):
    window_root = ObjectProperty()
    def insert_text(self, substring, from_undo=False):
        if self.window_root is not None:
            self.window_root.dispatch('on_input_text')
        
        return super(MyTextInput, self).insert_text(substring, from_undo=from_undo)

class KVIconInput(AnchorLayout):
    line_color = ListProperty([1, 1, 1, 1])
    line_color_pos = ListProperty([0, 0, 0, 0])
    color_line = ListProperty([0, 0, 0, 0])
    line_width = NumericProperty(dp(1.01))

    background_color = ListProperty([0, 0, 0, 0])
    text_input = ObjectProperty()
    radius = ListProperty([dp(15), dp(15), dp(15), dp(15)])

    icon_left = ObjectProperty(False)
    icon_left_type = StringProperty('') # 'toggle' or 'button'
    icon_left_color = ListProperty([1, 1, 1, 1])
    icon_left_source = StringProperty('')
    icon_left_pos_sources = ListProperty([])
    icon_left_state_sources = ListProperty([])
    icon_left_color_pos = ListProperty([0, 0, 0, 0])
    icon_left_size = ListProperty([dp(30), dp(25)])
    icon_left_effect_color = ListProperty([0, 0, 0, 0])

    icon_right = ObjectProperty(False)
    icon_right_type = StringProperty('') # 'toggle' or 'button'
    icon_right_color = ListProperty([1, 1, 1, 1])
    icon_right_source = StringProperty('')
    icon_right_pos_sources = ListProperty([])
    icon_right_state_sources = ListProperty([])
    icon_right_color_pos = ListProperty([0, 0, 0, 0])
    icon_right_size = ListProperty([dp(30), dp(25)])
    icon_right_effect_color = ListProperty([0, 0, 0, 0])

    label_text = StringProperty('')
    label_font_size = NumericProperty(dp(16))
    label_defaut_color = ListProperty([1, 1, 1, 1])
    label_pos_color = ListProperty([1, 1, 1, 1])
    state_label = StringProperty('')

    text_input_color = ListProperty([0, 0, 0, 0])

    def __init__(self, **kwargs):
        self.register_event_type('on_input_press')
        self.register_event_type('on_input_release')
        self.register_event_type('on_input_text')

        cb = ('_mouse_inside', '_mouse_outside', '_press', '_release', '_state')
        for i in {'left', 'right'}:
            set(map(lambda x: self.register_event_type(f'on_icon_{i}{x}'), cb))
    
        self.bind(
            icon_right_size=self.properties_icon_right,
            icon_right_source=self.properties_icon_right,
            icon_right_pos_sources=self.properties_icon_right,
            icon_right_state_sources=self.properties_icon_right,
            icon_right_color=self.properties_icon_right,
            icon_right_color_pos=self.properties_icon_right,
            icon_right_effect_color=self.properties_icon_right,
        )
        self.bind(
            icon_left_size=self.properties_icon_left,
            icon_left_source=self.properties_icon_left,
            icon_left_pos_sources=self.properties_icon_left,
            icon_left_state_sources=self.properties_icon_left,
            icon_left_color=self.properties_icon_left,
            icon_left_color_pos=self.properties_icon_left,
            icon_left_effect_color=self.properties_icon_left,
        )

        super(KVIconInput, self).__init__(**kwargs)

        self.pdentro = (0, 0)
        self.pfora = (0, 0)
        Clock.schedule_once(self.config)

    def config(self, *args):
        
        self.color_line = self.line_color
        radius_left = self.radius[0] if self.radius[0] > self.radius[3] else self.radius[3] 
        radius_right = self.radius[1] if self.radius[1] > self.radius[2] else self.radius[2]
        
        if radius_left > dp(13):
            one_pad_x = radius_left-radius_left/2
            two_pad_x = -one_pad_x/1.4
            self.ids.anchor_left.padding = [one_pad_x, 1, two_pad_x, 1]
            self.ids.anchor_input.padding = [one_pad_x, 1, one_pad_x, 1]
        else:
            self.ids.anchor_left.padding = [dp(7), dp(1), dp(15), dp(1)]
        
        if radius_right > dp(13):
            one_pad_x = radius_right-radius_right/2
            two_pad_x = -one_pad_x/1.7
            self.ids.anchor_right.padding = [two_pad_x, 1, one_pad_x, 1]
            # self.ids.anchor_input.padding = [one_pad_x, 1, two_pad_x, 1]
        else:
            self.ids.anchor_left.padding = [dp(7), dp(1), dp(-3), dp(1)]
            # self.ids.anchor_input.padding = [5, 1, 2, 1]

    def properties_icon_right(self, *args):
        if not self.icon_right:
            return None
        
        self.icon_right.size = self.icon_right_size
        if self.icon_right_source != '':
            self.icon_right.source = self.icon_right_source
        self.icon_right.pos_sources = self.icon_right_pos_sources
        self.icon_right.state_sources = self.icon_right_state_sources
        self.icon_right.defaut_color = self.icon_right_color
        self.icon_right.pos_color = self.icon_right_color_pos
        self.icon_right.effect_color = self.icon_right_effect_color

    def properties_icon_left(self, *args):
        if not self.icon_left:
            return None
        
        self.icon_left.size = self.icon_left_size
        if self.icon_left_source != '':
            self.icon_left.source = self.icon_left_source
        self.icon_left.pos_sources = self.icon_left_pos_sources
        self.icon_left.state_sources = self.icon_left_state_sources
        self.icon_left.defaut_color = self.icon_left_color
        self.icon_left.pos_color = self.icon_left_color_pos
        self.icon_left.effect_color = self.icon_left_effect_color

    def on_icon_right_type(self, icon, state):
        if self.icon_right:
            self.ids.anchor_right.remove(self.icon_right)
            self.icon_right_size = [0, 0]
            self.icon_right = False
        
        if state == 'button':
            self.icon_right = KVButtonIcon()
        elif state == 'toogle':
            self.icon_right = KVToggleButtonIcon()
        else:
            return None
        self.icon_right.window_root = self
        self.icon_right.bind(on_mouse_inside=self.on_icon_right_mouse_inside)
        self.icon_right.bind(on_mouse_outside=self.on_icon_right_mouse_outside)

        self.icon_right.bind(on_press=self.on_icon_right_press)
        self.icon_right.bind(on_release=lambda _: self.dispatch('on_icon_right_release'))
        self.icon_right.bind(on_state=self.on_icon_right_state)
        self.ids.anchor_right.add_widget(self.icon_right)
        self.properties_icon_right()
    
    def on_icon_left_type(self, icon, state):
        if self.icon_left:
            self.ids.anchor_left.remove(self.icon_left)
            self.icon_left_size = [0, 0]
            self.icon_left = False
        
        if state == 'button':
            self.icon_left = KVButtonIcon()
        elif state == 'toogle':
            self.icon_left = KVToggleButtonIcon()
        else:
            return None
        self.icon_left.window_root = self
        self.icon_left.bind(on_mouse_inside=self.on_icon_left_mouse_inside)
        self.icon_left.bind(on_mouse_outside=self.on_icon_left_mouse_outside)

        self.icon_left.bind(on_press=self.on_icon_left_press)
        self.icon_left.bind(on_release=self.on_icon_left_release)
        self.icon_right.bind(on_state=self.on_icon_left_state)
        self.ids.anchor_left.add_widget(self.icon_left)

    def on_touch_down(self, touch):
        if touch.is_mouse_scrolling:
            return False
        if self.ids.anchor_input.collide_point(*touch.pos):
            self.anima(True)
            self.dispatch('on_input_press')

        return super(KVIconInput, self).on_touch_down(touch)
    
    def on_touch_up(self, touch):
        if touch.is_mouse_scrolling:
            return False
        if not self.ids.anchor_input.collide_point(*touch.pos):
            self.dispatch('on_input_release')
            if self.text_input.text == '':
                self.anima(False)

        return super(KVIconInput, self).on_touch_up(touch)

    def on_pos(self, *args):
        self.pdentro = ((self.x - dp(50) + self.radius[-1] / 2.5), (self.y + dp(40)))
        radius_left = self.radius[0] if self.radius[0] > self.radius[3] else self.radius[3] 
        if radius_left <= dp(13):
            radius_left = dp(13)
        if self.icon_left_size[0] == 0:
            self.pfora = ((self.x - dp(50) + radius_left), (self.y + dp(10)))
        else:
            x = (self.x - dp(50) + self.icon_left_size[0] + radius_left / 2)
            self.pfora = (x, (self.y + dp(10)))

        if self.state_label == 'pdentro':
            self.ids.lbl.pos = self.pdentro
        elif self.state_label == 'pfora':
            self.ids.lbl.pos = self.pfora
        else:
            self.ids.lbl.pos = self.pfora

    def anima(self, pos_widget, *args):
        if pos_widget:
            self.state_label = 'pdentro'
            newpos = self.pdentro
            font = sp(12)
            if self.line_color_pos != [0, 0, 0, 0]:
                self.color_line = self.line_color_pos
            self.ids.lbl.color = self.label_pos_color
        if not pos_widget:
            self.state_label = 'pfora'
            newpos = self.pfora
            font = sp(16)
            self.color_line = self.line_color
            self.ids.lbl.color = self.label_defaut_color
        
        Animation(pos=(newpos), font_size=font,
                  d=.1, t='out_sine').start(self.ids.lbl)

    def on_icon_right_press(self, *args):
        pass
    def on_icon_right_release(self, *args):
        pass
    def on_icon_right_state(self, *args):
        pass
    def on_icon_right_mouse_inside(self, *args):
        pass
    def on_icon_right_mouse_outside(self, *args):
        pass
    
    def on_icon_left_press(self, *args):
        pass
    def on_icon_left_release(self, *args):
        pass
    def on_icon_left_state(self, *args):
        pass
    def on_icon_left_mouse_inside(self, *args):
        pass
    def on_icon_left_mouse_outside(self, *args):
        pass

    def on_input_press(self):
        pass
    def on_input_release(self):
        pass
    def on_input_text(self):
        pass
