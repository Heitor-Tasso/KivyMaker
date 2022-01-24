
from textwrap import dedent
from lang.py_local_builds import _with_builds, _without_builds
from kivy.lang import Builder
import sys, traceback, os
from kivy.utils import platform

try:
    from importlib import reload, import_module, invalidate_caches
except:      # for py 2 compatibility
    pass

from lang.reload_module import reset_module
from lang.path import correct_path

if platform == 'android':
    from temp_file import temporari_file

def write_logs(local_files, imports_files, local_py_files):
    with open('varibles.txt', mode='w', encoding='utf-8') as txt:
        valor = 'local_py_files = (\n'
        n = 0
        for i in local_py_files:
            n += 1
            if n == 1:
                valor += '    '
            valor += i+', '
            if n == 2:
                valor += '\n'
                n = 0
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

    def __init__(self, **kwargs):
        self.create_varibles()

    def create_varibles(self):
        '''
        Resete all varibles of Parser
        '''
        self.local_files = []
        self.imports_files = []
        self.local_py_files = []
        self.lines_main_file = []

        self.string_builds = False
        self.have_builder = False

        self.index_files = 0
        self.line_class_app = 0

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
        local_imports = self.imports_files[self.index_files::]
        self.index_files += len(locals_files)
        
        for _import, local in zip(local_imports, locals_files):
            with open(local, mode='r', encoding='utf-8') as text:
                lines_text = text.readlines()
                for numL, line in enumerate(lines_text):
                    self.verify_line(line, numL, _import)
                self.have_builder = False
        
        if self.local_files[self.index_files::]:
            self.update_imports()

    def verify_line(self, line, numL, current_local):
        '''
        Verify if the line has a import or Builder functions,
        to use this later.

        Args:
            `line` (str): line of a file being read.
            `numL` (int): index of this line.
            `current_local` (str): path location of this file.
        '''
        # must be in this orden because python import is from .. import ..
        for name_import in ('from', ' import'):
            index_import = line.find(name_import)
            if line[0:index_import].find('#') != -1:
                # the import line is commented
                continue

            if index_import == -1:
                # call build_funcs to know if have Builder.function
                self.update_build_funcs(line, current_local)
                
                if self.string_builds:
                    # line are commented
                    continue

                # check if this line is a Class App
                if line.find('class') != -1 and line.find('App') != -1:
                    self.name_of_class = line.split(' ')[1].split('(')[0]
                    self.line_class_app = numL
                
                continue
            
            list_import = line[index_import::].split(' ')
            # line only with import
            if not 'from' in list_import:
                locals = [[y.split(' ') for y in x.split(',')] for x in list_import[1::]]
                for list_word in locals:
                    for words in list_word:
                        if words[0] not in {' ', ''}:
                            correct_word = words[0].split('\n')[0]
                            if correct_word in _with_builds or correct_word not in _without_builds:
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
                if correct_word in _with_builds or correct_word not in _without_builds:
                    self.update_local_paths(correct_word)
            
            break # found the import, can be braked

    def update_local_paths(self, local):
        '''
        To know if has `local` in this python ambient.
        actualize `local_files` and `imports_files`.

        Args:
            `local` (str): any local of a python file.
        '''
        local = correct_path(local)
        if local in self.imports_files:
            # imports_files already has this local
            return None
        
        local_path = None
        for extension in ('.py', '.pyx'):
            if local_path is not None:
                break

            for locale in map(correct_path, sys.path):
                if not locale.endswith('/'):
                    locale += '/'

                local_path = f'{locale}{local}{extension}'
                try:
                    with open(local_path, mode="r", encoding="utf-8") as texto:
                        if local_path not in self.local_files:
                            self.local_files.append(local_path)
                            self.imports_files.append(local)
                        
                        texto.close()
                    break
                except (FileNotFoundError, OSError):
                    local_path = None

    def update_build_funcs(self, line, current_local):
        '''
        Update files with Builder functions, get if the line has.

        Args:
            `line` (str): line of a file being read.
            `current_local` (str): path location of this file.

        '''
        index_builder = line.find("Builder.load_file")
        # has builder load_file
        if index_builder != -1:
            if not self.have_builder:
                self.local_py_files.append(current_local)
                self.have_builder = True
            return None

        index_builder = line.find("Builder.load_string")
        # has builder load_string in this line
        if index_builder == -1:
            # 1 if has this characters else 0
            has_str = sum(set(map(lambda x: x in line, {'"""', "'''"})))
            if self.string_builds and has_str == 1:
                self.string_builds = False
                self.local_py_files.append(current_local)
                self.have_builder = True
            return None

        # has load_string and are not in a commentary
        if not self.string_builds:
            commented = line[0:index_builder].find('#')
            if line.rfind(')') == -1 and commented == -1:
                self.string_builds = True

    def construc_temp_file(self, filename):
        '''
        Write a new application in a temporary file so it can be used in KvMaker

        Args:
            `filename` (str): local of temp file
        
        '''
        path = self.path_filename.replace("/", "\\")

        lines = dedent(f"""
            __file__ = r'{path}'
            from lang.KivyApp import SimulateApp\n
        """)

        with open(filename, mode='w', encoding='utf-8') as file:
            for numL, line in enumerate(self.lines_main_file):
                if numL != self.line_class_app:
                    index_run = line.find(f'{self.name_of_class}().run()')
                    if index_run == -1:
                        # adiciona nova linha
                        lines += line
                    else:
                        lines += f'{line[0:index_run]}""'
                    continue
                # saber se o projeto está usando KivyMD ou Kivy
                class_app = 'MDApp' if line.find('MDApp') != -1 else 'App'
                # substitui para utilizar o app do KvMaker
                lines += f"{line.replace(class_app, 'SimulateApp')}"
            
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

            local_path = None
            for extension in ('.py', '.kv'):
                if local_path is not None:
                    break

                for locale in sys.path:
                    locale = correct_path(locale)
                    if not locale.endswith('/'):
                        locale += '/'
                    local_path = locale + local + extension
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
                        local_path = None

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
        for import_builder in reversed(self.local_py_files):
            list_import = import_builder.split('/')
            import_path = ''
            for word in list_import:
                import_path += word
                if word != list_import[-1]:
                    import_path += '.'
            reset_module(sys.modules.get(import_path))

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
            if self.dirname in sys.path:
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

        self.name_file, self.extension = file_path.split('.')

        with open(self.path_filename, mode='r', encoding='utf-8') as file:
            if self.extension == 'py':
                self.lines_main_file = file.readlines()
                try:
                    for numL, line in enumerate(self.lines_main_file):
                        self.verify_line(line, numL, self.name_file)

                    # start recursion and parse the main file
                    self.update_imports()
                
                    path_temp = correct_path(path_kvmaker) + '/temp_file/'
                    name_file = 'temp_file.temporari_file'
                    self.construc_temp_file(f'{path_temp}temporari_file.py')

                    if first_load_file is False:
                        self.read_kvs()
                        self.reload_py_files()

                    # reset this module if has
                    if sys.modules.get(name_file) is not None:
                        modul = sys.modules.get(name_file)
                        reset_module(modul)
                    
                    # get the widget os temporary file
                    if platform in {'win', 'linux', 'macosx'}:
                        invalidate_caches()
                        imported = import_module(name_file)
                        widget = getattr(imported, self.name_of_class)
                    elif platform == 'android':
                        widget = getattr(temporari_file, self.name_of_class)
                    
                    write_logs(self.local_files, self.imports_files, self.local_py_files)
                    file.close()
                    return  ['py', widget(), name_file]

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
