"""Tools for authenticating for email via oauth2"""

from msal import PublicClientApplication, ConfidentialClientApplication

from CanvasHacks.Configuration import Configuration
from CanvasHacks.Errors.oauth import OauthError


# https://pypi.org/project/msal/

# oauth for email
OAUTH_TOKEN_FILENAME = "{}/o365_token.txt"


class OauthHandler(object):
    """Manages the access token used for authentication """

    def __init__(self, configuration):
        """Should receive FileBasedConfig class """
        self.result = None  # It is just an initial value. Please follow instructions below.

        self.client_id = configuration.oauth_client_id

        self.authority = f"https://login.microsoftonline.com/{configuration.tenant_name}"
        self.client_credential = configuration.oauth_client_secret

        # scopes = ['/.default']
        # scopes = ['SMTP.Send',  '/.default']
        self.scopes = ['api://6eb9fab9-78fa-48bf-bce2-4e6f1ccb4bb0/.default']

        self.token_path = OAUTH_TOKEN_FILENAME.format(configuration.private_folder_path)

        self.access_token = None

    def _set_up_app(self):
        """
        Initializes the ConfidentialClientApplication instance
        :return:
        """
        self.app = ConfidentialClientApplication(self.client_id,
                                                 client_credential=self.client_credential,
                                                 authority=self.authority)

    def load_oauth_token(self):
        """Attempts to load the OAuth token from a file"""
        with open(self.token_path, 'r') as f:
            self.access_token = f.read()

    def request_access_token(self):
        """Uses the ConfidentialClientApplication instance to request an access token"""
        self._set_up_app()
        result = self.app.acquire_token_for_client(self.scopes)
        self.access_token = result['access_token']

    def save_oauth_token(self):
        """Writes the OAuth token to a file"""
        with open(self.token_path, 'w') as f:
            f.write(self.access_token)




















        # result = None  # It is just an initial value. Please follow instructions below.
        #
        # # We now check the cache to see
        # # whether we already have some accounts that the end user already used to sign in before.
        # self.accounts = self.app.get_accounts()
        # if self.accounts:
        #     # If so, you could then somehow display these accounts and let end user choose
        #     print("Pick the account you want to use to proceed:")
        #     for a in self.accounts:
        #         print(a["username"])
        #     # Assuming the end user chose this one
        #     chosen = self.accounts[0]
        #     # Now let's try to find a token in cache for this account
        #     # result = self.app.acquire_token_silent(["your_scope"], account=chosen)
        #     result = self.app.acquire_token_silent([self.scope], account=chosen)
        #
        #
        # if not result:
        #     # So no suitable token exists in cache. Let's get a new one from AAD.
        #     result = self.app.acquire_token_by_one_of_the_actual_method(..., scopes=["User.Read"])
        # if "access_token" in result:
        #     self.access_token = result["access_token"]
        #     print(result["access_token"])  # Yay!
        # else:
        #     print(result.get("error"))
        #     print(result.get("error_description"))
        #     print(result.get("error_description"))  # You may need this when reporting a bug
        #
        #     raise OauthError(**result)
        #     # raise OauthError(result.get("error"), result.get("error_description"), result.get("error_description"))
