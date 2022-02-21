from kivy.properties import ObjectProperty
from kivy.uix.modalview import ModalView
from kivy.uix.filechooser import FileChooser
from kivy.lang import Builder
from kivy.clock import Clock

""" things that are not explicit in the code:

function "hex" are imported in KvScreen.py
class "ToolBarTop" are imported from KvScreen.kv
"""

Builder.load_string("""
#: import KVIcons KVUtils.KVIcons
#: import KVButtonIcon KVuix.KVIcon.KVButtonIcon
#: import KVAnchorIcon KVuix.KVIcon.KVAnchorIcon

<Chooser>:
    root:None
    FileChooserIconLayout:
    FileChooserListLayout:

<FilesPath>:

    BoxLayout:
        orientation:'vertical'
        TollBarTop:
            KVAnchorIcon:
                KVButtonIcon:
                    source:KVIcons('back')
                    on_press: root.dismiss()
            Widget:
            KVAnchorIcon:
                KVButtonIcon:
                    source:KVIcons('grid')
                    on_press: fc.view_mode = 'icon'
            KVAnchorIcon:
                KVButtonIcon:
                    source:KVIcons('list-play')
                    on_press: fc.view_mode = 'list'
            Widget:
            KVAnchorIcon:
                KVButtonIcon:
                    source:KVIcons('add_white')
                    on_press: fc.load()
        Chooser:
            id: fc

""", filename="KVFilechooser.kv")

class Chooser(FileChooser):
    file = []
    app = ObjectProperty(None)

    def entry_released(self, entry, touch):
        super().entry_released(entry, touch)

        if self.file != self.selection:
            self.file = self.selection
            return None
        
        if self.file:
            self.app.validade_local(self.file[0])
            self.app.charg()
            self.file.clear()

class FilesPath(ModalView):
    opened = False
    def __init__(self, app, path='', **kwargs):
        super().__init__(**kwargs)
        self.ids.fc.app = app
        if path != '':
            self.ids.fc.path = path

    def open(self, *largs, **kwargs):
        if not self.opened:
            self.opened = True
            return super().open(*largs, **kwargs)
        return True
    
    def dismiss(self, *largs, **kwargs):
        if self.opened:
            self.opened = False
            return super().dismiss(*largs, **kwargs)
        return False
