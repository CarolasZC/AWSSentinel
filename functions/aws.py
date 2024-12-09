import boto3
import json

from botocore.exceptions import NoCredentialsError, PartialCredentialsError

def authenticate(access,secret):
        """Authenticate using AWS credentials."""
        try:
            session = boto3.session.Session(
                aws_access_key_id=access,
                aws_secret_access_key=secret,
                region_name="us-east-1"
            )
            return session
        except (NoCredentialsError, PartialCredentialsError) as e:
            return None
        
def parse_cloudtrail_event(id,event):
    """Parse a CloudTrail event and extract key details."""
    try:
        # Extract top-level fields
        event_name = ""
        event_source = ""
        event_time = ""
        username = ""
        source_ip = ""
        
        # Parse nested CloudTrailEvent JSON
        cloudtrail_event = event.get("CloudTrailEvent")
        username = event.get("Username",username)
        event_time = event.get("EventTime",event_time)
        if cloudtrail_event:
            event_details = json.loads(cloudtrail_event)  # Parse JSON string
            event_name = event_details.get("eventName", event_name)
            event_source = event_details.get("eventSource", event_source)
            source_ip = event_details.get("sourceIPAddress", source_ip)

        return {
            "event_name": event_name,
            "event_source": event_source,
            "event_time": event_time,
            "username": username,
            "source_ip": source_ip,
        }

    except json.JSONDecodeError:
        print("Error parsing CloudTrailEvent JSON")
        return {
            "event_name": "Unknown",
            "event_source": "Unknown",
            "event_time": "Unknown",
            "username": "Unknown",
            "source_ip": "Unknown",
        }

def filter_trail_by_event_name(logs,logs_model, text):
    logs_model.clear()
    if text != None or text != '':
        logs_model = [log for log in logs if text.lower() in log.get('event_name', '').lower()]
    else:
         logs_model = logs
    return logs_model