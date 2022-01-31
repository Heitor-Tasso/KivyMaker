
__all__ = ('runTouchApp', 'async_runTouchApp', 'stopTouchApp', )

from inspect import getfile
from kivy.resources import resource_find
from kivy.base import runTouchApp, async_runTouchApp, stopTouchApp
from os.path import dirname, join, exists, expanduser, sep

import os
from kivy.logger import Logger
from kivy.utils import platform
from kivy.core.window import Window
from kivy.properties import ObjectProperty, StringProperty

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.config import ConfigParser
from kivymd.theming import ThemeManager
from kivymd.utils.fpsmonitor import FpsMonitor

class SimulateApp(Widget):

    title = StringProperty('')
    icon = StringProperty('')
    
    kv_directory = StringProperty('')
    kv_file = StringProperty('')

    theme_cls = ObjectProperty(None)

    _user_data_dir = ""
    
    root = ObjectProperty(None)
    root2 = ObjectProperty(None)
    call_mdapp = True

    __events__ = ('on_start', 'on_stop', 'on_pause', 'on_resume',
                  'on_config_change', )

    def __init__(self, **kwargs):
        self._app_directory = None
        self._app_name = None
        self._app_window = None

        self.theme_cls = ThemeManager()

        self.config = None

    def start(self):
        self.root = self.build()
        return self.root

    def build(self):
        if not self.root:
            return Widget()

    def stop(self, KivyApp=None):
        if KivyApp is None:
            self.root2.remove_screen()
            self.dispatch('on_stop')
        elif KivyApp.root2 != self.root2:
            raise TypeError(f"this argument is not valid: '{KivyApp}'")
        else:
            self.call_mdapp = False
            KivyApp.stop()
    
    def run(self, *args):
        pass
    def on_stop(self, *args):
        pass
    def on_start(self, *args):
        pass
    def on_pause(self, *args):
        pass
    def on_resume(self, *args):
        pass
    def on_config_change(self, *args):
        pass

    def fps_monitor_start(self):
        monitor = FpsMonitor()
        monitor.start()
        Window.add_widget(monitor)

    def get_application_name(self):
        '''Return the name of the application.
        '''
        if self.title is not None:
            return self.title
        clsname = self.__class__.__name__
        if clsname.endswith('App'):
            clsname = clsname[:-3]
        return clsname

    def get_application_icon(self):
        if not resource_find(self.icon):
            return ''
        else:
            return resource_find(self.icon)

    def get_application_config(self, defaultpath='%(appdir)s/%(appname)s.ini'):
        if platform == 'android':
            return join(self.user_data_dir, '.{0}.ini'.format(self.name))
        elif platform == 'ios':
            defaultpath = '~/Documents/.%(appname)s.ini'
        elif platform == 'win':
            defaultpath = defaultpath.replace('/', sep)
        return expanduser(defaultpath) % {
            'appname': self.name, 'appdir': self.directory}

    @property
    def root_window(self):
        return self._app_window

    def load_config(self):
        try:
            config = ConfigParser.get_configparser('app')
        except KeyError:
            config = None
        if config is None:
            config = ConfigParser(name='app')
        self.config = config
        self.build_config(config)
        # if no sections are created, that's mean the user don't have
        # configuration.
        if len(config.sections()) == 0:
            return
        # ok, the user have some sections, read the default file if exist
        # or write it !
        filename = self.get_application_config()
        if filename is None:
            return config
        Logger.debug('App: Loading configuration <{0}>'.format(filename))
        if exists(filename):
            try:
                config.read(filename)
            except:
                Logger.error('App: Corrupted config file, ignored.')
                config.name = ''
                try:
                    config = ConfigParser.get_configparser('app')
                except KeyError:
                    config = None
                if config is None:
                    config = ConfigParser(name='app')
                self.config = config
                self.build_config(config)
                pass
        else:
            Logger.debug('App: First configuration, create <{0}>'.format(
                filename))
            config.filename = filename
            config.write()
        return config

    @property
    def directory(self):
        if self._app_directory is None:
            try:
                self._app_directory = dirname(getfile(self.__class__))
                if self._app_directory == '':
                    self._app_directory = '.'
            except TypeError:
                # if it's a builtin module.. use the current dir.
                self._app_directory = '.'
        return self._app_directory

    def _get_user_data_dir(self):
        # Determine and return the user_data_dir.
        data_dir = ""
        if platform == 'ios':
            data_dir = expanduser(join('~/Documents', self.name))
        elif platform == 'android':
            from jnius import autoclass, cast
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            context = cast('android.content.Context', PythonActivity.mActivity)
            file_p = cast('java.io.File', context.getFilesDir())
            data_dir = file_p.getAbsolutePath()
        elif platform == 'win':
            data_dir = os.path.join(os.environ['APPDATA'], self.name)
        elif platform == 'macosx':
            data_dir = '~/Library/Application Support/{}'.format(self.name)
            data_dir = expanduser(data_dir)
        else:  # _platform == 'linux' or anything else...:
            data_dir = os.environ.get('XDG_CONFIG_HOME', '~/.config')
            data_dir = expanduser(join(data_dir, self.name))
        if not exists(data_dir):
            os.mkdir(data_dir)
        return data_dir

    @property
    def user_data_dir(self):
        if self._user_data_dir == "":
            self._user_data_dir = self._get_user_data_dir()
        return self._user_data_dir

    @property
    def name(self):
        '''.. versionadded:: 1.0.7

        Return the name of the application based on the class name.
        '''
        if self._app_name is None:
            clsname = self.__class__.__name__
            if clsname.endswith('App'):
                clsname = clsname[:-3]
            self._app_name = clsname.lower()
        return self._app_name

    @staticmethod
    def get_running_app():
        '''Return the currently running application instance.

        .. versionadded:: 1.1.0
        '''
        return App._running_app
