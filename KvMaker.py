from functools import partial
import sys, traceback, os
from typing import Text

path, file = os.path.split(__file__)
path_temp =  path + '/temp_file/temporari_file.py'
with open(path_temp, mode='w', encoding='utf-8') as file:
    file.write('\n')
    file.close()

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.codeinput import CodeInput
from kivy.uix.dropdown import DropDown
from uix.filechooser import FilesPath
from kivy.uix.button import Button
from lang.import_file import Parser
from kivymd.app import MDApp

from kivy.logger import Logger
from kivy.lang import Builder
from kivy.clock import Clock

from kivy.utils import get_color_from_hex, platform
from lang.path import correct_path
from kivy.metrics import dp, sp
from time import time

from kivy.base import ExceptionHandler, ExceptionManager
from kivy.properties import (
    ListProperty, StringProperty,
    ObjectProperty, NumericProperty,
)

if platform == 'win':
    import keyboard

print('Voce esta rodando usando:', platform)

Builder.load_file('KvMaker.kv')

class ButtonDrop(Button):
    name_image = StringProperty('')

class MyDropDown(DropDown):

    def __init__(self, names, dict, **kwargs):
        super().__init__(**kwargs)
        for name, key in zip(names, dict.keys()):
            self.add_widget(ButtonDrop(text=name, name_image=key))

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            if self.auto_touch_dismiss:
                self.dismiss()

class Debug(BoxLayout):
    pass

class MyCode1(CodeInput):
    index = NumericProperty(0)
    def __init__(self, index, **kwargs):
        super().__init__(**kwargs)
        self.index = index
        # self.background_color = get_color_from_hex('#282a36')

