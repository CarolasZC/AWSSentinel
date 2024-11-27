from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout

class LoadingPopup:
    def __init__(self, title="Please Wait", message="Loading..."):
        """Initialize the LoadingPopup with a title and message."""
        self.content = BoxLayout(orientation="vertical", padding=10, spacing=10)
        self.label = Label(text=message, font_size="18sp")
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

