__version__ = '3.9.7'
__author__ = 'Sr.Gambiarra | HeitorTasso'

__about__ = '''
  Esse programa serve para facilitar o desenvolvimento de apps feito com Kivy ou KivyMD.
    
    - Como ele faz isso?
        Com o KivyMaker podemos atualizar o nosso App,
        sem ter que reiniciar o script pelo terminal ou IDE.
        Isso agiliza o processo de contrução da interface
        e até mesmo para adicionar funcionalidades à UI.
'''

from kivy.config import Config
Config.set('graphics', 'maxfps', '200')

from functools import partial
import traceback, os, sys

from KVUtils import KVGet_path, KVPhone, KVLog
import shutil
try:
    shutil.rmtree(KVGet_path("lang/temp"))
except FileNotFoundError as err:
    KVLog("ERROR", err)

from lang.KVPath import correct_path
from time import time

# Adds support for your workspace packages
pathPython = sys.path[0]
pathWin = f"{pathPython[0:pathPython.find('Temp')]}Programs\Python\Python39\Lib\site-packages"
sys.path.append(pathWin)

from kivy.uix.boxlayout import BoxLayout

from KVuix.KVTerminal import Debug
from KVuix.KVFilechooser import FilesPath
from lang.import_file import Parser
from kivymd.app import MDApp

from kivy.logger import Logger
from kivy.lang import Builder
from kivy.clock import Clock

from kivy.utils import platform
from kivy.core.window import Window
from kivy.metrics import dp

from kivy.base import ExceptionHandler, ExceptionManager
from kivy.properties import StringProperty, ObjectProperty

if platform in {'win', 'linux', 'macosx'}:
    import keyboard



