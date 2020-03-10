"""
Created by adam on 2/18/20
"""
from CanvasHacks.Models.model import StoreMixin

__author__ = 'adam'


class IGrader(StoreMixin):
    """Parent which defines common methods for any
    class in charge of grading student work

    todo Calling classes should be keeping a record of details of how grade assigned
    """
    def __init__(self, **kwargs):
        self.graded = [ ]
        self.handle_kwargs(**kwargs)

    def grade( self ):
        """Carry out grading on internally stored data
        from the repos it holds"""
        raise NotImplementedError

    # def log( self ):
    #     """
    #     :return:
    #     """
    #     raise NotImplementedError

    @property
    def activity( self ):
        return self.work_repo.activity


if __name__ == '__main__':
    pass