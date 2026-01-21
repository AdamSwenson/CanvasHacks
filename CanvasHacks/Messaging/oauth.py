"""Tools for authenticating for email via oauth2."""
import json

from msal import ConfidentialClientApplication

from CanvasHacks.Configuration import FileBasedConfiguration
from CanvasHacks.Errors.oauth import OauthError

# oauth for email
OAUTH_TOKEN_FILENAME = "{}/o365_token.json"


class OauthHandler(object):
    """Manages the access token used for authentication
    This includes retrieving it from the server, storing it in a file, and loading from a file
    https://learn.microsoft.com/en-us/exchange/client-developer/legacy-protocols/how-to-authenticate-an-imap-pop-smtp-application-by-using-oauth
    """

    def __init__(self, configuration: FileBasedConfiguration):
        """Should receive FileBasedConfig class. Usually this is by passing it environment.CONFIG """

        self.authority = f"https://login.microsoftonline.com/{configuration.tenant_name}"
        self.scopes = ["https://outlook.office365.com/.default"]

        self.client_credential = configuration.oauth_client_secret
        self.client_id = configuration.oauth_client_id
        self.token_path = OAUTH_TOKEN_FILENAME.format(configuration.private_folder_path)

        self.access_token = None
        self.result ={}

        self._set_up_app()

    def _set_up_app(self):
        """
        Initializes the ConfidentialClientApplication instance
        :return:
        """
        self.app = ConfidentialClientApplication(self.client_id,
                                                 client_credential=self.client_credential,
                                                 authority=self.authority)

    def load_oauth_token(self):
        """Attempts to load the OAuth token from a file
        This is unlikely to be needed given how often tokens expire
        """
        with open(self.token_path, 'r') as f:
            self.result = json.load(f)
            self.access_token = self.result["access_token"]

    def request_access_token(self):
        """Uses the ConfidentialClientApplication instance to request an access token"""
        try:
            # Store response in result so can use in writing
            self.result = self.app.acquire_token_for_client(self.scopes)
        # Catch unexpected catastrophic errors
        except Exception as e:
            raise OauthError(**self.result)

        # Raise error if the access token was not returned
        if 'access_token' not in self.result:
            raise OauthError(f"Failed to obtain an access token \n{self.result}")

        # Successfully retrieved, so set token
        self.access_token = self.result['access_token']

    def save_oauth_token(self):
        """Writes the OAuth token and accompanying information to a file.
        Not usually needed but sometimes useful for testing"""
        with open(self.token_path, 'w') as f:
            json.dump(self.result, f)
            print("Token saved to {}".format(self.token_path))

