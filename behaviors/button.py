
__all__ = ['ButtonBehavior', 'ToggleButtonBehavior']

from kivy.clock import Clock
from kivy.config import Config
from weakref import ref
from time import time
from kivy.app import App

from kivy.properties import (
    OptionProperty, ObjectProperty,
    BooleanProperty, NumericProperty,
)

class ButtonBehavior(object):
    '''
    This `mixin <https://en.wikipedia.org/wiki/Mixin>`_ class provides
    :class:`~kivy.uix.button.Button` behavior. Please see the
    :mod:`button behaviors module <kivy.uix.behaviors.button>` documentation
    for more information.

    :Events:
        `on_press`
            Fired when the button is pressed.
        `on_release`
            Fired when the button is released (i.e. the touch/click that
            pressed the button goes away).

    '''

    state = OptionProperty('normal', options=('normal', 'down'))
    '''The state of the button, must be one of 'normal' or 'down'.
    The state is 'down' only when the button is currently touched/clicked,
    otherwise its 'normal'.

    :attr:`state` is an :class:`~kivy.properties.OptionProperty` and defaults
    to 'normal'.
    '''

    last_touch = ObjectProperty(None)
    '''Contains the last relevant touch received by the Button. This can
    be used in `on_press` or `on_release` in order to know which touch
    dispatched the event.

    .. versionadded:: 1.8.0

    :attr:`last_touch` is a :class:`~kivy.properties.ObjectProperty` and
    defaults to `None`.
    '''

    min_state_time = NumericProperty(0)
    '''The minimum period of time which the widget must remain in the
    `'down'` state.

    .. versionadded:: 1.9.1

    :attr:`min_state_time` is a float and defaults to 0.035. This value is
    taken from :class:`~kivy.config.Config`.
    '''

    always_release = BooleanProperty(False)
    '''This determines whether or not the widget fires an `on_release` event if
    the touch_up is outside the widget.

    .. versionadded:: 1.9.0

    .. versionchanged:: 1.10.0
        The default value is now False.

    :attr:`always_release` is a :class:`~kivy.properties.BooleanProperty` and
    defaults to `False`.
    '''

    def __init__(self, **kwargs):
        self.register_event_type('on_press')
        self.register_event_type('on_release')
        if 'min_state_time' not in kwargs:
            self.min_state_time = float(Config.get('graphics',
                                                   'min_state_time'))
        super(ButtonBehavior, self).__init__(**kwargs)
        self.__state_event = None
        self.__touch_time = None
        self.fbind('state', self.cancel_event)

    def _do_press(self):
        self.state = 'down'

    def _do_release(self, *args):
        self.state = 'normal'

    def cancel_event(self, *args):
        if self.__state_event:
            self.__state_event.cancel()
            self.__state_event = None

    def on_touch_down(self, touch):
        if super(ButtonBehavior, self).on_touch_down(touch):
            return True
        if touch.is_mouse_scrolling:
            return False
        if not self.collide_point(touch.x, touch.y):
            return False
        if self in touch.ud:
            return False
        touch.grab(self)
        touch.ud[self] = True
        self.last_touch = touch
        self.__touch_time = time()
        self._do_press()
        if App._running_app:
            self.dispatch('on_press')
        return True

    def on_touch_move(self, touch):
        if touch.grab_current is self:
            return True
        if super(ButtonBehavior, self).on_touch_move(touch):
            return True
        return self in touch.ud

    def on_touch_up(self, touch):
        if touch.grab_current is not self:
            return super(ButtonBehavior, self).on_touch_up(touch)
        assert(self in touch.ud)
        touch.ungrab(self)
        self.last_touch = touch

        if (not self.always_release and
                not self.collide_point(*touch.pos)):
            self._do_release()
            return

        touchtime = time() - self.__touch_time
        if touchtime < self.min_state_time:
            self.__state_event = Clock.schedule_once(
                self._do_release, self.min_state_time - touchtime)
        else:
            self._do_release()
        if App._running_app:
            self.dispatch('on_release')
        return True

    def on_press(self):
        pass

    def on_release(self):
        pass

    def trigger_action(self, duration=0.1):
        '''Trigger whatever action(s) have been bound to the button by calling
        both the on_press and on_release callbacks.

        This is similar to a quick button press without using any touch events,
        but note that like most kivy code, this is not guaranteed to be safe to
        call from external threads. If needed use
        :class:`Clock <kivy.clock.Clock>` to safely schedule this function and
        the resulting callbacks to be called from the main thread.

        Duration is the length of the press in seconds. Pass 0 if you want
        the action to happen instantly.

        .. versionadded:: 1.8.0
        '''
        self._do_press()
        self.dispatch('on_press')

        def trigger_release(dt):
            self._do_release()
            self.dispatch('on_release')
        if not duration:
            trigger_release(0)
        else:
            Clock.schedule_once(trigger_release, duration)

