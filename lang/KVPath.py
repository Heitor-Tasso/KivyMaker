
import os

def correct_path(path_filename:str):
    bar_init = '/' if path_filename.startswith('/') else ''
    new_str = []
    for x in path_filename.split('\\'):
        new_str.extend(x.split(r'/'))
    path = [x + '/' for x in new_str[0:-1] if x != '']
    return ''.join([bar_init] + path + [new_str[-1]])

_path_temp = correct_path(os.path.split(__file__)[0]) 

def file_paths(path:str, extensions:tuple):
    files = []
    for diretorio, subpastas, arquivos in os.walk(correct_path(path)):
        for arquivo in arquivos:
            for ex in extensions:
                if arquivo.endswith(ex):
                    files.append(correct_path(diretorio+'/'+arquivo))
                    break
                elif not extensions:
                    files.append(correct_path(diretorio+'/'+arquivo))
                    break
    return files 

def files_paths(path:str):
    files = []
    for diretorio, subpastas, arquivos in os.walk(correct_path(path)):
        for arquivo in arquivos:
            files.append(correct_path(diretorio+'/'+arquivo))
    return files

def search_file_paths(words:tuple, path_filename:str, extensions:tuple):
    researches = []
    for local_file in file_paths(path_filename, extensions):
        try:
            with open(local_file, 'r') as arq:
                for num_line, line in enumerate(arq.readlines()):
                    for word in words:
                        if line.find(word) != -1 or word in line:
                            researches.append((local_file, line, num_line))
                            break
                arq.close()
        except UnicodeDecodeError:
            pass
            #print('Não foi possivel ler o arquivo:\n', local_file)
    return researches
