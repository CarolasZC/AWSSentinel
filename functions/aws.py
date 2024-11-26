import boto3

from botocore.exceptions import NoCredentialsError, PartialCredentialsError

from resources import colors

def authenticate(self):
        """Authenticate using AWS credentials."""
        self.aws_access_key = self.access_key_input.text.strip()
        self.aws_secret_key = self.secret_key_input.text.strip()
        if not self.aws_access_key or not self.aws_secret_key:
            self.logs_label.text = "Error: Please provide both AWS Access Key and Secret Key."
            self.logs_label.color = colors.RGBA_red
            return None
        try:
            session = boto3.session.Session(
                aws_access_key_id=self.aws_access_key,
                aws_secret_access_key=self.aws_secret_key,
            )
            return session
        except (NoCredentialsError, PartialCredentialsError) as e:
            self.logs_label.text = f"Authentication failed: {e}"
            self.logs_label.color = colors.RGBA_red
            return None