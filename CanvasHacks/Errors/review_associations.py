"""
Error related to the assignment of students to review other
students
Created by adam on 1/23/20
"""
__author__ = 'adam'

if __name__ == '__main__':
    pass


class AlreadyAssigned( Exception ):
    """Raised when the student whose work is being considered for assignment
    has already had someone else assigned to grade it
    """
    pass


class SubmissionIncomplete( Exception ):
    """Raised when the submission object being considered for
    review assignent has not yet been completed"""
    pass