class ToggleButtonBehavior(ButtonBehavior):
    '''This `mixin <https://en.wikipedia.org/wiki/Mixin>`_ class provides
    :mod:`~kivy.uix.togglebutton` behavior. Please see the
    :mod:`togglebutton behaviors module <kivy.uix.behaviors.togglebutton>`
    documentation for more information.
    .. versionadded:: 1.8.0
    '''

    __groups = {}

    group = ObjectProperty(None, allownone=True)
    '''Group of the button. If `None`, no group will be used (the button will be
    independent). If specified, :attr:`group` must be a hashable object, like
    a string. Only one button in a group can be in a 'down' state.
    :attr:`group` is a :class:`~kivy.properties.ObjectProperty` and defaults to
    `None`.
    '''

    allow_no_selection = BooleanProperty(True)
    '''This specifies whether the widgets in a group allow no selection i.e.
    everything to be deselected.
    .. versionadded:: 1.9.0
    :attr:`allow_no_selection` is a :class:`BooleanProperty` and defaults to
    `True`
    '''

    def __init__(self, **kwargs):
        self._previous_group = None
        super(ToggleButtonBehavior, self).__init__(**kwargs)

    def on_group(self, *largs):
        groups = ToggleButtonBehavior.__groups
        if self._previous_group:
            group = groups[self._previous_group]
            for item in group[:]:
                if item() is self:
                    group.remove(item)
                    break
        group = self._previous_group = self.group
        if group not in groups:
            groups[group] = []
        r = ref(self, ToggleButtonBehavior._clear_groups)
        groups[group].append(r)

    def _release_group(self, current):
        if self.group is None:
            return
        group = self.__groups[self.group]
        for item in group[:]:
            widget = item()
            if widget is None:
                group.remove(item)
            if widget is current:
                continue
            widget.state = 'normal'

    def _do_press(self):
        if (not self.allow_no_selection and
                self.group and self.state == 'down'):
            return

        self._release_group(self)
        self.state = 'normal' if self.state == 'down' else 'down'

    def _do_release(self, *args):
        pass

    @staticmethod
    def _clear_groups(wk):
        # auto flush the element when the weak reference have been deleted
        groups = ToggleButtonBehavior.__groups
        for group in list(groups.values()):
            if wk in group:
                group.remove(wk)
                break

    @staticmethod
    def get_widgets(groupname):
        '''Return a list of the widgets contained in a specific group. If the
        group doesn't exist, an empty list will be returned.
        .. note::
            Always release the result of this method! Holding a reference to
            any of these widgets can prevent them from being garbage collected.
            If in doubt, do::
                l = ToggleButtonBehavior.get_widgets('mygroup')
                # do your job
                del l
        .. warning::
            It's possible that some widgets that you have previously
            deleted are still in the list. The garbage collector might need
            to release other objects before flushing them.
        '''
        groups = ToggleButtonBehavior.__groups
        if groupname not in groups:
            return []
        return [x() for x in groups[groupname] if x()][:]