import os
from lang.KVPath import correct_path

sys_path = correct_path(os.path.split(__file__)[0])

def KVGet_path(local):
    return f'{sys_path}/{local}'

def KVIcons(name, ext='.png'):
    return KVGet_path(f'assets/icons/{name}{ext}')

def KVPhone(name, ext='.png'):
    return KVGet_path(f'assets/smartphones/{name}{ext}')

def KVLog(type_msg, msg):
    print(f'\n|| {type_msg} || --> !! {msg} !!\n')