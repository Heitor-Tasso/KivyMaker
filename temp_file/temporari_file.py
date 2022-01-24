
__file__ = r'D:\Trabalho\Programacao\Python\Codes\GUI\Kivy\Meus\Pizzaria\PizzaManagement\PizzaOrder\main.py'
from lang.KivyApp import SimulateApp

' ---------------------------------------------------------------------------------------------- '
import os, sys
"""
    seta o diretório de trabalho para o arquivo principal
    porque em utils, a função "icon" retorna o diretório dos icons,
    se o os.getcwd() não estiver apontando para o diretório desse arquivo,
    ele vai retornar o local errado.
"""
ph, fl = os.path.split(__file__)

os.chdir(ph) # change local work to this this

ph = ph[0:ph.rfind('\\')] # get top path of project
"""
    para poder importar arquivos da pasta anterior
    fiz dessa forma para reutilizar arquivos nos projetos
    depois vai ser necessário passar essas pastas para dentro de cada projeto quando for compilar
"""
if ph not in sys.path:
    sys.path.insert(0, ph)
' ---------------------------------------------------------------------------------------------- '

from kivy.app import App
from ScreenPizzas import ScreenPizza

class HandleOrderFood(SimulateApp):
    def build(self):
        return ScreenPizza()

if __name__ == '__main__':
    ""