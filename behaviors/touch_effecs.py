__all__ = ['EffectBehavior', ]

from kivy.graphics import (
    CanvasBase, Color,
    Ellipse, ScissorPush,
    ScissorPop, RoundedRectangle,
)
from kivy.graphics.stencil_instructions import (
    StencilPop, StencilPush,
    StencilUnUse, StencilUse,
)
from kivy.properties import (
    ListProperty, NumericProperty,
    StringProperty,
)

from kivy.uix.relativelayout import RelativeLayout
from kivy.animation import Animation
from kivy.metrics import dp

class EffectBehavior(object):
    #Size Ellipse
    radius_ellipse_default = NumericProperty(dp(10))
    radius_ellipse = NumericProperty(dp(10))

    #Type transition
    transition_in = StringProperty('in_cubic')
    transition_out = StringProperty('out_quad')
    #Duration of transition
    duration_in = NumericProperty(0.3)
    duration_out = NumericProperty(0.2)

    #To know the touch.pos of the widget
    touch_pos = ListProperty([0, 0])
    #Color background_effect
    effect_color = ListProperty([1, 1, 1, 0.5])

    #To know if is a Rouded or Rectangle...
    type_button = StringProperty('Rounded')
    #radius if Rounded
    radius_effect = ListProperty([dp(10), dp(10), dp(10), dp(10)])

    def __init__(self, **kwargs):
        super(EffectBehavior, self).__init__(**kwargs)
        self.radius_ellipse_default = self.radius_ellipse

        self.ripple_pane = CanvasBase()
        self.canvas.add(self.ripple_pane)
        self.bind(touch_pos=self.set_ellipse,
                  radius_ellipse=self.set_ellipse)
        self.bind(pos=self.draw_effect, size=self.draw_effect)

        self.ripple_ellipse = None
        self.ripple_rectangle = None
        self.ripple_col_instruction = None

    def ripple_show(self, touch):
        Animation.cancel_all(self, 'radius_ellipse', 'effect_color')
        if isinstance(self, RelativeLayout):
            pos_x, pos_y = self.to_window(*self.pos)
            self.touch_pos = (touch.x-pos_x, touch.y-pos_y)
        else:
            self.touch_pos = (touch.x, touch.y)
        
        self.draw_effect()

        anim = Animation(
            radius_ellipse=(max(self.size)*2),
            t=self.transition_in,
            effect_color=self.effect_color,
            duration=self.duration_in,
        )
        anim.start(self)

    def draw_effect(self, *args):
        if self.ripple_pane is None:
            return None

        if self.ripple_ellipse is not None:
            self.ripple_pane.clear()
        else:
            self.reset_CanvasBase()

        with self.ripple_pane:
            if self.type_button == 'Rounded':
                StencilPush()
                self.ripple_rectangle = RoundedRectangle(
                    size=self.size, pos=self.pos,
                    radius=self.radius_effect[::-1],
                )
                StencilUse()
                self.ripple_col_instruction = Color(rgba=self.effect_color)
                self.ripple_ellipse = Ellipse(
                    size=(self.radius_ellipse for _ in range(2)),
                    pos=(x-self.radius_ellipse/2 for x in self.touch_pos),
                )
                StencilUnUse()
                self.ripple_rectangle = RoundedRectangle(
                    size=self.size, pos=self.pos, 
                    radius=self.radius_effect[::-1],
                )
                StencilPop()

            elif self.type_button == 'Rectangle':
                ScissorPush(pos=self.pos, size=self.size)
                self.ripple_col_instruction = Color(rgba=self.effect_color)
                self.ripple_ellipse = Ellipse(
                    size=(self.radius_ellipse for _ in range(2)),
                    pos=(x-self.radius_ellipse/2 for x in self.touch_pos),
                )
                ScissorPop()

    def ripple_fade(self):
        Animation.cancel_all(self, 'radius_ellipse', 'effect_color')
        anim = Animation(
            radius_ellipse=max(self.size)*2,
            effect_color=self.effect_color,
            t=self.transition_out,
            duration=self.duration_out
        )
        anim.bind(on_complete=self.reset_CanvasBase)
        anim.start(self)

    def set_ellipse(self, instance, value):
        if not self.ripple_ellipse:
            return None

        self.ripple_ellipse.size = (self.radius_ellipse for _ in range(2))
        self.ripple_ellipse.pos = (x-self.radius_ellipse/2 for x in self.touch_pos)
    
    def on_touch_up(self, touch):
        self.ripple_rectangle = None
        self.ripple_ellipse = None
        return super(EffectBehavior, self).on_touch_up(touch)

    def reset_CanvasBase(self, *args):
        self.radius_ellipse = self.radius_ellipse_default
        self.ripple_pane.clear()
