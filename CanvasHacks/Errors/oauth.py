

class OauthError(Exception):
    """
    Error thrown when there is trouble with oauth2 credentials
    """
    def __init__( self, error, error_description=None, correlation_id=None):
        self.correlation_id = correlation_id
        self.error_description = error_description
        self.error = error

class ExpiredTokenError(Exception):
    """Thrown when the access token has expired"""

    def __init__(self, error=None, error_description=None):
        self.error_description = error_description
        self.error = error