class Init_screen(BoxLayout):

    path_file = StringProperty('')
    _icons = StringProperty('')
    _smartphones = StringProperty('')
    _system_path = '' 

    parser = ObjectProperty(None)
    chooser = ObjectProperty(None)
    debug = ObjectProperty(None)

    first_load = True
    quantos_s = 0
    reaload = False
    read_keys = None

    index_editor = 0
    current_editor = None
    editors = []

    path, file = os.path.split(__file__)

    properties_screens = {
        'ipad.png':{'scale':0.81, 'height':0.775, 'x':0, 'y':0},
        'samsung-s10.png':{'scale':0.768, 'height':0.79, 'x':dp(1.5), 'y':dp(2)},
    }

    def __init__(self, **kwargs):
        super(Init_screen, self).__init__(**kwargs)
        print('Local main -> ', self.path)
        print('File main ->', self.file)
        Clock.max_iteration = 60
        self._icons = self.path + '/assets/icons/'
        self._smartphones = self.path + '/assets/smartphones/'

        if platform == 'win':
            self.read_keys = self.win_keyboard
            self._system_path = 'C:\\Users'
        elif platform == 'android':
            self.read_keys = self.kivy_keyboard
            self._system_path = '/storage/emulated/0'
        
        MDApp._running_app.root2 = self
        self.parser = Parser()
        self.chooser = FilesPath(self, self._system_path)
        self.debug = Debug()
        self.dropdown = MyDropDown(['Ipad', 'Samsung Galaxy S10'], self.properties_screens)

    def change_screens(self, name_screen=''):
        BoxScreen = self.ids.conteiner
        if name_screen == '':
            w, h = BoxScreen.size
            if w < dp(500) and w > dp(300):
                BoxScreen.phone_img = self._smartphones+'samsung-s10.png'
                BoxScreen.property = self.properties_screens['samsung-s10.png']
            elif w > dp(500):
                BoxScreen.phone_img = self._smartphones+'ipad.png'
                BoxScreen.property = self.properties_screens['ipad.png']
        else:
            BoxScreen.phone_img = self._smartphones+name_screen
            BoxScreen.property = self.properties_screens[name_screen]

    def update_debug(self, state):
        print(state)
        if state == 'down':
            if self.debug not in self.ids.boxkv.children:
                self.ids.boxkv.add_widget(self.debug)
        elif state == 'normal':
            self.ids.boxkv.remove_widget(self.debug)

    def splitter_editor(self, first_x, last_x, widget):
        if max(first_x, last_x) - min(first_x, last_x) < 5:
            return first_x
        if first_x < last_x:
            box = self.ids.boxCode
            if (box.width - box.children[-1].width) < dp(300):
                return first_x

        widget.size_hint_x = 2 - (last_x * (2 / (widget.x + widget.width)))
        return last_x

    def create_editor(self):
        num_childrens = len(self.ids.boxCode.children)
        if num_childrens >= 3:
            self.remove_editor(self.index_editor-1)
            num_childrens -= 1
        editor = MyCode1(index=self.index_editor, size_hint_x=0.5)
        self.editors.append(editor)
        self.ids.boxCode.add_widget(editor, num_childrens)
        self.index_editor += 1
    
    def remove_editor(self, index):
        self.ids.boxCode.remove(self.editors[index])
        del self.editors[index]
        self.index_editor -= 1

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

    def reload(self, state, *args):
        if state == 'down':
            self.ids.bt_toggle.icon_color = get_color_from_hex('#50fa7b')
            Clock.schedule_interval(self.carrega, 0.3)
        else:
            self.ids.bt_toggle.icon_color = get_color_from_hex('#ff5555')
            Clock.unschedule(self.carrega)

    def remove_screen(self):
        filhos = self.ids.smartphone.children
        if filhos:
            self.ids.smartphone.remove_widget(filhos[0])

    def win_keyboard(self, *args):
        if keyboard.is_pressed('ctrl'):
            if keyboard.is_pressed('s'):
                self.allow_loading()
    
    def kivy_keyboard(self, *args):
        #call keyboard kivy
        pass
        #self.allow_loading()

    def allow_loading(self, *args):
        if self.ids.bt_toggle.state == 'down':
            self.quantos_s += 1
            print(f'Ctrl + s is pressed {self.quantos_s}')
            self.reaload = True

    def carrega(self, *args):
        self.read_keys()
        if self.reaload:
            self.reaload = False
            self.remove_screen()

            if self.editors:
                editor = self.editors[self.index_editor-1]
                if editor.focus == True:
                    print('focus == True')
                    with open(self.path_file, mode='w', encoding='utf-8') as texto:
                        texto.write(editor.text)

            tmp = time()
            widget = self.parser.import_widget(self.path_file, self.first_load, self)
            print('Demorou: ', time()-tmp, 'Segundos para importar o App')
            self.first_load = False

            if not widget or not widget[1]:
                return
            if widget[0] == 'Error':
                # self.ids.telinhas.current = 'debug'
                self.ids.btn_debug.state = 'down'
                setattr(MDApp, '__new_app', None)
                self.debug.ids.text_debug.text = widget[1]
            else:
                self.ids.telinhas.current = 'ScreenWidget'
                if widget[0] == 'py':
                    widget[1].root2 = self
                    setattr(MDApp, '__new_app', widget[1])
                    wid = widget[1].start()
                    self.ids.smartphone.add_widget(wid)
                    widget[1].dispatch('on_start')

                elif widget[0] == 'kv':
                    self.ids.smartphone.add_widget(widget[1])
                
                if self.editors == []:
                    self.create_editor()
                    self.hide_editor(self.index_editor-1)
                
                self.current_editor.text = self.parser.read_file
                self.ids.btn_debug.state = 'normal'

    def popup_get_folder(self, *args):
        pass
    def path_file_created(self, text_input, create=False):
        folder_file = self.popup_get_folder('Folder')
        if not folder_file:
            return
        if self.validade_local(text_input):
            # for i in ['//', '/', '\\']:
            #     if text_input.startswith(i):
            #         self.path_file = folder_file + text_input
            #         break
            # if not self.path_file:
            self.path_file = folder_file + '/' + text_input
            if create:
                print('created file')
                print(self.path_file, folder_file)
                with open(self.path_file, 'w') as new_file:
                    new_file.write('')
                    new_file.close()
                self.ids.input_file.input.text = self.path_file
                self.search_path()

    def suported_files(self, name_file:str) -> bool:
        for i in ['.py', '.kv']:
            if name_file.endswith(i):
                return True
        return False

    def validade_local(self, path):

        if self.suported_files(path):
            self.path_file = path
            return True
        else:
            #error path "Invalid Local"
            return False

    def search_path(self):
        path_input = self.ids.input_file.input.text

        # if [i for i in ['/', '//', '\\'] if i in path_input]:
        if os.path.isfile(path_input):
            self.validade_local(path_input)
            self.charg()
        elif self.suported_files(path_input):
            self.path_file_created(path_input)
            self.charg()
        # elif os.path.isdir(path_input):
        #     #error path "Invalid Path"
        #     pass
        else:
            if os.path.isdir(path_input):
                self.chooser.ids.fc.path = path_input
            self.chooser.open()

    def charg(self, *args):
        if self.path_file:
            self.path_file = correct_path(self.path_file)
            self.ids.tl.current = 'tela_kv'
            self.ids.bt_toggle.state = 'down'
            self.reaload = True
            self.chooser.dismiss()
    
    def volta(self):
        self.reaload = False
        self.ids.bt_toggle.state = 'normal'
        self.ids.tl.current = 'config'
        self.first_load = True
        self.quantos_s = 1

        first_index = self.parser.first_index
        dirname = self.parser.dirname

        self.parser.unload_files_builder(first_index, dirname)
        self.parser.reload_files_builder()
        self.parser.unload_builds_main(first_index, dirname)
        self.parser.create_varibles()
        
        # self.descarrega_kv('Sair')
        setattr(MDApp, '__new_app', None)
        self.quantos_s = 0
    
    def volta_debug(self):
        # self.ids.telinhas.current = 'ScreenWidget'
        self.ids.btn_debug.state = 'normal'
        self.ids.bt_toggle.state = 'down'
        # self.ids.bt_toggle.state = 'normal'

class LogException(ExceptionHandler):

    def handle_exception(self, inst):
        if MDApp._running_app:
            root = MDApp._running_app.root2
            # type, value, tb = sys.exc_info()
            # erros = traceback.format_list(traceback.extract_tb(tb))
            # err = ''
            # for w in erros:
            #     err += w
            trace = traceback.format_exc()
            err = "ERROR: {}".format(trace)
            # root.ids.telinhas.current = 'debug'
            root.ids.btn_debug.state = 'down'
            root.ids.bt_toggle.state = 'down'
            Clock.schedule_once(partial(root.reload, ('down')))
            setattr(MDApp, '__new_app', None)
            root.debug.ids.text_debug.text = err

        Logger.exception('!!ERRO!!')
        return ExceptionManager.PASS

ExceptionManager.add_handler(LogException())

class LoadScreenKivy(MDApp):
    root2 = ObjectProperty()

    def build(self):
        return Init_screen()

    def __getattribute__(self, name):
        # print('__getattribute__: ', name)
        if name in ('__new_app', 'root2', '_running_app'):
            print('Chamou: ', name)
            return super().__getattribute__(name)

        app = getattr(MDApp, '__new_app')
        if app is not None and app.call_mdapp:
            try:
                return getattr(app, name)
            except AttributeError as err:
                pass
        try:
            return super().__getattribute__(name)
        except AttributeError as err:
            pass

        raise AttributeError(f"ERROR: __getattribute__ = {name}")

if __name__ == '__main__':
    setattr(MDApp, '__new_app', None)
    LoadScreenKivy().run()

