from kivy.lang import Builder
from kivy.uix.codeinput import CodeInput
from kivy.properties import (
    NumericProperty, ObjectProperty,
    DictProperty,
)
from kivymd.app import MDApp
from kivy.clock import Clock
from functools import partial
from kivy.uix.screenmanager import Screen
from KVUtils import KVGet_path
from kivy.utils import get_color_from_hex
from kivy.metrics import dp

Builder.load_file(KVGet_path('KVuix/codeplace/KVCodePlace.kv'))

class MyCode1(CodeInput):
    index = NumericProperty(0)
    def __init__(self, index, **kwargs):
        super().__init__(**kwargs)
        self.index = index
        # self.background_color = get_color_from_hex('#282a36')

class KVScreenCode(Screen):
    index_editor = 0
    current_editor = None
    editors = []
    init_screen = ObjectProperty(None)
    prop_phone = DictProperty({'scale':1, 'height':1, 'x':0, 'y':0})

    def start_zoom_phone(self, dt, wid):
        func = Clock.schedule_interval(partial(self.do_zoom_phone, dt, wid), 0.1)
        return func

    def do_zoom_phone(self, dt, wid, time):
        wid.width += dt

    def stop_zoom_phone(self, func):
        Clock.unschedule(func)
    
    def volta(self):
        bt_toggle = self.ids.toolbar.ids.bt_toggle
        bt_toggle.state = 'normal'

        self.init_screen.reaload = False
        self.init_screen.ids.tl.current = 'config'
        self.init_screen.first_load = True
        self.init_screen.parser.create_varibles()
        
        # self.descarrega_kv('Sair')
        setattr(MDApp, '__new_app', None)
        self.init_screen.quantos_s = 0
    
    def hide_editor(self, index):
        if self.current_editor is None:
            pass
        elif self.editors[index] != self.current_editor:
            self.ids.boxCode.remove_widget(self.current_editor)
        
        num_childrens = len(self.ids.boxCode.children)
        if num_childrens >= 3:
            self.ids.boxCode.remove_widget(self.editors[index])
        else:
            self.ids.boxCode.add_widget(self.editors[index], num_childrens)
        self.current_editor = self.editors[index]
    
    def remove_editor(self, index):
        self.ids.boxCode.remove(self.editors[index])
        del self.editors[index]
        self.index_editor -= 1

    def create_editor(self):
        num_childrens = len(self.ids.boxCode.children)
        if num_childrens >= 3:
            self.remove_editor(self.index_editor-1)
            num_childrens -= 1

        editor = MyCode1(index=self.index_editor, size_hint_x=0.5)
        self.editors.append(editor)
        self.ids.boxCode.add_widget(editor, num_childrens)
        self.index_editor += 1

    def splitter_editor(self, first_x, last_x, widget):
        if max(first_x, last_x) - min(first_x, last_x) < 5:
            return last_x
        if first_x < last_x:
            box = self.ids.boxCode
            if (box.width - box.children[-1].width) < dp(300):
                return last_x

        widget.size_hint_x = 1 - (last_x * (1 / (widget.x + widget.width)))
        return last_x
    
    def update_debug(self, state):
        if state == 'down':
            if self.init_screen.debug not in self.ids.boxkv.children:
                self.ids.boxkv.add_widget(self.init_screen.debug)
        elif state == 'normal':
            self.ids.boxkv.remove_widget(self.init_screen.debug)
    
    def reload(self, state, *args):
        bt_toggle = self.ids.toolbar.ids.bt_toggle
        if state == 'down':
            bt_toggle.icon_color = get_color_from_hex('#50fa7b')
            Clock.schedule_interval(self.init_screen.carrega, 0.3)
        else:
            bt_toggle.icon_color = get_color_from_hex('#ff5555')
            Clock.unschedule(self.init_screen.carrega)

    def remove_screen(self):
        phone = self.ids.phone
        if phone.children:
            phone.remove_widget(phone.children[0])
