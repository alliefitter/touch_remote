from abc import abstractmethod, ABC
from pathlib import Path
from typing import Optional

from getmac import get_mac_address
from kivy.app import App
from kivy.input import MotionEvent
from kivy.properties import NumericProperty
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from lgtv_remote.adapter import WebOSClientAdapter
from lgtv_remote.settings import Settings, TvSettings
from pywebostv.controls import SystemControl, InputControl, MediaControl, ApplicationControl
from pywebostv.model import Application
from wakeonlan import send_magic_packet


class WebOsButton(Button):
    font_name = 'Ubuntu Mono Nerd Font Complete Mono'
    font_size = NumericProperty(64)

    def __init__(self, adapter: WebOSClientAdapter, **kwargs):
        self.adapter = adapter
        super().__init__(**kwargs)
        self._control = None

    @property
    @abstractmethod
    def command(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def control(self):
        raise NotImplementedError

    def on_press(self):
        try:
            getattr(self.control, self.command.lower())()
        except OSError as e:
            print(e)


class SystemButton(WebOsButton):
    @property
    @abstractmethod
    def command(self) -> str:
        raise NotImplementedError

    @property
    def control(self):
        if self._control is None:
            self._control = SystemControl(self.adapter.create(str(Path().home() / '.lgtv.yaml'), 'living_room'))

        return self._control


class MediaButton(WebOsButton):
    @property
    @abstractmethod
    def command(self) -> str:
        raise NotImplementedError

    @property
    def control(self):
        if self._control is None:
            self._control = MediaControl(self.adapter.create(str(Path().home() / '.lgtv.yaml'), 'living_room'))

        return self._control


class ApplicationButton(WebOsButton):
    @property
    @abstractmethod
    def command(self) -> str:
        raise NotImplementedError

    @property
    def control(self):
        if self._control is None:
            self._control = ApplicationControl(self.adapter.create(str(Path().home() / '.lgtv.yaml'), 'living_room'))

        return self._control

    def on_press(self):
        try:
            self.control.launch(Application({'id': self.command}))
        except OSError as e:
            print(e)


class InputButton(WebOsButton):
    @property
    @abstractmethod
    def command(self) -> str:
        raise NotImplementedError

    @property
    def control(self):
        if self._control is None:
            self._control = InputControl(self.adapter.create(str(Path().home() / '.lgtv.yaml'), 'living_room'))
            self._control.connect_input()

        return self._control


class PowerOn(Button):
    text = '⏻'
    font_name = 'Ubuntu Mono Nerd Font Complete Mono'
    font_size = NumericProperty(64)

    def __init__(self, settings: TvSettings, **kwargs):
        self.settings = settings
        super().__init__(**kwargs)

    def on_press(self):
        send_magic_packet(get_mac_address(ip=self.settings.host))


class PowerOff(SystemButton):
    text = '⭘'

    @property
    def command(self) -> str:
        return 'power_off'


class PowerGrid(GridLayout):
    cols = NumericProperty(2)

    def __init__(self, settings: Settings, adapter: WebOSClientAdapter, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(PowerOn(settings.get('living_room')))
        self.add_widget(PowerOff(adapter))


class VolumeUp(MediaButton):
    text = 'ﱛ'

    @property
    def command(self) -> str:
        return 'volume_up'


class VolumeDown(MediaButton):
    text = 'ﱜ'

    @property
    def command(self) -> str:
        return 'volume_down'


class Rewind(MediaButton):
    text = '丹'

    @property
    def command(self) -> str:
        return 'rewind'


class Pause(MediaButton):
    text = ''

    @property
    def command(self) -> str:
        return 'pause'


class Play(MediaButton):
    text = '喇'

    @property
    def command(self) -> str:
        .0

        return 'play'


class FastForward(MediaButton):
    text = ''

    @property
    def command(self) -> str:
        return 'fast_forward'


class PlayControlsGrid(GridLayout):
    cols = NumericProperty(4)

    def __init__(self, adapter: WebOSClientAdapter, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(Rewind(adapter))
        self.add_widget(Pause(adapter))
        self.add_widget(Play(adapter))
        self.add_widget(FastForward(adapter))


class VolumeGrid(GridLayout):
    cols = NumericProperty(1)

    def __init__(self, adapter: WebOSClientAdapter, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(VolumeUp(adapter))
        self.add_widget(VolumeDown(adapter))


class Home(InputButton):
    text = 'ﳐ'

    @property
    def command(self) -> str:
        return 'home'


class Back(InputButton):
    text = ''

    @property
    def command(self) -> str:
        return 'back'


class Up(InputButton):
    text = ''

    @property
    def command(self) -> str:
        return 'up'


class Left(InputButton):
    text = ''

    @property
    def command(self) -> str:
        return 'left'


class Right(InputButton):
    text = ''

    @property
    def command(self) -> str:
        return 'right'


class Down(InputButton):
    text = ''

    @property
    def command(self) -> str:
        return 'down'


class Ok(InputButton):
    text = 'Ok'

    @property
    def command(self) -> str:
        return 'ok'


class Mute(MediaButton):
    text = 'ﱝ'

    @property
    def command(self) -> str:
        return 'mute'


class SettingsApp(ApplicationButton):
    text = '漣'

    @property
    def command(self) -> str:
        return 'com.palm.app.settings'


class DPad(GridLayout):
    cols = NumericProperty(3)

    def __init__(self, adapter: WebOSClientAdapter, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(Back(adapter))
        self.add_widget(Up(adapter))
        self.add_widget(Home(adapter))
        self.add_widget(Left(adapter))
        self.add_widget(Ok(adapter))
        self.add_widget(Right(adapter))
        self.add_widget(Mute(adapter))
        self.add_widget(Down(adapter))
        self.add_widget(SettingsApp(adapter))


class VolumeAndPowerGrid(GridLayout):
    cols = NumericProperty(2)

    def __init__(self, adapter: WebOSClientAdapter, settings: Settings, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(PowerGrid(settings, adapter))
        self.add_widget(VolumeGrid(adapter))


class LeftGrid(GridLayout):
    cols = NumericProperty(1)

    def __init__(self, adapter: WebOSClientAdapter, settings: Settings, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(VolumeAndPowerGrid(adapter, settings))
        self.add_widget(PlayControlsGrid(adapter))


class TouchRemoteApp(App):
    def build(self):
        layout = GridLayout(cols=2)
        layout.height = layout.minimum_height
        settings = Settings()
        adapter = WebOSClientAdapter(settings)
        settings.load(str(Path().home() / '.lgtv.yaml'))
        layout.add_widget(LeftGrid(adapter, settings))
        layout.add_widget(DPad(adapter))
        return layout


if __name__ == "__main__":
    TouchRemoteApp().run()
