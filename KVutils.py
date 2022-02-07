import os
from lang.KVPath import correct_path

sys_path = correct_path(os.path.split(__file__)[0])

def KVget_path(local):
    return f'{sys_path}/{local}'

def KVicons(name, ext='.png'):
    return KVget_path(f'assets/icons/{name}{ext}')

def KVphone(name, ext='.png'):
    return KVget_path(f'assets/smartphones/{name}{ext}')