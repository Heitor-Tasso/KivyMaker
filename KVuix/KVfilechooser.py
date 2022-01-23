from kivy.uix.modalview import ModalView
from kivy.uix.filechooser import FileChooser
from kivy.lang import Builder
from kivy.clock import Clock

""" things that are not explicit in the code:

function "hex" are imported in KvScreen.py
class "ToolBarTop" are imported from KvScreen.kv
class "AnchorIcon" are imported from KvScreen.kv
"""

Builder.load_string("""

<Chooser>:
    FileChooserIconLayout:
    FileChooserListLayout:

<FilesPath>:
    _icons:app.root2._icons
    BoxLayout:
        orientation: 'vertical'
        TollBarTop:
            AnchorIcon:
                KVButtonIcon:
                    icon_source:root._icons+'back.png'
                    on_press: root.dismiss()
            Widget:
            AnchorIcon:
                KVButtonIcon:
                    icon_source:root._icons+'grid.png'
                    on_press: fc.view_mode = 'icon'
            AnchorIcon:
                KVButtonIcon:
                    icon_source:root._icons+'list-play.png'
                    on_press: fc.view_mode = 'list'
            Widget:
            AnchorIcon:
                KVButtonIcon:
                    icon_source:root._icons+'add_white.png'
                    on_press: fc.load()
            
                
        Chooser:
            id: fc

""", filename="KVfilechooser.kv")

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
