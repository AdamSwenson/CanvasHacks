

class OauthError(Exception):
    """
    Error thrown when there is trouble with oauth2 credentials
    """
    def __init__( self, error, error_description, correlation_id):
        self.correlation_id = correlation_id
        self.error_description = error_description
        self.error = error