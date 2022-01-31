# Python == 3.9.7

from functools import partial
import traceback, os, sys
from KVutils import KVget_path, KVphone

path = sys.path[0]
path = path[0:path.find('Temp')] + r'Programs\Python\Python39\Lib\site-packages'
sys.path.append(path)
del path

with open(KVget_path('lang/temp.py'), mode='w', encoding='utf-8') as file:
    file.write('\n')
    file.close()

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.codeinput import CodeInput

from KVuix.KVfilechooser import FilesPath
from KVuix.KVdropdown import MyDropDown
from lang.import_file import Parser
from kivymd.app import MDApp

from kivy.logger import Logger
from kivy.lang import Builder
from kivy.clock import Clock

from kivy.utils import get_color_from_hex, platform
from lang.path import correct_path
from kivy.metrics import dp
from time import time

from kivy.base import ExceptionHandler, ExceptionManager
from kivy.properties import (
    StringProperty, ObjectProperty, NumericProperty,
)

if platform in {'win', 'linux', 'macosx'}:
    import keyboard

Builder.load_file(KVget_path('KvMaker.kv'))

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
        'ipad':{'scale':0.81, 'height':0.775, 'x':0, 'y':0},
        'samsung-s10':{'scale':0.768, 'height':0.79, 'x':dp(1.5), 'y':dp(2)},
    }

    def __init__(self, **kwargs):
        super(Init_screen, self).__init__(**kwargs)
        print('Voce esta rodando usando -> ', platform)
        print('Local main -> ', self.path)
        print('File main ->', self.file)

        Clock.max_iteration = 60

        local_plat = {'win':'C:\\Users', 'macosx':'/Users', 'linux':'/home'}
        if platform in local_plat.keys():
            self.ids.sct.rotation = 0
            self.read_keys = self.win_keyboard
            self._system_path = local_plat[platform]
        
        elif platform == 'android':
            self.ids.sct.rotation = 180
            self.read_keys = self.kivy_keyboard
            self._system_path = '/storage/emulated/0'
        
        MDApp._running_app.root2 = self
        self.parser = Parser()
        self.chooser = FilesPath(self, self._system_path)
        self.debug = Debug()
        self.dropdown = MyDropDown(['Ipad', 'Samsung Galaxy S10'], self.properties_screens)

        # Clock.schedule_once(self.config)
    
    def config(self, *args):
        # self.ids.input_file.input.text = r'C:\Users\IO\Downloads\SpotifyClone\Spotify.py'
        self.ids.input_file.input.text = r'D:\Trabalho\Programacao\Python\Codes\GUI\Kivy\Meus\Pizzaria\PizzaManagement\PizzaOrder\main.py'
        self.search_path()
        self.change_screens()

    def change_screens(self, name_screen=''):
        BoxScreen = self.ids.conteiner
        if name_screen == '':
            w, h = BoxScreen.size
            if w < dp(500) and w > dp(300):
                BoxScreen.phone_img = KVphone('samsung-s10')
                BoxScreen.property = self.properties_screens['samsung-s10']
            elif w > dp(500):
                BoxScreen.phone_img = KVphone('ipad')
                BoxScreen.property = self.properties_screens['ipad']
        else:
            BoxScreen.phone_img = KVphone(name_screen)
            BoxScreen.property = self.properties_screens[name_screen]

    def update_debug(self, state):
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
        if not self.reaload:
            return None

        self.reaload = False
        self.remove_screen()
        if self.editors:
            editor = self.editors[self.index_editor-1]
            if editor.focus == True:
                print('Escreveu texto do editor no arquivo -> ', self.path_file)
                with open(self.path_file, mode='w', encoding='utf-8') as texto:
                    texto.write(editor.text)
        
        tmp = time()
        ext, widget = self.parser.import_widget(self.path_file, self.first_load, self.path)
        print('Demorou: ', time()-tmp, 'Segundos para importar o App')        
        self.first_load = False

        if ext == 'Error':
            self.ids.btn_debug.state = 'down'
            setattr(MDApp, '__new_app', None)
            # ocorreu um erro e widget é a mensagem
            self.debug.ids.text_debug.text = widget
            return None

        self.ids.telinhas.current = 'ScreenWidget'
        if ext == 'py':
            widget.root2 = self
            setattr(MDApp, '__new_app', widget)
            self.ids.smartphone.add_widget(widget.start())
            widget.dispatch('on_start')
        elif ext == 'kv':
            self.ids.smartphone.add_widget(widget)
        
        if self.editors == []:
            self.create_editor()
            self.hide_editor(self.index_editor-1)
        
        self.current_editor.text = ''.join(self.parser.lines_main_file)
        self.ids.btn_debug.state = 'normal'

    def popup_get_folder(self, *args):
        pass

    def path_file_created(self, text_input, create=False):
        folder_file = self.popup_get_folder('Folder')
        if not folder_file:
            return
        if self.validade_local(text_input):
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
        if os.path.isfile(path_input):
            self.validade_local(path_input)
            self.charg()
        elif self.suported_files(path_input):
            self.path_file_created(path_input)
            self.charg()
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

        self.parser.create_varibles()
        
        # self.descarrega_kv('Sair')
        setattr(MDApp, '__new_app', None)
        self.quantos_s = 0
    
    def volta_debug(self):
        self.ids.btn_debug.state = 'normal'
        self.ids.bt_toggle.state = 'down'

class LogException(ExceptionHandler):

    def handle_exception(self, inst):
        if MDApp._running_app:
            root = MDApp._running_app.root2
            trace = traceback.format_exc()
            err = "ERROR: {}".format(trace)

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
        if name in ('__new_app', 'root2', '_running_app'):
            return super().__getattribute__(name)

        app = getattr(MDApp, '__new_app')
        if app is not None and app.call_mdapp:
            try:
                return getattr(app, name)
            except AttributeError:
                pass
        try:
            return super().__getattribute__(name)
        except AttributeError:
            pass

        raise AttributeError(f"ERROR: __getattribute__ = {name}")

if __name__ == '__main__':
    setattr(MDApp, '__new_app', None)
    LoadScreenKivy().run()

