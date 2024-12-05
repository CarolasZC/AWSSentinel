from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty
from kivy.uix.button import Button

from resources import colors

class LoadingPopup:
    def __init__(self, title="Please Wait", message="Loading..."):
        """Initialize the LoadingPopup with a title and message."""
        self.content = BoxLayout(orientation="vertical", padding=10, spacing=10)
        self.label = Label(color=colors.Yellow ,text=message, font_size="18sp")
        self.content.add_widget(self.label)

        self.popup = Popup(
            title=title,
            content=self.content,
            size_hint=(0.6, 0.4),
            auto_dismiss=False,
        )

    def open(self):
        """Open the popup."""
        self.popup.open()

    def dismiss(self):
        """Dismiss the popup."""
        self.popup.dismiss()

    def update_message(self, message):
        """Update the popup message."""
        self.label.text = message

class DoubleClickableLabel(Label):
    popup = ObjectProperty(None)  # Ensure `popup` is always available

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.register_event_type('on_double_press')
        if "on_double_press" in kwargs:
            self.bind(on_double_press=kwargs["on_double_press"])

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos) and touch.is_double_tap:
            self.dispatch('on_double_press', touch)
            return True
        return super().on_touch_down(touch)

    def on_double_press(self, *args):
        """Override this method in instances to handle double-press events."""
        pass

    def open_trail_detail(self, event, time, username, ip, event_source):
        """Create a popup for displaying event details."""
        layout = BoxLayout(orientation="vertical", padding=10, spacing=10)
        label = Label(
            text=f"Event Source: {event_source}\nTime: {time}\nUsername: {username}\nSource IP: {ip}",
            font_size="15sp",
            size_hint=(1, 0.8),
            color=colors.LimeGreen
        )
        close_btn = Button(text="Close", size_hint=(1, 0.2))
        layout.add_widget(label)
        layout.add_widget(close_btn)

        self.popup = Popup(
            title=f"Event Detail for {event}",
            content=layout,
            size_hint=(0.6, 0.4),
            auto_dismiss=False,
        )
        close_btn.bind(on_press=self.popup.dismiss)
        self.popup.open()