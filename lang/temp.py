
__file__ = r'D:\Trabalho\Programacao\Python\Codes\GUI\Kivy\Meus\CloneSpotify\SpotifyClone\Spotify.py'
from lang.KivyApp import SimulateApp
from kivy.config import Config
Config.set('graphics', 'maxfps', '80')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.uix.scrollview import ScrollView
from kivy.uix.floatlayout import FloatLayout
from kivy.lang.builder import Builder
from kivy.graphics.texture import Texture
from kivy.clock import Clock
from kivy.properties import ObjectProperty, StringProperty, ListProperty
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from utils import icon

Builder.load_file('Spotify.kv')

class Body(BoxLayout):
    
    manager = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.playlists = (('Pisadinha', 'assets/playlist-icon/raimundos.jpg'), ('Akon', 'assets/playlist-icon/mamonas.jpg'),
                          ('Indie', 'assets/playlist-icon/redhot.jpg'), ('Emoção', 'assets/playlist-icon/akon.jfif'),
                          ('182', 'assets/playlist-icon/engenheiros.jpg'), ('Fabio', 'assets/playlist-icon/elliot.jfif'))
        for name, local in self.playlists:
            playlist = RecommendedPlayList(name_playlist=name, source=local)
            self.ids.grid.add_widget(playlist)
            for _ in range(2):
                playlist = RecentPlayList(name_playlist=name, source=local)
                self.ids.buscaRecent.add_widget(playlist)
        
        for _ in range(5):
            self.ids.content.add_widget(RootNameNoIcon(self.playlists))
            self.ids.content.add_widget(RootNameIcon(self.playlists))
        
            card = InteractiveCards(
                    'Seus gêneros favoritos',
                    'Pop', get_color_from_hex('#8c67ac'),
                    'Rock', get_color_from_hex('#e51e31')
            )
            self.ids.box_search.add_widget(card)

    def gradient(self, rgba1, rgba2, area):
        colors = []
        maxim = []
        fatores = []
        types = [0, 0, 0, 0]
        
        for i in range(4):
            if rgba1[i] > rgba2[i]:
                ma, mi = rgba1[i], rgba2[i]
            else:
                types[i] = 1
                ma, mi = rgba2[i], rgba1[i]
            fatores.append((ma-mi) / area)
            maxim.append(rgba2[i])
        for _ in range(0, area):
            rgba = []
            for i in range(4):
                rgba.append(round(maxim[i]))
                if types[i] == 1:
                    maxim[i] = maxim[i] - fatores[i]
                else:
                    maxim[i] = maxim[i] + fatores[i]
            colors.extend(rgba)
        return colors

    def create_degrade(self, colors, sizes):
        colors_gradient = []

        for i in reversed(range(1, len(colors))):
            colors_gradient.extend(self.gradient(colors[i-1], colors[i], sizes[i-1]*2))

        texture = Texture.create(size=(2, sum(sizes)), colorfmt='rgba')
        texture.blit_buffer(bytes(colors_gradient), colorfmt='rgba', bufferfmt='ubyte')
        return texture

class Downloads(FloatLayout):
    
    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return False

        app = App.get_running_app()
        app.root.manager.current = 'busca'
        
        return super().on_touch_down(touch)

class SearchDownload(BoxLayout):
    max_pos = ListProperty([0, 0])
    search = ObjectProperty(None)
    box = ObjectProperty(None)
    scroll = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.search = Downloads()
        self.add_widget(self.search)
    
    def change_pos(self, *args):
        if self.scroll is None or self.box is None:
            return

        nx, ny = self.scroll.to_parent(*self.pos)
        if ny > self.max_pos[1]:
            self.search.ids.pesquisa.pos = self.max_pos
            if self.search not in self.box.children:
                self.remove_widget(self.search)
                self.box.pos = self.max_pos
                self.box.add_widget(self.search)
        else:
            self.search.ids.pesquisa.pos = self.pos
            if self.search not in self.children:
                self.box.remove_widget(self.search)
                self.add_widget(self.search)


class InteractiveCards(BoxLayout):
    def __init__(self, root_text, text_card1, color_card1,
                       text_card2, color_card2, **kwargs):
        super().__init__(**kwargs)
        self.ids.lbl.text = root_text
        self.ids.card1.text_card = text_card1
        self.ids.card1.background_color = color_card1
        self.ids.card2.text_card = text_card2
        self.ids.card2.background_color = color_card2

class RootNameIcon(BoxLayout):
    def __init__(self, playlists=[], **kwargs):
        super().__init__(**kwargs)
        self.add_widget(MyScrollView(playlists))

class RootNameNoIcon(BoxLayout):
    def __init__(self, playlists=[], **kwargs):
        super().__init__(**kwargs)
        self.add_widget(MyScrollView(playlists))

class RectanglePlayList(BoxLayout):
    playlist_name = StringProperty('')
    playlist_source = StringProperty('')
    icon_source = StringProperty('')

class MyScrollView(ScrollView):
    def __init__(self, playlists=[], **kwargs):
        super().__init__(**kwargs)
        for name, local in playlists:
            playlist = RectanglePlayList(playlist_name=name, playlist_source=local,
                                         icon_source=icon('send-down-green'))
            self.ids.box.add_widget(playlist)

class RecommendedPlayList(BoxLayout):
    name_playlist = StringProperty('')
    source = StringProperty('')

class RecentPlayList(BoxLayout):
    name_playlist = StringProperty('')
    source = StringProperty('')

class RoudedImage(Widget):
    texture = ObjectProperty(None)
    source = StringProperty('')
    radius = ListProperty([dp(5), 0, 0, dp(5)])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.create_texture, 1)

    def create_texture(self, *args):
        image = Image(
            source=self.source, allow_stretch=True, keep_ratio=False, 
            size_hint=(None, None), size=self.size,
        )
        self.texture = image.texture

class MusicPlayer(SimulateApp):
    def build(self):
        return Body()

if __name__ == '__main__':
    MusicPlayer().run()