Builder.load_file(KVGet_path('KvMaker.kv'))


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

    path, file = os.path.split(__file__)

    phones = [
        'Ipad', 'Samsung Galaxy S10', 'Galaxy S10 One Camera',
    ]
    props_phones = {
        'ipad':{'scale':0.81, 'height':0.775, 'x':0, 'y':0},
        'samsung-s10':{'scale':0.768, 'height':0.79, 'x':dp(1.5), 'y':dp(2)},
        's10-one-camera':{'scale':0.94, 'height':0.81, 'x':dp(-1.5), 'y':dp(2.5)},
    }

    def __init__(self, **kwargs):
        super(Init_screen, self).__init__(**kwargs)
        self.debug = Debug()
        
        KVLog('PLATFORM', platform)
        KVLog('MAIN-PATH', self.path)
        KVLog('MAIN-FILE', self.file)

        Clock.max_iteration = 60
        
        local_plat = {'win':'C:\\Users', 'macosx':'/Users', 'linux':'/home'}
        if platform in local_plat.keys():
            self.ids.codeplace.ids.sct.rotation = 0
            self.read_keys = self.win_keyboard
            self._system_path = local_plat[platform]
        
        elif platform == 'android':
            self.ids.codeplace.ids.sct.rotation = 180
            self.read_keys = self.kivy_keyboard
            self._system_path = '/storage/emulated/0'
        
        MDApp._running_app.root2 = self
        Clock.schedule_once(self.config)

    def config(self, *args):
        self.parser = Parser()
        self.chooser = FilesPath(self, self._system_path)
        self.ids.codeplace.prop_phone = self.props_phones['samsung-s10']
        
        # text_input = self.ids.input_file.text_input
        # text_input.text =  r'G:\Programacao\Python\GUI\Kivy\Meus\DraftUI\teste.py'
        # text_input.text =  r'G:\Programacao\Python\GUI\Kivy\Meus\DraftUI\main.py'
        # text_input.text =  r'G:\Programacao\Python\GUI\Kivy\Meus\FireDoom\main.py'
        # text_input.text =  r'G:\Programacao\Python\GUI\Kivy\Meus\CloneSpotify\SpotifyClone\Spotify.py'
        # text_input.text =  r'D:\Programacao\Python\GUI\Kivy\Meus'
        # self.search_path()
        # self.change_screens()

    def change_screens(self, name_screen=''):
        SmartImage = self.ids.codeplace.ids.img_phone
        if name_screen == '':
            if not SmartImage.change_screen:
                return None
            
            w, h = SmartImage.size
            if w < dp(500) and w > dp(300):
                SmartImage.source = KVPhone('samsung-s10')
                self.ids.codeplace.prop_phone = self.props_phones['samsung-s10']
            elif w > dp(500):
                SmartImage.source = KVPhone('ipad')
                self.ids.codeplace.prop_phone = self.props_phones['ipad']
        else:
            SmartImage.source = KVPhone(name_screen)
            self.ids.codeplace.prop_phone = self.props_phones[name_screen]

        self.ids.codeplace.ids.phone.width -= 1/100

    def win_keyboard(self, *args):
        if keyboard.is_pressed('ctrl'):
            if keyboard.is_pressed('s'):
                self.allow_loading()
    
    def kivy_keyboard(self, *args):
        #call keyboard kivy
        pass
        #self.allow_loading()

    def allow_loading(self, *args):
        toolbar = self.ids.codeplace.ids.toolbar
        if toolbar.ids.bt_toggle.state == 'down':
            self.quantos_s += 1
            KVLog('RELOAD', f'Ctrl+S {self.quantos_s} vezes')
            self.reaload = True

    def update_editor(self, write=False):
        if not write:
            with open(self.path_file, mode='r', encoding='utf-8') as file:
                KVLog('UPDATE-EDITOR', self.path_file)
                self.ids.codeplace.current_editor.code.text = file.read()
                file.close()
            return None
        
        with open(self.path_file, mode='w', encoding='utf-8') as file:
            KVLog('UPDATE-FILE-ON_EDITOR', self.path_file)
            editor = self.ids.codeplace.editors[self.ids.codeplace.index_editor-1]
            file.write(editor.code.text)
            file.close()

    def carrega(self, *args):
        self.read_keys()
        if not self.reaload:
            return None
        
        self.reaload = False
        self.ids.codeplace.remove_screen()

        if self.ids.codeplace.editors:
            editor = self.ids.codeplace.editors[self.ids.codeplace.index_editor-1]
            if editor.code.focus == True or platform in {'android'}:
                self.update_editor(write=True)
        else:
            self.ids.codeplace.create_editor()
            self.ids.codeplace.hide_editor(self.ids.codeplace.index_editor-1)
        
        tmp = time()
        ext, widget = self.parser.import_widget(self.path_file, self.first_load, self.path)
        dt = round(time()-tmp, 2)
        KVLog('TIME-RELOAD', f'{dt} Segundos')
        self.first_load = False

        if ext == 'Error':
            toolbar = self.ids.codeplace.ids.toolbar
            toolbar.ids.btn_debug.state = 'down'
            setattr(MDApp, '__new_app', None)
            # ocorreu um erro e widget é a mensagem
            # self.debug.ids.text_debug.text += widget
            KVLog('ERRO', widget)
            self.parser.write_logs()
            self.update_editor()
            return None

        phone = self.ids.codeplace.ids.phone
        if ext == 'py':
            widget.root2 = self
            setattr(MDApp, '__new_app', widget)
            phone.add_widget(widget.start())
            widget.dispatch('on_start')
        elif ext == 'kv':
            phone.add_widget(widget)
        
        self.update_editor()
        toolbar = self.ids.codeplace.ids.toolbar
        toolbar.ids.btn_debug.state = 'normal'

    def popup_get_folder(self, *args):
        pass

    def path_file_created(self, text_input, create=False):
        folder_file = self.popup_get_folder('Folder')
        if not folder_file:
            return None
        
        if self.validade_local(text_input):
            self.path_file = f'{folder_file}/{text_input}'
            if create:
                KVLog('CREATE-FILE', self.path_file)
                KVLog('FILE-PATH', folder_file)
                with open(self.path_file, 'w') as new_file:
                    new_file.write('')
                    new_file.close()
                self.ids.input_file.text_input.text = self.path_file
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
        path_input = self.ids.input_file.text_input.text
        if os.path.isfile(path_input):
            self.validade_local(path_input)
            self.charg()
        elif self.suported_files(path_input):
            self.path_file_created(path_input)
            self.charg()
        else:
            # chooser = self.chooser
            if os.path.isdir(path_input):
                self.chooser.ids.fc.path = path_input
            self.chooser.open()

    def charg(self, chooser=None, *args):
        if self.path_file:
            self.path_file = correct_path(self.path_file)
            self.ids.tl.current = 'tela_kv'

            toolbar = self.ids.codeplace.ids.toolbar
            toolbar.ids.bt_toggle.state = 'down'
            Clock.schedule_once(self.allow_loading, 1.5)
            self.chooser.dismiss()

class LogException(ExceptionHandler):

    def handle_exception(self, inst):
        if MDApp._running_app:
            root = MDApp._running_app.root2
            trace = traceback.format_exc()
            err = "\nERROR: {}".format(trace)

            root.parser.write_logs()
            codeplace = root.ids.codeplace
            toolbar = codeplace.ids.toolbar
            
            toolbar.ids.btn_debug.state = 'down'
            toolbar.ids.bt_toggle.state = 'down'
            
            Clock.schedule_once(partial(codeplace.reload, ('down')))
            setattr(MDApp, '__new_app', None)
            root.debug.ids.text_debug.text += err

        Logger.exception('!!ERRO!!')
        return ExceptionManager.PASS

ExceptionManager.add_handler(LogException())

class LoadScreenKivy(MDApp):
    root2 = ObjectProperty()
    simule_app = ObjectProperty()

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
    app = LoadScreenKivy()
    app.run()
    app.root2.debug.stop()
    Window.close()

    try:
        shutil.rmtree(KVGet_path("lang/temp"))
    except (FileNotFoundError, PermissionError) as err:
        KVLog("ERROR", err)
    
