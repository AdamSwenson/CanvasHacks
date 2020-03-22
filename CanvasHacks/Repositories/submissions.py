"""
Created by adam on 1/18/20
"""
import canvasapi
import pandas as pd

import CanvasHacks.environment as env
from CanvasHacks.Api.DownloadProcessingTools import extract_body
from CanvasHacks.Repositories.interfaces import ISubmissionRepo

__author__ = 'adam'

from CanvasHacks.Repositories.mixins import ObjectHandlerMixin

class CannotDetermineState(Exception):
    """Raised when can't tell the submission status of a record"""
    pass

class SubmissionRepository( ISubmissionRepo, ObjectHandlerMixin ):
    """Downloads and stores canvasapi.Submission objects
    NB, for many operations on quiz assignments, will need
    to use QuizSubmission objects. That's not this repo
    """

    def __init__( self, assignment: canvasapi.assignment.Assignment ):
        """

        :param assignment: Canvas api unit object for use in downloading
        """
        self.assignment = assignment
        self.download()

    def has_completed( self, student ):
        """
        Determines whether the student has submitted the assignment
        :param student:
        :return: Boolean
        """
        student_id = self._handle_id(student)
        rec = self.get_by_student_id(student_id)
        # state = self.frame.loc['student_id', student_id].workflow_state

        if rec.workflow_state == 'submitted':
            return True

        if rec.workflow_state == 'unsubmitted':
            return False

        raise CannotDetermineState

    def download( self ):
        """Downloads and stores submission objects as a list in self.data"""
        self.data = [ s for s in self.assignment.get_submissions() ]
        for d in self.data:
            d.body = extract_body( d )
        print( "Downloaded {} submissions for unit id {}".format( len( self.data ), self.assignment.id ) )

    @property
    def ungraded_submissions( self ):
        return [ s for s in self.data if s.workflow_state != 'graded' ]

    @property
    def frame( self ):
        """Returns the submissions as a dataframe"""
        s = [ ]
        for r in self.data:
            # Iterating through list of canvasapi.Submission objects
            s.append( { 'course_id': int( r.course_id ),
                        'quiz_id': int( r.assignment_id ),
                        'activity_id': int( r.assignment_id ),
                        'student_id': int( r.user_id ),
                        'user_id': int( r.user_id ),
                        'submission_id': int( r.id ),
                        'attempt': r.attempt,
                        'grade': r.grade,
                        'score': r.score,
                        'workflow_state': r.workflow_state,
                        'late': r.late
                        } )
            # s.append( { 'course_id': int( self.unit.course_id ),
            #             'quiz_id': int( self.unit.id ),
            #             'student_id': int( r[ 'user_id' ] ),
            #             'submission_id': int( r[ 'id' ] ),
            #             'attempt': int( r[ 'attempt' ] )
            #             } )
        return pd.DataFrame( s )

    def get_by_id( self, submission_id: int ):
        """Returns submission object with the id"""
        for s in self.data:
            if s.id == submission_id:
                return s

    def get_by_student_id( self, student_id ):  # , attempt=None ):
        for s in self.data:
            if s.id == student_id:
                # if attempt is None:
                #     return s
                # elif s.attempt == attempt:
                return s


class AssignmentSubmissionRepository( SubmissionRepository ):
    body_column_name = 'body'

    def __init__( self, assignment: canvasapi.assignment.Assignment ):
        """

        :param assignment: Canvas api unit object for use in downloading
        """
        self.assignment = assignment
        self.download()
        self._remove_ignored_users()

    def _remove_ignored_users( self, users=None ):
        """
        Removes all records from data, for each in a list of
        users, either given as a param, or the excluded_users
        list stored on env.CONFIG
        :param users:
        :return:
        """
        users = users if users is not None else env.CONFIG.excluded_users
        prelen = len( self.data )

        # Remove them
        self.data = [ s for s in self.data if s.user_id not in users ]

        removed = prelen - len( self.data )
        if removed > 0:
            print( "Removed {} records belonging to users in the excluded list".format( removed ))

    @property
    def frame( self ):
        """Returns the submissions as a dataframe"""
        s = [ ]
        for r in self.data:
            # Iterating through list of canvasapi.Submission objects
            s.append( { 'course_id': int( r.course_id ),
                        'activity_id': int( r.assignment_id ),
                        'student_id': int( r.user_id ),
                        'user_id': int( r.user_id ),
                        'submission_id': int( r.id ),
                        'attempt': r.attempt,
                        'grade': r.grade,
                        'score': r.score,
                        'workflow_state': r.workflow_state,
                        'late': r.late,
                        self.body_column_name: r.body
                        } )

        return pd.DataFrame( s )


class QuizSubmissionRepository( ISubmissionRepo ):

    def __init__( self, quiz: canvasapi.quiz.Quiz ):
        """
        Should get quiz object with something like
            quiz = environment.CONFIG.course.get_quiz(activity_inviting_to_complete.quiz_id)
        :param quiz: Canvas api unit object for use in downloading
        """
        self.quiz = quiz
        self.download()

    def download( self ):
        """Downloads and stores submission objects as a list in self.data"""
        self.data = [ s for s in self.quiz.get_submissions() ]
        print( "Downloaded {} submissions for quiz id {}".format( len( self.data ), self.quiz.id ) )

    @property
    def frame( self ):
        """Returns the submissions as a dataframe"""
        s = [ ]
        for r in self.data:
            # Iterating through list of canvasapi.Submission objects
            s.append( { 'course_id': int( r.course_id ),
                        'quiz_id': int( r.quiz_id ),
                        'student_id': int( r.user_id ),
                        'user_id': int( r.user_id ),
                        'submission_id': int( r.submission_id ),
                        'attempt': r.attempt,
                        'score': r.score,
                        'workflow_state': r.workflow_state,
                        } )
        return pd.DataFrame( s )

    def get_by_student_id( self, student_id, attempt=None ):
        return [ d for d in self.data if d.user_id == student_id and d.attempt == attempt ][ 0 ]


if __name__ == '__main__':
    pass
