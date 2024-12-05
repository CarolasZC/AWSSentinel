import datetime
import threading

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from botocore.exceptions import ClientError
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.uix.anchorlayout import AnchorLayout

from resources import colors
from resources import components
from functions import *

class AWSSentinalApp(App):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.aws_regions = []
        self.logs = []
        self.loading_popup = None

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

        # # Logs Previous and Next button Section
        # buttons_layout = BoxLayout(orientation='horizontal',size_hint=(1, None), height=50, spacing=10, padding=(10, 10))
        # previous_button = Button(text="Previous", size_hint=(None, 1), width=100)
        # next_button = Button(text="Next", size_hint=(None, 1), width=100)
        # buttons_anchor = AnchorLayout(anchor_x='right', anchor_y='bottom', size_hint=(1, None), height=60,)
        # buttons_layout.add_widget(previous_button)
        # buttons_layout.add_widget(next_button)
        # buttons_anchor.add_widget(buttons_layout)   
        # logs_layout.add_widget(buttons_anchor)

        # Fetch Logs Button
        fetch_logs_button = Button(text="Fetch CloudTrail Logs",size_hint=(1, 0.1),color=colors.LimeGreen)
        fetch_logs_button.bind(on_press=self.fetch_logs)
        root_layout.add_widget(fetch_logs_button)

        return root_layout

    def fetch_regions(self, instance):
        """Start fetching AWS regions in a thread."""
        access_key = self.access_key_input.text.strip()
        secret_key = self.secret_key_input.text.strip()

        if not access_key or not secret_key:
            self.logs_label.text = "Error: Please provide both AWS Access Key and Secret Key."
            self.logs_label.color = colors.Red
            return

        self.loading_popup = components.LoadingPopup(message="Fetching AWS regions...")
        self.loading_popup.open()

        threading.Thread(target=self._fetch_regions_thread , args=(access_key,secret_key)).start()

    def _fetch_regions_thread(self,access_key,secret_key):
        """Threaded method to fetch AWS regions."""
        try:
            session = aws.authenticate(access_key, secret_key)
            if not session:
                Clock.schedule_once(lambda dt: self._update_logs_label("Authentication failed.", colors.Red))
                return

            ec2 = session.client("ec2")
            regions = [region["RegionName"] for region in ec2.describe_regions()["Regions"]]

            # Update UI with regions on the main thread
            Clock.schedule_once(lambda dt: self._update_regions_ui(regions, True))
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_message = e.response["Error"]["Message"]
            Clock.schedule_once(lambda dt: self._update_logs_label(f"Error fetching regions: {error_code} - {error_message}", colors.Red))
        except Exception as e:
            Clock.schedule_once(lambda dt: self._update_logs_label(f"Unexpected Error: {str(e)}", colors.Red))
        finally:
            Clock.schedule_once(lambda dt:self.loading_popup.dismiss())

    def fetch_logs(self, instance):
        """Start fetching CloudTrail logs in a thread."""
        access_key = self.access_key_input.text.strip()
        secret_key = self.secret_key_input.text.strip()
        if not access_key or not secret_key:
            self.logs_label.text = "Error: Please provide both AWS Access Key and Secret Key."
            self.logs_label.color = colors.Red
            return

        selected_region = self.region_spinner.text
        if selected_region == "Select Region":
            self.logs_label.text = "Please select a region first!"
            self.logs_label.color = colors.Red
            return

        self.loading_popup = components.LoadingPopup("Fetching CloudTrail logs...")
        self.loading_popup.open()
        threading.Thread(target=self._fetch_logs_thread, args=(selected_region,access_key,secret_key)).start()

    def _fetch_logs_thread(self, selected_region,access_key,secret_key):
        """Threaded method to fetch CloudTrail logs."""
        end_time = datetime.datetime.now()
        start_time = end_time - datetime.timedelta(days=30)
        try:
            session = aws.authenticate(access_key, secret_key)
            if not session:
                Clock.schedule_once(lambda dt: self._update_logs_label("Authentication failed.", colors.Red))
                return

            client = session.client("cloudtrail", region_name=selected_region)
            paginator = client.get_paginator("lookup_events")
            logs = []
            for page in paginator.paginate(
                LookupAttributes=[
            {
                'AttributeKey': 'ReadOnly',
                'AttributeValue': 'false'
            },
        ],
        StartTime=start_time,EndTime=end_time):
                 logs.extend(page["Events"])
            # Update UI with logs on the main thread
            Clock.schedule_once(lambda dt: self._update_logs_ui(logs, True))
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_message = e.response["Error"]["Message"]
            Clock.schedule_once(lambda dt: self._update_logs_label(f"Error fetching logs: {error_code} - {error_message}", colors.Red))
        except Exception as e:
            error_message = f"Unexpected Error: {str(e)}"
            Clock.schedule_once(lambda dt: self._update_logs_label(error_message, colors.Red))
        finally:
            Clock.schedule_once(lambda dt:self.loading_popup.dismiss())

    def _update_regions_ui(self, regions, success):
        """Update UI with fetched regions or error message."""
        if success:
            self.aws_regions = regions
            self.region_spinner.values = self.aws_regions
            self.logs_label.text = "Regions fetched successfully!"
            self.logs_label.color = colors.LimeGreen
        else:
            self.logs_label.text = regions
            self.logs_label.color = colors.Red

    def _update_logs_ui(self, logs, success):
        """Update UI with fetched logs or error message."""
        if success:
            self.logs = logs
            self.logs_container.clear_widgets()

            for id,log in enumerate(self.logs):
                event_data = aws.parse_cloudtrail_event(id,log)
                # Create labels
                log_label = components.DoubleClickableLabel(
                    text=f"Event Name: {event_data['event_name']}",
                    size_hint_y=None,
                    height=30,
                )
                log_label.on_double_press = lambda *args, event=event_data: log_label.open_trail_detail(
                    event=event['event_name'], time=event['event_time'], username=event['username'], ip=event['source_ip'],event_source=event['event_source']
                )
                # Add to container
                self.logs_container.add_widget(log_label)

            self.logs_label.text = f"Fetched {len(self.logs)} events!"
            self.logs_label.color = colors.LimeGreen
        else:
            self.logs_label.text = logs
            self.logs_label.color = colors.Red

    def _update_logs_label(self, message, color):
        """Update logs label with a message and color."""
        self.logs_label.text = message
        self.logs_label.color = color

if __name__ == "__main__":
    AWSSentinalApp().run()