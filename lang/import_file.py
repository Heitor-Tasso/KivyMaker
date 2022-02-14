
import sys, traceback, os
from kivy.lang import Builder
from kivy.utils import platform
from kivy.clock import Clock

from importlib import import_module, invalidate_caches
from lang.KVPath import correct_path, file_paths
from lang.reload_module import reset_module
from KVUtils import KVget_path
from textwrap import dedent

if platform == 'android':
    from lang import temp

class Parser(object):

    # varibles that you can't reset
    name_module_main = 'lang.temp'

    def __init__(self, **kwargs):
        self.create_varibles()

    def create_varibles(self):
        '''
        Resete all varibles of Parser
        '''
        self.local_files = []
        self.imports_files = []
        self.lines_main_file = []
        self.schedules = []
        self._KvPaths = []
        self._PyPaths = []

        self.find_class = False
        self.commented = False
        self.index_files = 0

        self.name_file = ''
        self.name_of_class = ''
        self.dirname = ''
        self.extension = ''
        self.path_filename = ''

    def write_logs(self):
        varibles = (
            'find_class', 'index_files',
            'name_file', 'name_of_class', 'dirname',
            'extension', 'path_filename',
        )
        big_data = (
            'local_files', 'imports_files',
            '_KvPaths', '_PyPaths', 'schedules',
        )
        
        text = ''
        with open('log.txt', mode='w', encoding='utf-8') as txt:
            text += ''.join(f'\n{x} = "{getattr(self, x)}"\n' for x in varibles)
            
            for v in big_data:
                text += f'\n{v} = [\n'
                text += ''.join(f'{" "*4}"{x}",\n' for x in getattr(self, v))
                text += f']\n'
            
            txt.writelines(text)
            txt.close()

    def update_imports(self):
        '''
        Start recursion to get all imports
        '''
        locals_files = self.local_files[self.index_files::]
        imports_files = self.imports_files[self.index_files::]
        self.index_files += len(locals_files)
        
        for local, f_import in zip(locals_files, imports_files):
            with open(local, mode='r', encoding='utf-8') as text:
                for numL, line in enumerate(text.readlines()):
                    self.verify_line(line, numL)
        
        if self.local_files[self.index_files::]:
            self.update_imports()

    def verify_line(self, line, numL):
        '''
        Verify if the line has a import or Builder functions,
        to use this later.

        Args:
            `line` (str): line of a file being read.
            `numL` (int): index of this line.
        '''
        lp = line.replace(' ', '')
        # to know if this line are commented
        if lp.startswith("'''") or lp.startswith('"""'):
            self.commented = not self.commented
        if lp.startswith('#') or self.commented:
            return None
        
        for name_import in ('from', ' import'):
            index_import = line.find(name_import)
            if index_import == -1:
                self.find_app(line, numL)
                continue
            
            list_import = line[index_import::].split(' ')
            correct_word = ''
            # line only with import
            if not 'from' in list_import:
                locals = [[y.split(' ') for y in x.split(',')] for x in list_import[1::]]
                for list_word in locals:
                    for words in list_word:
                        if words[0] not in {' ', ''}:
                            correct_word = words[0].split('\n')[0]
                            self.update_local_paths(correct_word)
            else:
                # with from and import
                locals = line[index_import::].split(' ')
                list_locals = [] if len(locals) < 3 else locals[1].split('.')
                local = ''
                for word_import in list_locals:
                    if word_import != list_locals[-1]:
                        local += f'{word_import}/'
                        continue
                    correct_word = f'{local}{word_import}'.split('\n')[0]
            if correct_word != '':
                self.update_local_paths(correct_word)
                break

    def find_app(self, line, numL):
        if line.find('SimulateApp') != -1 or self.find_class:
            return None
        
        if line.find('class') != -1 and line.find('App') != -1:
            self.name_of_class = line.split(' ')[1].split('(')[0]

            class_app = 'MDApp' if line.find('MDApp') != -1 else 'App'
            # substitui para utilizar o app do KvMaker
            line = line.replace(class_app, 'SimulateApp')
            self.lines_main_file[numL] = line
            self.find_class = True

    def update_local_paths(self, local):
        '''
        To know if has `local` in this python ambient.
        actualize `local_files` and `imports_files`.

        Args:
            `local` (str): any local of a python file.
        '''
        if local is None or local.startswith('kivy'):
            return None
        
        local = correct_path(local)
        if local in self.imports_files:
            # imports_files already has this local
            return None
        
        for locale in self._PyPaths:
            if locale.find(local) != -1:
                self.local_files.append(locale)
                self.imports_files.append(local)
                break

    def files_project(self):
        self.last_local = self.dirname[0:self.dirname.rfind('/')]
        self._PyPaths = file_paths(self.last_local, ('.py', ))
        self._KvPaths = file_paths(self.last_local, ('.kv', ))
        if self.path_filename in self._PyPaths:
            self._PyPaths.remove(self.path_filename)
    
    def construc_temp_file(self, filename):
        '''
        Write a new application in a temporary file so it can be used in KvMaker

        Args:
            `filename` (str): local of temp file
        
        '''
        path = self.path_filename.replace("/", "\\")
        lines = dedent(f"""
            __file__ = r'{path}'
            from lang.KivyApp import SimulateApp
        """)

        with open(filename, mode='w', encoding='utf-8') as file:
            lines += ''.join(self.lines_main_file)
            # escreve no arquivo temporário
            file.writelines(lines)

    def read_kvs(self):
        '''
        find the imports of Kv file to know where are all files of this project.
        '''
        for path_file in self._KvPaths:
            """
            set will remove all identically varibles and
            if has only False, can be reload {False} else True in {False True}
            not reload...
            """
            with open(path_file, 'r', encoding='utf-8') as file:
                self.imports_kv_file(file.readlines())
                file.close()
        # renew the path of files and imports
        self.update_imports()

    def imports_kv_file(self, lines):
        """
        Get all Kv import of this lines.

        Args:
            `lines` (list[str]): file.readlines(), all lines of this file.
        
        """
        for line in lines:
            if line.find('#:') == -1:
                # is't a kv import
                continue

            word = ''
            for word in reversed(line.split(' ')):
                if word != '':
                    break
            
            local = word[0:word.rfind('.')].replace('.', '/')

            for extension in ('.py', '.kv'):
                local_path = self.last_local + '/' + local + extension
                try:
                    with open(local_path, mode="r", encoding="utf-8") as texto:
                        if extension == '.py':
                            if local_path not in self.local_files:
                                self.local_files.append(local_path)
                                self.imports_files.append(local)
                        else:
                            self.imports_kv_file(texto.readlines())
                        texto.close()
                    break
                except (FileNotFoundError, OSError):
                    pass

    def unload_kv_files(self):
        '''
        Unload all kv dependencies.
        '''
        files = {'KvMaker.kv', 'style.kv'}
        for path_file in reversed(Builder.files):
            """
            set will remove all identically varibles and
            if has only False, can be reload {False} else True in {False True}
            not reload...
            """
            if path_file.startswith('KV'):
                continue
            if len(set(map(path_file.endswith, files))) < 2:
                Builder.unload_file(path_file)

    def reload_py_files(self):
        '''
        Reload all python dependencies.
        '''
        for import_builder in reversed(self.imports_files):
            list_import = import_builder.split('/')
            import_path = ''
            for word in list_import:
                import_path += word
                if word != list_import[-1]:
                    import_path += '.'
            
            pymodul = sys.modules.get(import_path)
            if pymodul is not None:
                reset_module(pymodul)

    def import_main(self):
        # get the widget os temporary file
        if platform in {'win', 'linux', 'macosx'}:
            # invalidate_caches()
            return import_module(self.name_module_main)
        elif platform in {'android'}:
            return temp

    def reset_main_module(self, first_load_file):
        self.import_main()

        # reset this module if has
        modul = sys.modules.get(self.name_module_main)
        if modul is not None and first_load_file is not True:
            reset_module(modul)

        widget = getattr(self.import_main(), self.name_of_class)
        return widget()
        

    def import_widget(self, path_filename, first_load_file, path_kvmaker):
        """
        Get the root Widget of the project being run. 

        Args:
            `path_filename` (str): main file local of the project.
            `first_load_file` (bool): False if this project has imported else True.
            `path_kvmaker` (str): local of KivyMaker app.

        Returns:
            ['py', widget, name_file] if is a python file and was possible to create widget.
            ['kv', width] if is a kv file and was possible to create widget.
        
        """

        if first_load_file is True:
            # remove a pasta anterior
            if self.dirname in self._PyPaths:
                sys.path.remove(self.dirname)
        else:
            self.unload_kv_files()
        
        if self.schedules != []:
            # unschedule functions os temp file
            ev = Clock._root_event
            while ev is not None:
                callback = ev.get_callback()
                if callback not in self.schedules:
                    Clock.unschedule(callback)
                ev = ev.next

        self.create_varibles()
        self.path_filename = correct_path(path_filename)
        self.dirname, file_path = os.path.split(self.path_filename)

        # get Clock functions os KvMaker
        ev = Clock._root_event
        while ev is not None:
            self.schedules.append(ev.get_callback())
            ev = ev.next

        if self.dirname not in sys.path:
            # it needs to be like that because Android only accepts that
            sys.path.insert(0, self.dirname)
        # change python work area
        os.chdir(self.dirname)
        self.files_project()
        self.name_file, self.extension = file_path.split('.')

        with open(self.path_filename, mode='r', encoding='utf-8') as file:
            if self.extension == 'py':
                self.lines_main_file = file.readlines()
                try:
                    for numL, line in enumerate(self.lines_main_file):
                        self.verify_line(line, numL)

                    # start recursion and parse the main file
                    self.update_imports()

                    self.construc_temp_file(KVget_path('lang/temp.py'))

                    self.read_kvs()
                    if first_load_file is False:
                        self.reload_py_files()
                    widget = self.reset_main_module(first_load_file)
                    
                    self.write_logs()
                    file.close()
                    return  ['py', widget]

                except Exception:
                    msg = self.erros()
                    file.close()
                    return ['Error', msg]

            elif self.extension == 'kv':
                try:
                    file.close()
                    return ['kv', Builder.load_string(file.read(), filename=f'{self.name_file}.kv')]
                except Exception as error:
                    file.close()
                    return ['Error', str(error)]
            else:
                file.close()
                return ['Error', "Não suportamos outros tipos de arquivos, somente:\n - arquivo.py\n - arquivo.kv"]

    def erros(self):
        '''
        Get errors of terminal log

        Returns:
            str: error message.
        '''
        trace = traceback.format_exc()
        err = "ERROR: {}".format(trace)
        return err
