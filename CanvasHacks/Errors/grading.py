"""
Created by adam on 2/27/20
"""
__author__ = 'adam'

if __name__ == '__main__':
    pass


class NonStringInContentField(Exception):
    """Raised when something other than a string
    appears in a field that we are assessing
    """
    pass


class StudentUnableToComplete(Exception):
    """Raised when a student is unable to 
    complete the assignment. Usually because 
    the student they are assigned to review hasn't done their part
    """
    
    def __init__(self, blocked_student, blocking_student):
        self.blocked_student = blocked_student
        self.blocking_student = blocking_student