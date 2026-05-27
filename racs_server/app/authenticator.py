class Authenticator:
    def __init__(self, azure_auth_token: str, google_auth_token: str, aws_auth_token: str):
        self.azure_auth_token = azure_auth_token
        self.google_auth_token = google_auth_token
        self.aws_auth_token = aws_auth_token