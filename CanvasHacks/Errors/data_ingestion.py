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
    pass