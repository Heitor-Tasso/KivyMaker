import threading, sys, os
from kivy.lang import Builder

from kivy.uix.boxlayout import BoxLayout

Builder.load_string("""
<Debug>:
    orientation:'vertical'
    size_hint_y:None
    height:'200dp'
    canvas:
        Color:
            rgba:hex('#282a36')
        Rectangle:
            size:self.size
            pos:self.pos
    BoxLayout:
        size_hint_y:None
        height:'40dp'
        canvas:
            Color:
                rgba:hex('#18204d')
            Rectangle:
                size:self.size
                pos:self.pos
        Label:
            text:'Debug'
            font_size: '20sp'
            bold:True
    ScrollView:
        bar_width: '15dp'
        scroll_type: ['bars']
        BoxLayout:
            size_hint: None, None
            size: self.minimum_width, self.minimum_height    
            padding: '10dp'
            Label:
                id: text_debug
                size_hint:None, None
                size:self.texture_size
                #font_size:'16dp'
                # background_color:hex('#282a36')

""", filename='KVTerminal.kv')

class Debug(BoxLayout):
    def __init__(self, **kwargs):
        super(Debug, self).__init__(**kwargs)

        self._stdout = None
        self._stderr = None
        self._r = None
        self._w = None
        self._thread = None
        self.start()

    def start(self):
        self._stdout = sys.stdout
        self._stderr = sys.stderr
        r, w = os.pipe()
        r, w = os.fdopen(r, 'r'), os.fdopen(w, 'w', 1)
        self._r = r
        self._w = w
        sys.stdout = self._w
        sys.stderr = self._w
        self._thread = threading.Thread(target=self._handler)
        self._thread.start()

    def stop(self):
        self._w.close()
        if self._thread: self._thread.join()
        self._r.close()
        sys.stdout = self._stdout
        sys.stderr = self._stderr

    def _handler(self):
        while not self._w.closed:
            try:
                while True:
                    line = self._r.readline()
                    if not line:
                        break
                    self.print(line)
            except:
                break

    def print(self, s, end=""):
        print(s, file=self._stdout, end=end)
        self.ids.text_debug.text += s
