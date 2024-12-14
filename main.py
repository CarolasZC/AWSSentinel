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
from kivy.core.window import Window

from resources import colors
from resources import components
from functions import *

class AWSSentinalApp(App):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.aws_regions = []
        self.logs = []
        self.filtered_events = []
        self.loading_popup = None
        self.current_page = 0 
        self.logs_per_page = 10

    def build(self):
        Window.clearcolor=colors.DarkBlueGray
        # Width , Height
        Window.size = (800, 600)

        # Root layout
        root_layout = BoxLayout(
            orientation="vertical", padding=15, spacing=20
        )

        # Authentication Section
        auth_layout = BoxLayout(
            orientation="vertical", size_hint=(1, None), spacing=10
        )

        # AWS Access Key
        key_box = BoxLayout(
            orientation="horizontal", size_hint=(1, None), height=40, spacing=5
        )
        key_label = Label(
            text="AWS Access Key:", size_hint=(0.3, 1), halign="left", valign="middle"
        )
        key_label.bind(size=key_label.setter("text_size"))
        self.access_key_input = TextInput(
            hint_text="Enter AWS Access Key", multiline=False, size_hint=(0.7, 1)
        )
        key_box.add_widget(key_label)
        key_box.add_widget(self.access_key_input)

        # AWS Secret Key
        secret_box = BoxLayout(
            orientation="horizontal", size_hint=(1, None), height=40, spacing=5
        )
        secret_label = Label(
            text="AWS Secret Key:", size_hint=(0.3, 1), halign="left", valign="middle"
        )
        secret_label.bind(size=secret_label.setter("text_size"))
        self.secret_key_input = TextInput(
            hint_text="Enter AWS Secret Key", multiline=False, password=True, size_hint=(0.7, 1)
        )
        secret_box.add_widget(secret_label)
        secret_box.add_widget(self.secret_key_input)

        # Add authentication fields to the layout
        auth_layout.add_widget(key_box)
        auth_layout.add_widget(secret_box)
        root_layout.add_widget(auth_layout)

        # Region Selection Section
        region_layout = BoxLayout(
            orientation="horizontal", size_hint=(1, 0.1), spacing=10
        )
        self.region_spinner = Spinner(
            text="Select Region", values=(), size_hint=(0.7, None), height=40
        )
        self.region_spinner.bind(
            on_release=lambda instance: setattr(instance._dropdown, 'max_height', "200dp")
        )
        fetch_regions_button = Button(
            text="Fetch Regions", size_hint=(0.3, None), height=40
        )
        fetch_regions_button.bind(on_press=self.fetch_regions)
        region_layout.add_widget(self.region_spinner)
        region_layout.add_widget(fetch_regions_button)
        root_layout.add_widget(region_layout)

        # Logs Section
        logs_layout = components.ColoredBoxLayout(
            bg_color=colors.LightGray, orientation="vertical", padding=10 , spacing=5
        )
        logs_label_with_filter_layout = BoxLayout(
            orientation="horizontal",size_hint=(1, None), height=30
        )
        self.logs_label = Label(
            text="CloudTrail Logs:",size_hint=(1, None), height=30, halign="left", valign="middle", bold=True, padding=[10,0,0,0]
        )
        self.filter_event_input = TextInput(
            hint_text="Filter Event Log By Event Name", multiline=False, size_hint=(0.5, 1)
        )
        self.filter_event_input.bind(on_text_validate=self.filter_logs)
        self.logs_label.bind(size=self.logs_label.setter("text_size"))
        logs_label_with_filter_layout.add_widget(self.logs_label)
        logs_label_with_filter_layout.add_widget(self.filter_event_input)
        logs_layout.add_widget(logs_label_with_filter_layout)

        scroll_view = ScrollView(size_hint=(1, 1))
        self.logs_container = GridLayout(
            cols=1, size_hint_y=None
        )
        self.logs_container.bind(minimum_height=self.logs_container.setter("height"))
        scroll_view.add_widget(self.logs_container)
        logs_layout.add_widget(scroll_view)
        root_layout.add_widget(logs_layout)

        # Logs Previous and Next button Section
        buttons_layout = BoxLayout(
            orientation='horizontal', spacing=10, size_hint=(None, None), height=40
        )
        self.previous_button = Button(
            text="Previous", size_hint=(None, 1), width=100, disabled=True
        )
        self.next_button = Button(
            text="Next", size_hint=(None, 1), width=100, disabled=False
        )
        self.previous_button.bind(on_press=self.go_to_previous_page)
        self.next_button.bind(on_press=self.go_to_next_page)
        buttons_layout.add_widget(self.previous_button)
        buttons_layout.add_widget(self.next_button)
        buttons_anchor = AnchorLayout(
           anchor_x='right', anchor_y='bottom', size_hint=(0.85, None), height=60
        )
        buttons_anchor.add_widget(buttons_layout)
        logs_layout.add_widget(buttons_anchor)

        # Fetch Logs Button
        pagination_layout = BoxLayout(
            orientation="horizontal", size_hint=(1, None), height=40
        )
        fetch_logs_button = Button(
            text="Fetch CloudTrail Logs",size_hint=(0.6, 0.8),color=colors.LimeGreen, padding=10
        )
        self.export_logs_button = Spinner(
            text="Select Export Logs Type",values=['JSON','PDF'],size_hint=(0.6, 0.8),color=colors.LimeGreen, padding=10
        )
        fetch_logs_button.bind(on_press=self.fetch_logs)
        self.export_logs_button.bind(on_press=lambda insatnce: self.export_type(
            logs=self.logs, format=self.export_logs_button.text
        ))
        pagination_layout.add_widget(fetch_logs_button)
        pagination_layout.add_widget(self.export_logs_button)
        root_layout.add_widget(pagination_layout)

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
            Clock.schedule_once(lambda dt: self._update_logs_ui(logs, True,self.current_page))
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_message = e.response["Error"]["Message"]
            Clock.schedule_once(lambda dt: self._update_logs_label(f"Error fetching logs: {error_code} - {error_message}", colors.Red))
        except Exception as e:
            error_message = f"Unexpected Error: {str(e)}"
            Clock.schedule_once(lambda dt: self._update_logs_label(error_message, colors.Red))
        finally:
            Clock.schedule_once(lambda dt:self.loading_popup.dismiss())

    def _update_logs_ui(self, logs, success,start_index):
        """Update UI with fetched logs or error message."""
        if success:
            self.logs = logs
            self.logs_container.clear_widgets()

            logs_to_display = self.filtered_events if self.filtered_events else self.logs
            start_index = self.current_page * self.logs_per_page
            end_index = start_index + self.logs_per_page
            paginated_logs = logs_to_display[start_index:end_index]

            for id,log in enumerate(paginated_logs, start=start_index):
                event_data = aws.parse_cloudtrail_event(id=id, event=log)
                # Create labels
                log_label = components.DoubleClickableLabel(
                    text=f"Event Name: {event_data['event_name']} | Time: {event_data['event_time']}",
                    size_hint_y=None,
                    font_size="15dp",
                    height=30,
                    padding= [0,5]
                )
                log_label.on_double_press = lambda *args, event=event_data: log_label.open_trail_detail(
                    event=event['event_name'], time=event['event_time'], username=event['username'], ip=event['source_ip'],event_source=event['event_source']
                )
                # Add to container
                self.logs_container.add_widget(log_label)

            total_pages = (len(logs_to_display) - 1) // self.logs_per_page + 1
            self.logs_label.text = f"Fetched {len(logs_to_display)} events! Page: {self.current_page + 1}/{total_pages}"
            self.logs_label.color = colors.LimeGreen

            self.previous_button.disabled = self.current_page == 0
            self.next_button.disabled = self.current_page + 1 >= total_pages
        else:
            self.logs_label.text = logs
            self.logs_label.color = colors.Red
            
    def _update_logs_label(self, message, color):
        """Update logs label with a message and color."""
        self.logs_label.text = message
        self.logs_label.color = color

    def export_type(self,logs,format):
        if logs and logs !='':
            self.loading_popup = components.LoadingPopup(message="Exporting event logs...")
            self.loading_popup.open()

            if format=="PDF":
                function.Data.export_to_pdf(logs)
                self.logs_label.text = "Logs successfully exported as PDF."
                self.logs_label.color = colors.LimeGreen
            elif format =="JSON":
                function.Data.export_to_json(logs)
                self.logs_label.text = "Logs successfully exported as JSON."
                self.logs_label.color = colors.LimeGreen
            else:
                self.logs_label.text = "Error: Unsupported export type selected."
                self.logs_label.color = colors.Red
                
            self.export_logs_button.text = "Select Export Logs Type" 
            self.loading_popup.dismiss()
        else:
            self.logs_label.text = "Error: No logs are available."
            self.logs_label.color = colors.Red

    def filter_logs(self,instance):
        input_text = instance.text.strip()
        if not input_text:
            self.filtered_events = []
            self._fetch_logs_thread(selected_region=self.region_spinner.text,access_key=self.access_key_input.text,secret_key=self.secret_key_input.text)
        else:
            self.filtered_events =aws.filter_trail_by_event_name(self.logs, input_text)
            self._update_logs_ui(logs=self.filtered_events, success=True)      
    
    def go_to_previous_page(self, instance):
        logs_to_display = self.filtered_events if self.filtered_events else self.logs
        if self.current_page > 0:
            self.current_page -= 1
            self._update_logs_ui(logs=logs_to_display,success=True,start_index=self.current_page)

    def go_to_next_page(self, instance):
        logs_to_display = self.filtered_events if self.filtered_events else self.logs
        total_pages = (len(logs_to_display) - 1) // self.logs_per_page + 1

        if self.current_page + 1 < total_pages:
            self.current_page += 1
            self._update_logs_ui(logs=logs_to_display,success=True,start_index=self.current_page)
            
if __name__ == "__main__":
    AWSSentinalApp().run()