import boto3

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