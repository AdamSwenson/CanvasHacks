"""Tools for authenticating for email via oauth2"""

from msal import PublicClientApplication

from CanvasHacks.Configuration import Configuration
from CanvasHacks.Errors.oauth import OauthError


# https://pypi.org/project/msal/


class OauthHandler(object):

    def __init__(self, configuration):
        self.result = None  # It is just an initial value. Please follow instructions below.
        self.authority = f"https://login.microsoftonline.com/{configuration.tenant_name}"
        self.client_id = configuration.oauth_client_id

        self.access_token = None


    def set_up_app(self):
        """
        Initializes the PublicClientApplication instance
        :return:
        """
        self.app = PublicClientApplication(
        self.client_id,
        authority=self.authority
        )

        result = None  # It is just an initial value. Please follow instructions below.

        # We now check the cache to see
        # whether we already have some accounts that the end user already used to sign in before.
        accounts = self.app.get_accounts()
        if accounts:
            # If so, you could then somehow display these accounts and let end user choose
            print("Pick the account you want to use to proceed:")
            for a in accounts:
                print(a["username"])
            # Assuming the end user chose this one
            chosen = accounts[0]
            # Now let's try to find a token in cache for this account
            result = self.app.acquire_token_silent(["your_scope"], account=chosen)


        if not result:
            # So no suitable token exists in cache. Let's get a new one from AAD.
            result = self.app.acquire_token_by_one_of_the_actual_method(..., scopes=["User.Read"])
        if "access_token" in result:
            self.access_token = result["access_token"]
            print(result["access_token"])  # Yay!
        else:
            print(result.get("error"))
            print(result.get("error_description"))
            print(result.get("error_description"))  # You may need this when reporting a bug

            raise OauthError(**result)
            # raise OauthError(result.get("error"), result.get("error_description"), result.get("error_description"))
