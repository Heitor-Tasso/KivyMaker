
import sys, traceback, os
from kivy.lang import Builder
from kivy.utils import platform

from importlib import import_module, invalidate_caches
from lang.path import correct_path, file_paths
from lang.reload_module import reset_module
from KVutils import KVget_path
from textwrap import dedent

if platform == 'android':
    from lang import temp

def write_logs(local_files, imports_files):
    with open('varibles.txt', mode='w', encoding='utf-8') as txt:
        valor = '\n'

        valor += ')\n\nlocal_files = (\n'
        valor += ''.join(tuple(map(lambda i: f'     {i},\n', local_files)))
        valor += '\n)\n\nimports_files = (\n'
        n = 0
        for i in imports_files:
            n += 1
            if n == 1:
                valor += '    '
            valor += i+', '
            if n == 3:
                valor += '\n'
                n = 0
        valor += ')\n\n'

        txt.writelines(valor)
        txt.close()

class Parser(object):

    # varibles that you can't reset
    last_builder_files = []
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
        self._paths = []

        self.find_class = False
        self.index_files = 0

        self.name_file = ''
        self.name_of_class = ''
        self.dirname = ''
        self.extension = ''
        self.path_filename = ''

    def update_imports(self):
        '''
        Start recursion to get all imports
        '''
        locals_files = self.local_files[self.index_files::]
        self.index_files += len(locals_files)
        
        for local in locals_files:
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
        # must be in this orden because python import is from .. import ..
        for name_import in ('from', ' import'):
            index_import = line.find(name_import)
            if line[0:index_import].find('#') != -1:
                # the import line is commented
                continue

            if index_import == -1:
                if line.find('SimulateApp') != -1 or self.find_class:
                    continue
                if line.find('class') != -1 and line.find('App') != -1:
                    self.name_of_class = line.split(' ')[1].split('(')[0]

                    class_app = 'MDApp' if line.find('MDApp') != -1 else 'App'
                    # substitui para utilizar o app do KvMaker
                    line = line.replace(class_app, 'SimulateApp')
                    self.lines_main_file[numL] = line
                    self.find_class = True
                continue
            
            list_import = line[index_import::].split(' ')
            # line only with import
            if not 'from' in list_import:
                locals = [[y.split(' ') for y in x.split(',')] for x in list_import[1::]]
                for list_word in locals:
                    for words in list_word:
                        if words[0] not in {' ', ''}:
                            correct_word = words[0].split('\n')[0]
                            self.update_local_paths(correct_word)
                break # found the import, can be braked

            # with from and import
            locals = line[index_import::].split(' ')
            list_locals = [] if len(locals) < 3 else locals[1].split('.')
            local = ''
            for word_import in list_locals:
                if word_import != list_locals[-1]:
                    local += f'{word_import}/'
                    continue
                
                # corret path of this import
                correct_word = f'{local}{word_import}'.split('\n')[0]
                self.update_local_paths(correct_word)
            
            break # found the import, can be braked

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
        
        for locale in self._paths:
            if locale.find(local) != -1:
                self.local_files.append(locale)
                self.imports_files.append(local)
                break

    def files_project(self):
        self.last_local = self.dirname[0:self.dirname.rfind('/')]
        self._paths = file_paths(self.last_local, ('.py', ))
        if self.path_filename in self._paths:
            self._paths.remove(self.path_filename)
    
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
        files = {'KvMaker.kv', 'style.kv'}
        for path_file in self.last_builder_files:
            """
            set will remove all identically varibles and
            if has only False, can be reload {False} else True in {False True}
            not reload...
            """
            if len(set(map(path_file.endswith, files))) < 2:
                try:
                    with open(path_file, 'r', encoding='utf-8') as file:
                        self.imports_kv_file(file.readlines())
                        file.close()
                except FileNotFoundError:
                    pass
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
            reset_module(pymodul)

    def import_main(self):
        # get the widget os temporary file
        if platform in {'win', 'linux', 'macosx'}:
            invalidate_caches()
            return import_module(self.name_module_main)
        elif platform in {'android'}:
            return temp

    def reset_main_module(self):
        self.import_main()

        # reset this module if has
        modul = sys.modules.get(self.name_module_main)
        if modul is not None:
            reset_module(modul)

        return getattr(self.import_main(), self.name_of_class)()

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
        self.last_builder_files = Builder.files.copy()
        if first_load_file is True:
            if self.dirname in self._paths:
                sys.path.remove(self.dirname)
        else:
            self.unload_kv_files()
                
        self.create_varibles()
        self.path_filename = correct_path(path_filename)
        self.dirname, file_path = os.path.split(self.path_filename)

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
                    widget = self.reset_main_module()
                    
                    write_logs(self.local_files, self.imports_files)
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
