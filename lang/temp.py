
__file__ = r'D:\Trabalho\Programacao\Python\Codes\GUI\Kivy\Meus\ScreenLogin\login.py'
from lang.KivyApp import SimulateApp
from kivy.app import App
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.uix.anchorlayout import AnchorLayout

Builder.load_file('login.kv')

class Login(AnchorLayout):
    def __init__(self, **kwargs):
        super(Login, self).__init__(**kwargs)
    
    def size_login(self, box, size):
        w, h = size
        if w <= dp(340):
            box.width = self.width/1.2
        if h >= dp(650):
            box.height = h/1.25

class Program(SimulateApp):
    def build(self):
        return Login()

if __name__ == '__main__':
    Program().run()
