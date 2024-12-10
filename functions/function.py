import configparser
import telegram
import requests
import os
import json

from xhtml2pdf import pisa
from cryptography.fernet import Fernet

config = configparser.ConfigParser()
config_path = os.path.abspath("./resources/config.ini")
config.read(config_path)
serect = config['General']


class Secret:
    def generate_key():
        return Fernet.generate_key()

    def save_key(key , path="resources/secret.key"):
        os.makedirs(os.path.dirname(path), exist_ok=True)  
        with open("secret.key","wb") as key_file:
            key_file.write(key)

    def load_key(filename="resources/secret.key"):
        if not os.path.exists(filename):
            raise FileNotFoundError(f"The secret key file '{filename}' does not exist.")
        return open(filename,"rb").read()
    
class Notification:
    async def sendNotification(message,type):
        if type =="tg":
            await telegram.Bot(token=serect["tgbotid"]).send_message(chat_id=(serect["tggroupid"]), text=message)

        if type =="slack":
            return requests.post(serect["swebhook"], message)
        
class Data:
    def export_to_pdf(events, filename="event_trail.pdf"):
        
        # Start building the HTML content
        html_content = """
        <html>
        <head>
            <style>
            @page { size: landscape; }
                body { font-family: Arial, sans-serif; }
                h1 { text-align: center; }
                table { table-layout: fixed; width: 100%; border-collapse: collapse; }
                th, td {font-size: 8px ; word-wrap: break-word; overflow: hidden; border: 1px solid #ddd; padding: 5px; text-align: left; text-overflow: ellipsis; }
                th { background-color: #f2f2f2; }   
            </style>
        </head>
        <body>
            <h1>Event Trail Report</h1>
            <table>
                <thead>
                    <tr>
                        <th>Event Name</th>
                        <th>Event Source</th>
                        <th>Event Time</th>
                        <th>User Name</th>
                        <th>IP Address</th>
                    </tr>
                </thead>
                <tbody>
        """

        # Iterate through the events list
        for event in events:
            # Each event is a dictionary; access its keys safely
            cloudtrail_event = event.get("CloudTrailEvent")

            if cloudtrail_event:
                event_details = json.loads(cloudtrail_event)  # Parse CloudTrailEvent JSON

                # Add the event to the HTML table
                html_content += f"""
                    <tr>
                        <td>{event_details.get('eventName', 'Unknown')}</td>
                        <td>{event_details.get('eventSource', 'Unknown')}</td>
                        <td>{event.get('EventTime', 'Unknown')}</td>
                        <td>{event.get("Username",'Unknown')}</td>
                        <td>{event_details.get('sourceIPAddress', 'Unknown')}</td>
                    </tr>
                """

        # Close the HTML tags
        html_content += """
                </tbody>
            </table>
        </body>
        </html>
        """

        # Convert HTML to PDF
        with open(filename, "wb") as pdf_file:
            pisa.CreatePDF(src=html_content, dest=pdf_file)

    def export_to_json(events):
        with open('event_trail.json', 'w', encoding='utf-8') as f:
            json.dump(events, f, ensure_ascii=False, indent=4 ,default=str)
        