"""
Errors and special cases that arise when trying to pair up
 students for peer review.
Created by adam on 1/23/20
"""
__author__ = 'adam'

if __name__ == '__main__':
    pass

class AllAssigned(Exception):
    """Raised when every student who has submitted new has
    previously been assigned a partner. This could arise
    if they resubmitted the assignment after the deadline and
    were thus treated as new
    """
    def __init__(self, submitters):
        self.submitters = submitters

class AlreadyAssigned( Exception ):
    """Raised when the student whose work is being considered for assignment
    has already had someone else assigned to grade it
    """
    pass


class SubmissionIncomplete( Exception ):
    """Raised when the submission object being considered for
    review assignent has not yet been completed"""
    pass


class NoAvailablePartner( Exception ):
    """Raised when only 1 new person has submitted and thus
    there is no one to review them"""
    def __init__(self, submitters):
        self.submitters = submitters

class NoReviewPairingsLoaded(Exception):
    pass

