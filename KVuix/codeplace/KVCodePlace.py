from kivy.lang import Builder
from kivy.uix.scrollview import ScrollView
from kivy.uix.codeinput import CodeInput
from kivy.core.text.markup import MarkupLabel as CoreLabel
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

class TextCode(CodeInput):
    can_scroll = True
    def on_touch_down(self, touch):
        if not self.can_scroll:
            # Não posso rolar
            return False
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if not self.can_scroll:
            # Não posso rolar
            return False
        return super().on_touch_move(touch)

class CodeEditor(ScrollView):
    index = NumericProperty(0)
    code = ObjectProperty(None)
    bar_move = ''
    touch_pos = [0, 0]

    def __init__(self, index, **kwargs):
        super().__init__(**kwargs)
        self.index = index
        self.bind(size=self.update_width_code)
    
    def on_touch_down(self, touch):
        self.touch_pos = touch.pos
        if not self.collide_point(*touch.pos):
            return False

        self.code.can_scroll = False
        if touch.x >= (self.x + self.width - self.bar_width):
            self.bar_move = 'left'
            return True
        elif touch.y <= (self.y + self.bar_width):
            self.bar_move = 'bottom'
            return True

        self.bar_move = ''
        self.code.can_scroll = True
        return super().on_touch_down(touch)

    def maximum_text(self):
        label = CoreLabel(**self.code._get_line_options())
        lines = self.code.text.splitlines()
        max_width = 0
        for i in range(len(lines)):
            max_width = max(label.get_extents(lines[i])[0], max_width)
        return max_width + dp(20)

    def update_width_code(self, *args):
        if self.code is None or len(self.code._cursor) < 2:
            return None

        labels = self.code._lines_labels
        if not labels:
            return None
        
        if self.code._cursor[1] > len(labels):
            self.code._cursor = (0, 0)

        max_width = max(self.maximum_text(), self.width)
        if max_width != self.code.width:
            self.code.width = max_width
            self.scroll_x = 1

        current_label = labels[self.code._cursor[1]]
        if current_label.width > self.width:
            if self.scroll_x <= 0.5:
                self.scroll_x += 0.5
        else:
            self.scroll_x = 0
        
        if self.code.height <= self.height:
            self.scroll_y = 0
    
    def decrise_scroll(self, dt, direction):
        name = f'scroll_{direction}'
        n_scroll = getattr(self, name)
        
        if n_scroll >= dt:
            setattr(self, name, (n_scroll - dt))
        elif n_scroll > 0:
            setattr(self, name, 0)

    def incrise_scroll(self, dt, direction):
        name = f'scroll_{direction}'
        n_scroll = getattr(self, name)
        
        if n_scroll <= 1 - dt:
            setattr(self, name, (n_scroll + dt))
        elif n_scroll < 1:
            setattr(self, name, 1)

    def on_touch_move(self, touch):
        if self.code is None:
            return None
        if not self.collide_point(*touch.pos):
            return None
        
        if self.code._selection:
            # Desce ou sobe de acordo com a seleção
            x, y = touch.pos
            
            dt = (1 / self.code.height) * dp(20)
            if y < (self.y + dp(40)):
                self.decrise_scroll(dt, 'y')
            elif y > (self.y + self.height - dp(40)):
                self.incrise_scroll(dt, 'y')

            dt = (1 / self.code.height) * 40
            if x < (self.x + dp(40)):
                self.decrise_scroll(dt, 'x')
            elif x > (self.x + self.width - dp(40)):
                self.incrise_scroll(dt, 'x')

        if not self.code.can_scroll:
            last_pos = self.touch_pos
            self.touch_pos = touch.pos

            cfd = (last_pos[1] - touch.y)
            distance = abs(cfd * (len(self.code._lines) * dp(17) / dp(185)) / 2.2)
            dt = round((1 / self.code.height * distance), 2)
            if self.bar_move == 'left':
                if cfd > dp(5):
                    # Movimentar bar para baixo
                    self.decrise_scroll(dt, 'y')
                elif cfd < dp(-5):
                    # Movimentar bar para cima
                    self.incrise_scroll(dt, 'y')
                else:
                    self.touch_pos = last_pos
            
            cfd = (last_pos[0] - touch.x)
            dt = dp(7) * (1 / (self.code.width/max(abs(cfd), 1)))
            if self.bar_move == 'bottom':
                if cfd > dp(5):
                    # Movimentar bar para esquerda
                    self.decrise_scroll(dt, 'x')
                elif cfd < dp(-5):
                    # Movimentar bar para a direita
                    self.incrise_scroll(dt, 'x')
                else:
                    self.touch_pos = last_pos
            return True

        return super().on_touch_move(touch)

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

        editor = CodeEditor(index=self.index_editor, size_hint_x=0.5)
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
