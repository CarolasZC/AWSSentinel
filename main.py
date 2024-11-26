import boto3

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.utils import get_color_from_hex
from botocore.exceptions import ClientError
from resources import colors
from functions import *

class AWSSentinalApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.aws_regions = []
        self.logs = []
        self.aws_access_key = None
        self.aws_secret_key = None

    def build(self):
        # Root layout
        root_layout = BoxLayout(orientation="vertical", padding=[10, 10], spacing=10)

        # Authentication Section
        auth_layout = BoxLayout(orientation="vertical", size_hint=(1, None), spacing=5)

        # AWS Access Key
        key_box = BoxLayout(orientation="horizontal", size_hint=(1, None), height=40, spacing=5)
        key_label = Label(text="AWS Access Key:", size_hint=(0.3, 1), halign="left", valign="middle")
        key_label.bind(size=key_label.setter("text_size"))
        self.access_key_input = TextInput(hint_text="Enter AWS Access Key", multiline=False, size_hint=(0.7, 1))
        key_box.add_widget(key_label)
        key_box.add_widget(self.access_key_input)

        # AWS Secret Key
        secret_box = BoxLayout(orientation="horizontal", size_hint=(1, None), height=40, spacing=5)
        secret_label = Label(text="AWS Secret Key:", size_hint=(0.3, 1), halign="left", valign="middle")
        secret_label.bind(size=secret_label.setter("text_size"))
        self.secret_key_input = TextInput(hint_text="Enter AWS Secret Key", multiline=False, password=True, size_hint=(0.7, 1))
        secret_box.add_widget(secret_label)
        secret_box.add_widget(self.secret_key_input)

        # Add authentication fields to the layout
        auth_layout.add_widget(key_box)
        auth_layout.add_widget(secret_box)
        root_layout.add_widget(auth_layout)

        # Region Selection Section
        region_layout = BoxLayout(orientation="horizontal", size_hint=(1, 0.1), spacing=10)
        self.region_spinner = Spinner(text="Select Region", values=(), size_hint=(0.7, None), height=40)
        fetch_regions_button = Button(text="Fetch Regions", size_hint=(0.3, None), height=40)
        fetch_regions_button.bind(on_press=self.fetch_regions)
        region_layout.add_widget(self.region_spinner)
        region_layout.add_widget(fetch_regions_button)
        root_layout.add_widget(region_layout)

        # Logs Section
        logs_layout = BoxLayout(orientation="vertical", size_hint=(1, 0.6))
        self.logs_label = Label(text="CloudTrail Logs:",size_hint=(1, None), height=30, halign="left", valign="middle", bold=True)
        self.logs_label.bind(size=self.logs_label.setter("text_size"))
        logs_layout.add_widget(self.logs_label)
        scroll_view = ScrollView(size_hint=(1, 1))
        self.logs_container = GridLayout(cols=1, size_hint_y=None, spacing=10)
        self.logs_container.bind(minimum_height=self.logs_container.setter("height"))
        scroll_view.add_widget(self.logs_container)
        logs_layout.add_widget(scroll_view)
        root_layout.add_widget(logs_layout)

        # Fetch Logs Button
        fetch_logs_button = Button(text="Fetch CloudTrail Logs",size_hint=(1, 0.1),color=get_color_from_hex(colors.green))
        fetch_logs_button.bind(on_press=self.fetch_logs)
        root_layout.add_widget(fetch_logs_button)

        return root_layout

    def fetch_regions(self, instance):
        """Fetch AWS regions and populate the spinner."""
        session = aws.authenticate(self)
        if not session:
            return
        try:
            ec2 = session.client("ec2")
            regions = ec2.describe_regions()["Regions"]
            self.aws_regions = [region["RegionName"] for region in regions]
            self.region_spinner.values = self.aws_regions
            self.logs_label.text = "Regions fetched successfully!"
            self.logs_label.color = colors.RGBA_green
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_message = e.response["Error"]["Message"]
            self.logs_label.text = f"Error fetching regions: {error_code} - {error_message}"
            self.logs_label.color = colors.RGBA_red
        except Exception as e:
            self.logs_label.text = f"Unexpected Error in fetching regions: {str(e)}"
            self.logs_label.color = colors.RGBA_red

    def fetch_logs(self, instance):
        """Fetch CloudTrail logs for the selected region."""
        session = aws.authenticate(self)
        if not session:
            return
        selected_region = self.region_spinner.text
        if selected_region == "Select Region":
            self.logs_label.text = "Please select a region first!"
            self.logs_label.color = colors.RGBA_red
            return
        try:
            client = session.client("cloudtrail", region_name=selected_region)
            paginator = client.get_paginator("lookup_events")
            self.logs = []
            for page in paginator.paginate():
                self.logs.extend(page["Events"])
            self.logs_container.clear_widgets()
            for log in self.logs[:20]:
                log_label = Label(text=f"Event: {log['EventName']}", size_hint_y=None, height=30)
                self.logs_container.add_widget(log_label)
            self.logs_label.text = f"Fetched {len(self.logs)} events!"
            self.logs_label.color = colors.RGBA_green
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_message = e.response["Error"]["Message"]
            self.logs_label.text = f"Error fetching logs: {error_code} - {error_message}"
            self.logs_label.color = colors.RGBA_red
        except Exception as e:
            self.logs_label.text = f"Unexpected Error in fetching logs: {str(e)}"
            self.logs_label.color = colors.RGBA_red

if __name__ == "__main__":
    AWSSentinalApp().run()