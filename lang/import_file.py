
import sys, traceback, os
from kivy.lang import Builder
from kivy.clock import Clock
from lang.KivyApp import KVClock, KVWindow
import shutil, random

from textwrap import dedent
from KVUtils import KVGet_path, KVLog, sys_path
from lang.KVPath import correct_path, file_paths
from lang.reload_module import reload_module, get_module
from lang.regex import RegEx, process_py_line, process_kv_line, get_random_string

from kivy.core.image import ImageLoader


def ignorePath(igone_paths):
  def ignoref(directory, contents):
    paths = igone_paths
    if isinstance(paths, str):
        paths = [paths]

    new_contents = []
    for f in contents:
        for path in paths:
            if not directory.endswith(path):
                continue
            new_contents.append(f)
    return new_contents
  return ignoref


init_file = None

class Parser(object):

    current_temp_path = ''
    last_images = ()

    def __init__(self, **kwargs):
        self.create_varibles()

    def create_varibles(self):
        '''
        Resete all varibles of Parser
        '''
        self.local_files = []
        self.imports_files = []
        self.schedules = []
        self._KvPaths = []
        self._PyPaths = []
        self.local_kivy_files = []
        self.clock_functions = []

        self.find_class = False
        self.commented = False
        self.in_kv_string = False
        self.has_string_filename = False
        self.index_files = 0

        self.name_file = ''
        self.name_of_class = ''
        self.dirname = ''
        self.extension = ''
        self.path_filename = ''
        
        self.main_reg_ex = None

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

    def create_regex(self, lines, path, caller="others") -> RegEx:
        name_p = self.dirname.split("/")[-1]
        destin_path = KVGet_path(f"lang/temp/{self.current_temp_path}/{path.split(name_p)[-1]}")
        
        reg_ex = RegEx(lines, path, destin_path)
        process = process_py_line if path.endswith(".py") else process_kv_line
        args = (reg_ex, self, caller, init_file) if path.endswith(".py") else (reg_ex, self)
        
        while reg_ex.next(): process(*args)

        file = None
        for name_import in reg_ex.imports:
            local_path = self.dirname + '/' + name_import
            # print("local_path IMPORT -=> ", local_path)
            try:
                file = open(local_path, mode="r", encoding="utf-8")
            except (FileNotFoundError, OSError):
                continue
                
            if name_import.endswith('.py'):
                if name_import in self.imports_files:
                    file.close()
                    continue

                for locale in self._PyPaths:
                    if locale.find(name_import) == -1:
                        continue

                    self.local_files.append(locale)
                    self.imports_files.append(name_import)
                    break
            elif name_import.endswith('.kv'):
                new_lines = file.read().split("\n")
                file.close()
                # Continue the tree
                self.create_regex(new_lines, local_path)
            else:
                file.close()

        return reg_ex

    def update_imports(self):
        '''
        Start recursion to get all imports
        '''
        locals_files = self.local_files[self.index_files::]
        imports_files = self.imports_files[self.index_files::]
        self.index_files += len(locals_files)

        name_p = self.dirname.split("/")[-1]
        for local, f_import in zip(locals_files, imports_files):
            with open(local, mode='r', encoding='utf-8') as text:
                reg_ex = self.create_regex(text.read().split("\n"), local)

                _file_path = KVGet_path(f"lang/temp/{self.current_temp_path}/{local.split(name_p)[-1]}")

                with open(_file_path, "w", encoding="UTF-8") as temp_file:
                    __file_new = _file_path.replace('/', '\\')
                    temp_file.write(f"__file__ = r'{__file_new}'\n\n")
                    temp_file.write(reg_ex.result())
                
        
        if self.local_files[self.index_files::]:
            self.update_imports()


    def files_project(self, kvmaker_path):
        self._PyPaths = file_paths(self.dirname, ('.py', ))
        self._KvPaths = file_paths(self.dirname, ('.kv', ))

        for path in file_paths(kvmaker_path, ('.py', '.kv')):
            if path in self._PyPaths:
                self._PyPaths.remove(path)
            elif path in self._KvPaths:
                self._KvPaths.remove(path)
    
    def change_main_file(self):
        '''
        Write a new application in a temporary file so it can be used in KvMaker

        Args:
            `filename` (str): local of temp file
        
        '''
        __file_new = KVGet_path(f"lang/temp/{self.current_temp_path}/{self.name_file}.py").replace("/", "\\")
        lines = dedent(f"""
            __file__ = r'{__file_new}'
            from lang.KivyApp import SimulateApp\n
        """)

        with open(KVGet_path(f'lang/temp/{self.current_temp_path}/{self.name_file}.py'), mode='w', encoding='utf-8') as file:
            # escreve no arquivo temporário
            file.writelines(lines+self.main_reg_ex.result())

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
                self.create_regex(file.read().split("\n"), path_file)
        

    def get_correct_import(self, local, regex):
        if local.startswith("."):
            relative_name = os.path.split(regex.path)[0].split(self.current_temp_path)[-1].split("/")[-1]
            # print("relative_name -=> ", relative_name)
            local = relative_name + local
        
        ignore_names = {"kivy", "kivymd", "os", "sys", "math", "subprocess", "thread", "kivy_garden"}
        for name in ignore_names:
            if local.startswith(name):
                return None
        
        if local not in self.imports_files and local not in regex.imports:
            return local
        return None


    def unload_kv_files(self):
        '''
        Unload all kv dependencies.
        '''
        
        # from kivy.factory import Factory
        
        files = {'KvMaker.kv', 'style.kv'}
        # print("\nBuiler.rules 0-> \n", list(map(lambda x: x[1].name, Builder.rules)))
        # Builder._clear_matchcache()
        # # print(Factory.classes[x]["name"])
        # print("\nFactory.classes 0-> \n", list(map(lambda x: x, Factory.classes)))

        for path_file in self.local_kivy_files:
            KVLog('Descarregando Kv', path_file)
            Builder.unload_file(path_file)
            if path_file.endswith("load_string_KV.kv"):
                os.remove(path_file)
            
        # for path_file in reversed(Builder.files):
        #     """
        #     set will remove all identically varibles and
        #     if has only False, can be reload {False} else True in {False True}
        #     not reload...
        #     """
        #     if path_file.startswith('KV') or os.path.split(path_file)[1].startswith('KV'):
        #         continue

        #     if sum(map(path_file.endswith, files)) == 0:
        #         KVLog('Descarregando Kv', path_file)
        #         Builder.unload_file(path_file)
        #         if path_file.endswith("load_string_KV.kv"):
        #             os.remove(path_file)

    def reload_py_files(self):
        print("\nself.imports_files -=> ", self.imports_files)
        '''
        Reload all python dependencies.
        '''
        # import_names = []
        for import_builder in reversed(self.imports_files):
            import_path = import_builder.replace(".py", "").replace('/', '.')
            
            print("WILL RELOAD --> ", import_path)
            pymodul = sys.modules.get(import_path)
            if pymodul is not None:
                try:
                    reload_module(pymodul)
                except Exception as err:
                    print("DEU RUIM!! -=: ", err)
        
    def unload_py_files(self):
        if self.current_temp_path == "":
            return None

        for name_module in tuple(sys.modules.keys()):
            module = sys.modules[name_module]
            
            if not hasattr(module, "__file__"):
                continue
            
            if module.__file__ == None:
                print("-- NONE __FILE__ -=> ", module)
                # if module.__name__.startswith("uix"):
                #     print("REMOVENDO MODULO -=> ", module)
                #     del sys.modules[name_module]    
                continue

            if module.__file__.find(self.current_temp_path) != -1:
                print("MODULO -=> ", name_module, module)
                del sys.modules[name_module]


    def reset_main_module(self, first_load_file):
        if self.name_of_class == '':
            return None
        
        print("... RESET MAIN MODULE ...")
        module = get_module(f"lang.temp.{self.current_temp_path}.{self.name_file}")
        print("MAIN MODULE -=> ", module)

        # Builder.unload_file(self.name_of_class)
        if not first_load_file:
            reload_module(module)

        module = get_module(f"lang.temp.{self.current_temp_path}.{self.name_file}")
        widget = getattr(module, self.name_of_class)
        return widget()
        

    def import_widget(self, path_filename, first_load_file, kvmaker_path):
        """
        Get the root Widget of the project being run. 

        Args:
            `path_filename` (str): main file local of the project.
            `first_load_file` (bool): False if this project has imported else True.
            `kvmaker_path` (str): local of KivyMaker app.

        Returns:
            ['py', widget, name_file] if is a python file and was possible to create widget.
            ['kv', width] if is a kv file and was possible to create widget.
        
        """
        KVLog('first_load_file', first_load_file)
        global init_file
        init_file = first_load_file
        KVClock.unschedule_all()
        KVWindow.unbind_all()
        
        
        if not first_load_file:
            self.unload_kv_files()
        else:
            for path_file in self.local_kivy_files:
                KVLog('Descarregando Kv', path_file)
                Builder.unload_file(path_file)
            self.local_kivy_files.clear()
        
            self.unload_py_files()

        self.create_varibles()
        self.path_filename = correct_path(path_filename)
        KVLog('self.path_filename', path_filename)
        self.dirname, file_path = os.path.split(self.path_filename)
        if first_load_file:

            os.chdir(sys_path)

            
            temp_path = KVGet_path(f"lang/temp/{self.current_temp_path}")
            if temp_path in sys.path:
                # it needs to be like that because Android only accepts that
                print("RETIRANDO PATH -=> ", temp_path)
                sys.path.remove(temp_path)

            try:
                shutil.rmtree(KVGet_path(f"lang/temp/{self.current_temp_path}"))
            except Exception as err:
                print("Can't remove all_files -=> ", err)
            
            print("destin -=> ", KVGet_path("lang/temp"))

            self.current_temp_path = get_random_string(random.randint(10, 30))
            shutil.copytree(self.dirname, KVGet_path(f"lang/temp/{self.current_temp_path}"), ignore=ignorePath(".git"))


        temp_path = KVGet_path(f"lang/temp/{self.current_temp_path}")
        if temp_path not in sys.path:
            # it needs to be like that because Android only accepts that
            print("COLOCANDO PATH -=> ", temp_path)
            sys.path.insert(0, temp_path)

        # change python work area
        os.chdir(KVGet_path(f"lang/temp/{self.current_temp_path}"))

        self.files_project(kvmaker_path)
        self.name_file, self.extension = file_path.split('.')

        with open(self.path_filename, mode='r', encoding='utf-8') as file:
            if self.extension == 'py':
                self.main_reg_ex = self.create_regex(file.read().split("\n"), self.path_filename, "main")
                self.change_main_file()
                try:
                    self.read_kvs()

                    # start recursion and parse the all file
                    self.update_imports()

                    if first_load_file == False:
                        self.reload_py_files()
                    
                    widget = self.reset_main_module(first_load_file)
                    if widget == None:
                        return ['Error', 'Seu app não tem nenhuma classe para inicializar']
                    
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
                return ['Error', "\nNão suportamos outros tipos de arquivos, somente:\n - arquivo.py\n - arquivo.kv"]

    def erros(self):
        '''
        Get errors of terminal log

        Returns:
            str: error message.
        '''
        trace = traceback.format_exc()
        err = "ERROR: {}".format(trace)
        return err
