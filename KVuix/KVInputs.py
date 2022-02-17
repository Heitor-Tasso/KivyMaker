__all__ = ['KVIconInput', 'MyTextInput']

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.metrics import dp, sp
from kivy.properties import (ListProperty, NumericProperty,
                            ObjectProperty, StringProperty)
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.textinput import TextInput

Builder.load_string("""
#: import KVButtonIcon KVuix.KVIcon.KVButtonIcon
#: import KVAnchorIcon KVuix.KVIcon.KVAnchorIcon

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
            KVButtonIcon:
                id:button_left
                name:'icon_left'
                size:root.icon_left_size
                defaut_color:root.icon_left_color
                pos_color:root.icon_left_color_pos
                sources:root.icon_left_source
                color_effect:root.icon_left_effect_color
                state_button:root.icon_left_state
        AnchorLayout:
            id:anchor_input
            padding: '1dp'
            BoxLayout:
                orientation:'vertical'
                Widget:
                    size_hint_y:'0.11dp'
                MyTextInput:
                    id:input
                    window_root:root
                    background_color:(1, 1, 1, 0)
                    password:root.hide
                    foreground_color:root.text_input_color
                    multiline:False

        KVAnchorIcon:
            padding: [dp(-1), dp(1), dp(7), dp(1)]
            width:root.icon_left_size[0]+dp(30)
            id:anchor_right
            KVButtonIcon:
                id:button_right
                name:'icon_right'
                window_root:root
                size:root.icon_right_size
                sources:root.icon_right_source
                defaut_color:root.icon_right_color
                pos_color:root.icon_right_color_pos
                color_effect:root.icon_right_effect_color
                state_button:root.icon_right_state
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
        self.window_root.dispatch('on_input_text')
        return super(MyTextInput, self).insert_text(substring, from_undo=from_undo)

class KVIconInput(AnchorLayout):
    line_color = ListProperty([1, 1, 1, 1])
    line_color_pos = ListProperty([0, 0, 0, 0])
    color_line = ListProperty([0, 0, 0, 0])
    line_width = NumericProperty(1.01)

    background_color = ListProperty([0, 0, 0, 0])
    
    radius = ListProperty([dp(15), dp(15), dp(15), dp(15)])

    icon_left = ObjectProperty()
    icon_left_state = StringProperty('toggle')#'toggle' or 'button'
    icon_left_color = ListProperty([1, 1, 1, 1])
    icon_left_source = ListProperty([])
    icon_left_color_pos = ListProperty([0, 0, 0, 0])
    icon_left_size = ListProperty([dp(30), dp(25)])
    icon_left_effect_color = ListProperty([0, 0, 0, 0])

    icon_right = ObjectProperty()
    icon_right_state = StringProperty('toggle')#'toggle' or 'button'
    icon_right_color = ListProperty([1, 1, 1, 1])
    icon_right_source = ListProperty([])
    icon_right_color_pos = ListProperty([0, 0, 0, 0])
    icon_right_size = ListProperty([dp(30), dp(25)])
    icon_right_effect_color = ListProperty([0, 0, 0, 0])

    label_text = StringProperty('')
    label_font_size = NumericProperty(dp(16))
    label_defaut_color = ListProperty([1, 1, 1, 1])
    label_pos_color = ListProperty([1, 1, 1, 1])
    state_label = StringProperty('')

    input = ObjectProperty()
    text_input_color = ListProperty([1, 1, 1, 1])

    __events__ = (
        'on_touch_down', 'on_touch_move', 'on_touch_up', 'on_kv_post',
        
        'on_icon_right_press', 'on_icon_right_release', 'on_icon_left_press',
        'on_icon_left_release', 'on_input_press', 'on_input_release', 
        'on_input_text', 'on_init_input', 'on_icon_right_pos',
        'on_icon_right_pos_release',
    )

    def __init__(self, **kwargs):
        super(KVIconInput, self).__init__(**kwargs)
        self.pdentro = (0, 0)
        self.pfora = (0, 0)
        Clock.schedule_once(self.config)

    def icon_down(self, button, *args):
        if button.state_button == 'toggle':
            button.num += 1
            if button.PosSource and button.num == 1:
                button.source = button.sources[1]
            elif button.num == 2:
                button.source = button.sources[0]
                button.num = 0
        elif button.state_button == 'button':
            if button.PosSource:
                button.source = button.sources[1]
    def icon_up(self, button, *args):
        if button.state_button == 'button':
            button.source = button.sources[0]

    def config(self, *args):
        self.pads()
        self.color_line = self.line_color
        self.icon_right = self.ids.button_right
        self.icon_left = self.ids.button_left
        self.input = self.ids.input
        if not self.icon_left_source:
            self.ids.box.remove_widget(self.ids.anchor_left)
            self.icon_left_size = [0, 0]
            self.icon_left = False
        if not self.icon_right_source:
            self.ids.box.remove_widget(self.ids.anchor_right)
            self.icon_right_size = [0, 0]
            self.icon_right = False
        self.dispatch('on_init_input')

    def pads(self, *args):
        radius_left = self.radius[0] if self.radius[0] > self.radius[3] else self.radius[3] 
        radius_right = self.radius[1] if self.radius[1] > self.radius[2] else self.radius[2]
        
        if radius_left > 13:
            one_pad_x = radius_left-radius_left / 2
            two_pad_x = -one_pad_x / 1.4
            self.ids.anchor_left.padding = [one_pad_x, 1, two_pad_x, 1]
            self.ids.anchor_input.padding = [one_pad_x, 1, one_pad_x, 1]
        else:
            self.ids.anchor_left.padding = [dp(7), dp(1), dp(15), dp(1)]
        
        if radius_right > dp(13):
            one_pad_x = radius_right-radius_right / 2
            two_pad_x = -one_pad_x / 1.7
            self.ids.anchor_right.padding = [two_pad_x, 1, one_pad_x, 1]
            # self.ids.anchor_input.padding = [one_pad_x, 1, two_pad_x, 1]
        else:
            self.ids.anchor_left.padding = [dp(7), dp(1), dp(-3), dp(1)]
            # self.ids.anchor_input.padding = [5, 1, 2, 1]

    def on_touch_down(self, touch):
        if touch.is_mouse_scrolling:
            return False

        if self.ids.anchor_input.collide_point(*touch.pos):
            self.anima(True)
            self.dispatch('on_input_press')
            
        if self.icon_right:
            if self.icon_right.collide_point(*touch.pos):
                self.icon_down(self.icon_right)
                self.dispatch('on_icon_right_press')
        if self.icon_left:
            if self.icon_left.collide_point(*touch.pos):
                self.icon_down(self.icon_left)
                self.dispatch('on_icon_left_press')

        return super(KVIconInput, self).on_touch_down(touch)
    
    def on_touch_up(self, touch):
        if touch.is_mouse_scrolling:
            return False

        if not self.ids.anchor_input.collide_point(*touch.pos):
            self.dispatch('on_input_release')
            if self.ids.input.text == '':
                self.anima(False)
        if self.icon_right:
            if self.icon_right.collide_point(*touch.pos):
                self.icon_up(self.icon_right)
                self.dispatch('on_icon_right_release')
        if self.icon_left:
            if self.icon_left.collide_point(*touch.pos):
                self.icon_up(self.icon_left)
                self.dispatch('on_icon_left_release')
        return super(KVIconInput, self).on_touch_up(touch)

    def on_icon_right_press(self):
        pass
    def on_icon_right_release(self):
        pass
    def on_icon_left_press(self):
        pass
    def on_icon_left_release(self):
        pass
    def on_input_press(self):
        pass
    def on_input_release(self):
        pass
    def on_init_input(self):
        pass
    def on_input_text(self, *args):
        pass
    def on_icon_right_pos(self, *args):
        pass
    def on_icon_right_pos_release(self, *args):
        pass

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
