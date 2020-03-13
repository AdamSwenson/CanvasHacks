"""
Created by adam on 2/24/20
"""
__author__ = 'adam'

if __name__ == '__main__':
    pass

class NoNewSubmissions(Exception):
    """Raised when there is, ahem, nothing new
    in the data which has been retrieved
    """
    pass

class NoStudentWorkDataLoaded(Exception):
    """Raised to indicate that ALL attempts to acquire data
    have failed and no more will be attempted"""
    pass

class NoWorkDownloaded(Exception):
    """
    Raised to indicate that the download attempts have failed
    so a handler can determine the next steps
    """
    def __init__(self):
        self.message = "Could not download data."


class NoWorkFromFile(Exception):
    """
    Raised to indicate that the download attempts have failed
    so a handler can determine the next steps
    """
    def __init__(self):
        self.message = "Could not load data from file."
