"""
Created by adam on 1/18/20
"""
import canvasapi

from CanvasHacks.Repositories.IRepositories import IRepo
from CanvasHacks.DownloadProcessingTools import extract_body
__author__ = 'adam'


class SubmissionRepository( IRepo ):

    def __init__( self, assignment: canvasapi.assignment.Assignment ):
        """

        :param assignment: Canvas api assignment object for use in downloading
        """
        self.assignment = assignment
        self.download()

    def download( self ):
        self.data = [ s for s in self.assignment.get_submissions()]
        for d in self.data:
            d.body = extract_body(d)
        print("Downloaded {} submissions for assignment id {}".format(len(self.data), self.assignment.id))


    def get_by_id( self, submission_id: int ):
        """Returns submission object with the id"""
        for s in self.data:
            if s.id == submission_id:
                return s

    def get_by_student_id( self, student_id):
        for s in self.data:
            if s.id == student_id:
                return s


if __name__ == '__main__':
    pass
