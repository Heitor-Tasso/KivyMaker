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
    app = None

    def load(self, *args):
        if self.file:
            self.app.validade_local(self.file[0])
            self.app.charg()
            self.file = []

    def entry_released(self, entry, touch):
        if self.file == self.selection:
            Clock.schedule_once(self.load)
        else:
            self.file = self.selection
        return super().entry_released(entry, touch)

class FilesPath(ModalView):
    def __init__(self, app, path='', **kwargs):
        super().__init__(**kwargs)
        self.ids.fc.app = app
        if path != '':
            self.ids.fc.path = path
