
from lang.path import file_paths, correct_path

def find_builder_python(local, name_varible, local_file=None):
    local = correct_path(local)
    files_with = []
    files_without = []
    paths = file_paths(local, ('.py', '.pyi', '.pyx', '.pxd'))

    for file in paths:
        file = correct_path(file)
        
        site_packages = file.find('site-packages')
        if site_packages != -1:
            import_path_py = file[site_packages+14::]
        else:
            import_path_py = file.split(local)[1]
        new_imported = import_path_py[0:import_path_py.rfind('.')]

        try:
            with open(file, mode='r', encoding='utf-8') as text:
                lines = text.readlines()
                commented = False
                long_string = False
                have_builder = False
                find_aspas = startwith_aspas = -1
                type_aspas = ''

                for numL, line in enumerate(lines):
                    striped = line.strip(' ')
                    
                    if not long_string and not commented:
                        for aspas in ('"""', "'''"):
                            find_aspas = striped.find(aspas)
                            startwith_aspas = striped.startswith(aspas)
                            if find_aspas != -1 or startwith_aspas:
                                type_aspas = aspas
                                break
                    else:
                        find_aspas = striped.find(type_aspas)
                        startwith_aspas = striped.startswith(type_aspas)

                    if startwith_aspas and not commented and not long_string:
                        commented = True
                    elif find_aspas != -1 and not commented and not long_string:
                        long_string = True
                    elif find_aspas != -1 and not commented and long_string:
                        long_string == False
                        type_aspas = ''
                    elif startwith_aspas and commented and not long_string:
                        commented = False
                        type_aspas = ''
                    
                    if not striped.startswith('#'):
                        "this line isn't commented"
                        if not commented:
                            load_file = line.find('Builder.load_file')
                            if load_file == -1:
                                load_file = line.find('Builder.load_string')

                            if load_file != -1:
                                if line[0:load_file].find('#') == -1:
                                    # files += new_imported + ', numL = ' + str(numL+1) + ', \n'
                                    have_builder = True
                                    if new_imported not in files_with:
                                        find_lib = new_imported.find('Lib')
                                        if find_lib != -1:
                                            files_with.append(new_imported[find_lib+4::])
                                        files_with.append(new_imported)
                                        
                if have_builder is False:
                    if new_imported not in files_without:
                        find_lib = new_imported.find('Lib')
                        if find_lib != -1:
                            files_without.append(new_imported[find_lib+4::])
                        files_without.append(new_imported)
                else:
                    have_builder = False
                    
        except (UnicodeDecodeError, FileNotFoundError):
            pass

    files = "_with" + name_varible + " = {\n    "
    tam = 0
    for file in files_with:
        files += f"'{file}', "
        tam += len(file)
        if tam > 70:
            files += '\n    '
            tam = 0
    files += '\n}\n'

    files += "_without" + name_varible + " = {\n    "
    tam = 0
    for file in files_without:
        files += f"'{file}', "
        tam += len(file)
        if tam > 70:
            files += '\n    '
            tam = 0
    files += '\n}\n'

    if local_file is not None:
        with open(local_file, mode='w', encoding='utf-8') as txt:
            txt.writelines(files)
            txt.close()
    return (files, files_with, files_without)


# local = "C:/Users/IO/AppData/Local/Programs/Python/Python39/Lib/site-packages/"
local = "C:/Users/IO/AppData/Local/Programs/Python/Python39/"

find_builder_python(local, '_builds', 'py_local_builds.py')