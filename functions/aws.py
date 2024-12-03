import boto3
import datetime
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
        
def parse_cloudtrail_event(event):
    """Parse a CloudTrail event and extract key details."""
    try:
        # Extract top-level fields
        event_name = event.get("EventName", "Unknown")
        event_time = event.get("EventTime", "Unknown")
        username = event.get("Username", "Unknown")
        source_ip = event.get("sourceIPAddress", "Unknown")
        
        # Parse nested CloudTrailEvent JSON
        cloudtrail_event = event.get("CloudTrailEvent")
        if cloudtrail_event:
            event_details = json.loads(cloudtrail_event)  # Parse JSON string
            event_time = event_details.get("eventTime", event_time)
            source_ip = event_details.get("sourceIPAddress", source_ip)
            user_identity = event_details.get("userIdentity", {})
            username = user_identity.get("userName", username)

        # Format event_time if it's a datetime
        if isinstance(event_time, datetime.datetime):
            event_time = event_time.strftime("%Y-%m-%d %H:%M:%S")

        return {
            "event_name": event_name,
            "event_time": event_time,
            "username": username,
            "source_ip": source_ip,
        }

    except json.JSONDecodeError:
        print("Error parsing CloudTrailEvent JSON")
        return {
            "event_name": "Unknown",
            "event_time": "Unknown",
            "username": "Unknown",
            "source_ip": "Unknown",
        }