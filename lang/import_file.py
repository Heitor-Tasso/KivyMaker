
from lang.py_local_builds import _with_builds, _without_builds
from kivy.lang import Builder
import sys, traceback, os
from kivy.utils import platform

try:
    from importlib import reload, import_module
except:      # for py 2 compatibility
    pass

from lang.reload_module import reset_module
from lang.path import correct_path

if platform == 'android':
    from temp_file import temporari_file

def write_logs(imports_files_builder, local_files, imports_files, local_files_builder):
    with open('varibles.txt', mode='w', encoding='utf-8') as txt:
        valor = 'imports_files_builder = (\n'
        n = 0
        for i in imports_files_builder:
            n += 1
            if n == 1:
                valor += '    '
            valor += i+', '
            if n == 2:
                valor += '\n'
                n = 0

        valor += '\n)\nlocal_files_builder = (\n'
        n = 0
        for i in local_files_builder:
            n += 1
            if n == 1:
                valor += '    '
            valor += i+', '
            if n == 2:
                valor += '\n'
                n = 0

        valor += ')\n\nlocal_files = (\n'
        # n = 0
        for i in local_files:
            # n += 1
            valor += '    '+i+',\n'
            # if n == 2:
            #     valor += '\n'
            #     n = 0

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

    def __init__(self, **kwargs):
        self.create_varibles()

    def create_varibles(self):
        self.local_files = []
        self.imports_files = []
        self.imports_files_builder = []
        self.local_files_builder = []
        self.lines_main_file = []

        self.string_builds = False
        self.have_builder = False
        self.runApp = True
        self.verify_main = False

        self.index_files = 0
        self.index_load_string = 0
        self.index_imports = 0
        self.line_class_app = 0
        self.first_index = 0

        self.name_file = ''
        self.name_file_kv = ''
        self.name_of_class = ''
        self.name_root_func = ''
        self.dirname = ''
        self.extension = ''
        self.read_file = ''

    def update_imports(self):
        locals_files = self.local_files[self.index_files::]
        local_imports = self.imports_files[self.index_files::]
        self.index_files += len(locals_files)
        
        for _import, local in zip(local_imports, locals_files):
            with open(local, mode='r', encoding='utf-8') as text:
                lines_text = text.readlines()
                for numL, line in enumerate(lines_text):
                    self.verify_line(line, numL, lines_text, _import)
                self.have_builder = False
        
        if locals_files:
            self.update_imports()

    def verify_line(self, line, numL, lines, current_local):
        local = ''
        local_words = []

        for name_import in ('from', ' import'):
            index_import = line.find(name_import)

            if index_import != -1:
                if line[0:index_import].find('#') == -1:
                    list_import = line[index_import::].split(' ')

                    if not 'from' in list_import:
                        list_locals = [[y.split(' ') for y in x.split(',')] for x in list_import[1::]]
                        for list_word in list_locals:
                            for words in list_word:
                                if words[0] not in (' ', ''):
                                    correct_word = words[0].split('\n')[0]
                                    if correct_word in _with_builds or correct_word not in _without_builds:
                                        local_words.append(correct_word)

                    elif 'from' in list_import:
                        locals = line[index_import::].split(' ')
                        list_locals = [] if len(locals) < 3 else locals[1].split('.')

                        for word_import in list_locals:
                            if word_import == list_locals[-1]:
                                correct_word = (local + word_import).split('\n')[0]
                                if correct_word in _with_builds or correct_word not in _without_builds:
                                    local_words.append(correct_word)
                                local = ''
                            else:
                                local += f'{word_import}/'

                    for locale in local_words:
                        locale = correct_path(locale)
                        if locale not in self.imports_files:
                            self.update_local_paths(locale)
                
                    local_words.clear()
                    break
            else:
                self.update_build_funcs(line, numL, lines, current_local)
                if '' in {self.name_root_func, self.name_of_class}:
                    self.funcs_class(lines, line, numL)
                self.Start(line)

    def update_local_paths(self, local):
        local_path = None

        for extension in ('.py', '.pyx', '.pyi', '.pxd'):
            if local_path is not None:
                break

            for locale in sys.path:
                locale = correct_path(locale)
                if not locale.endswith('/'):
                    locale += '/'
                try:
                    local_path = locale + local + extension
                    with open(local_path, mode="r", encoding="utf-8") as texto:

                        if local_path not in self.local_files:
                            self.local_files.append(local_path)
                            self.imports_files.append(local)
                        
                        texto.close()
                    break
                except (FileNotFoundError, OSError):
                    local_path = None

    def update_build_funcs(self, line, numL, lines, current_local):
        index_builder = line.find("Builder.load_file")

        if index_builder != -1:
            if line[0:index_builder].find('#') == -1:
                try:
                    name = ''
                    if line.rfind("'") != -1:
                        name = line.split("'")[1]
                    elif line.rfind('"') != -1:
                        name = line.split('"')[1]
                    correct_name = correct_path(name)
                    if correct_name not in self.imports_files_builder:
                        self.imports_files_builder.append(correct_name)
                        self.index_imports += 1

                        if not self.have_builder:
                            self.local_files_builder.append(current_local)
                            self.have_builder = True
                except IndexError:
                    pass
                    #print('ERRO: deixe o local do arquivo explicito!!\n', line)
        else:
            index_builder = line.find("Builder.load_string")

            if index_builder != -1 and not self.string_builds:
                commented = line[0:index_builder].find('#')

                if line.rfind(')') == -1 and commented == -1:
                    self.string_builds = True
                    self.index_load_string = numL
                elif commented == -1:
                    pass
                    #print('build string = ', line.split(','))

            elif index_builder == -1 and self.string_builds:
                """
                    needs changes...
                    if i have a comment in my python files, this function will grab 
                    all Builder.load_string regardless of the comments
                """
                if '"""' in line or "'''" in line:
                    self.string_builds = False
                    all_lines = lines[self.index_load_string:numL+1]
    
    def funcs_class(self, lines, line, num_line):
        if self.string_builds:
            return

        names_line = line.split(' ')
        for num, name in enumerate(names_line):
            if name == 'def':
                name_def = names_line[num+1].split('(')[0]
                if name_def == 'build':
                    for line_file in lines[num_line:]:
                        if line_file.find('return') != -1:
                            "an implementation is needed to get args from the class"
                            line_return_build = line_file.split(' ')[-1]
                            list_name = line_return_build.split('(')[0]
                            if self.name_root_func == '':
                                if list_name.find('Builder.') != -1:
                                    self.name_root_func = line_return_build
                                else:
                                    self.name_root_func = list_name
                            break
        if self.name_of_class == '':
            if line.find('class') != -1 and line.find('App') != -1:
                self.name_of_class = names_line[1].split('(')[0]
                self.line_class_app = num_line
    
    def Start(self, line):
        if self.string_builds or not self.runApp:
            return

        f_name = line.find("__name__")
        f_main = line.find("__main__")
        if f_name != -1 and f_main != -1 and not line.startswith('#'):
            self.verify_main = True

        running = line.find(self.name_of_class + '().run()')        
        if running != -1:
            if not self.verify_main and not line.startswith('#'):
                self.runApp = False

    def contruc_file(self, filename):
        lines = "from lang.KivyApp import SimulateApp\n"
        print(filename)
        with open(filename, mode='w', encoding='utf-8') as file:
            for numL, line in enumerate(self.lines_main_file):
                if numL == self.line_class_app:
                    if line.find('MDApp') != -1: class_app = 'MDApp'
                    else: class_app = 'App'
                    lines += line.replace(class_app, 'SimulateApp') + '\n' 
                else:
                    # if line.find('def build') != -1:
                    #     line = line.replace('build', 'start')
                    lines += line + '\n'
            file.writelines(lines)
    
    def import_package(self, name_file):
        # imported = import_module(name_file)
        if sys.modules.get(name_file) is not None:
            modul = sys.modules.get(name_file)
            reset_module(modul)
        # print('name: ', name_file)
        if platform == 'win':
            imported = import_module(name_file)
            classe = getattr(imported, self.name_of_class)
        else:
            classe = getattr(temporari_file, self.name_of_class)

        return classe()
    
    def unload_files_builder(self, index, dirname):
        # unload dependencies and load again
        index = index - (1 if index > 0 else 0)
        lista = self.imports_files_builder[index::]
        for path_file_kv in reversed(lista):
            new_path = dirname + '/' + path_file_kv
            # print('    descarregou builder of: ', new_path)
            Builder.unload_file(new_path)
    
    def unload_builds_main(self, index, dirname):
        for path_file_kv in self.imports_files_builder[0:index]:
            new_path = dirname + '/' + path_file_kv
            # print('        descarregou builder of: ', new_path)
            Builder.unload_file(new_path)

    def reload_files_builder(self):
        for import_builder in reversed(self.local_files_builder):
            list_import = import_builder.split('/')
            import_path = ''
            for word in list_import:
                import_path += word
                if word != list_import[-1]:
                    import_path += '.'
            # print('    recarregou module of: ', import_path)
            reset_module(sys.modules.get(import_path))

    def import_widget(self, path_filename, first_load_file, reload_app):
        if first_load_file is True:
            if self.dirname in sys.path:
                sys.path.remove(self.dirname)
                
        self.create_varibles()
        path_filename = correct_path(path_filename)
        self.dirname, file_path = os.path.split(path_filename)

        if self.dirname not in sys.path:
            # it needs to be like that because Android only accepts that
            sys.path = [self.dirname] + sys.path

        os.chdir(self.dirname)

        self.name_file, self.extension = file_path.split('.')
        self.name_file_kv = self.name_file + '.kv'

        with open(path_filename, mode='r', encoding='utf-8') as file:
            self.read_file = file.read()
            if self.extension == 'py':
                self.lines_main_file = self.read_file.splitlines()
                try:
                    for numL, line in enumerate(self.lines_main_file):
                        self.verify_line(line, numL, self.lines_main_file, self.name_file)
                    
                    if self.runApp is False:
                        msg = "Não esqueça de colocar no final:\n    if __name__ == '__main__':\n        class().run()\n"
                        file.close()
                        return ['Error', msg]

                    # index of last script imports with Builder from main file
                    self.first_index = self.index_imports 
                    self.update_imports() # to start recursion and parse the main file
                
                    path_temp = correct_path(reload_app.path) + '/temp_file/'
                    name = 'temporari_file'
                    name_file = 'temp_file.' + name
                    self.contruc_file(path_temp + name + '.py')

                    if first_load_file is False:
                        # unload dependencies (Builder)
                        self.unload_files_builder(self.first_index, self.dirname)
                        # reloads all scripts being used (minus the main script)
                        self.reload_files_builder()
                        # need more studies
                        self.unload_builds_main(self.first_index, self.dirname)

                    widget = self.import_package(name_file)

                    write_logs(self.imports_files_builder, self.local_files, self.imports_files, self.local_files_builder)
                    file.close()
                    return  ['py', widget, name_file]

                except Exception:
                    msg = self.erros()
                    file.close()
                    return ['Error', msg]

            elif self.extension == 'kv':
                try:
                    file.close()
                    return ['kv', Builder.load_string(self.read_file, filename=self.name_file_kv)]
                except Exception as error:
                    file.close()
                    return ['Error', str(error)]
            else:
                file.close()
                return ['Error', "Não suportamos outros tipos de arquivos, somente:\n - arquivo.py\n - arquivo.kv"]

    def erros(self):
        type, value, tb = sys.exc_info()
        print(type)
        # erros = traceback.format_list(traceback.extract_tb(tb))
        # err = ''
        # for w in erros:
        #     err += w
        trace = traceback.format_exc()
        err = "ERROR: {}".format(trace)

        line = ''
        for i in err[::-1]:
            line+=i
            n_line = line[::-1]
            if n_line.find('super(') != -1 and n_line.rfind('__init__(') != -1:
                line = "Erro"
                break
        if type == TypeError and line == "Erro":
            err += "\nTente colocar essa classe no arquivo .kv dessa maneira:\n    <NameClass@TypeObject>:"
        return err
