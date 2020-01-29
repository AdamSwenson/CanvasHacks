"""
Objects which define the parameters/ values for the entire assignment

Created by adam on 12/24/19
"""
import pandas as pd

__author__ = 'adam'
import canvasapi

if __name__ == '__main__':
    pass
import re

from CanvasHacks.Models.model import Model


class Activity( Model ):
    """A wrapper around the canvas provided properties for a quiz which adds
     properties and methods specific to the peer review assignments

    NOT SPECIFIC TO ANY GIVEN STUDENT
    """

    @classmethod
    def is_activity_type( cls, assignment_name ):
        """Given the name of an assignment, determines
        whether it is an instance of this assignment type"""
        return cls.regex.search( assignment_name.strip().lower(), re.IGNORECASE )

    def __init__( self, **kwargs ):
        # when the activity is due
        # ": "2013-01-23T23:59:00-07:00"
        self.due_at = None
        # when to lock the activity
        self.lock_at = None
        # // when to unlock the activity
        self.unlock_at = None
        self.points_possible = None
        self.unit_number = None

        super().__init__( **kwargs )

    @property
    def make_title( self ):
        # if self.unit_number:
        return "Unit {} {}".format(self.unit_number, self.title_base)

    @property
    def assignable_points( self ):
        """How many points are assigned by the reviewer"""
        return self.max_points - self.completion_points

    @staticmethod
    def _check_date( date ):
        """Checks that a value is a pd.Timestamp
        if not, it tries to make it into one"""
        return date if isinstance( date, pd.Timestamp ) else pd.to_datetime( date )

    # @property
    # def dates_dict( self ):
    #     return {'assign' self.make_title

class TopicalAssignment( Activity ):
    title_base = 'Topical assignment'

    regex = re.compile( r"\btopical assignment\b" )

    def __init__( self, **kwargs ):
        super().__init__( **kwargs )


class InitialWork( Activity ):
    title_base = "Content assignment"

    regex = re.compile( r"\bcontent assignment\b" )

    def __init__( self, **kwargs ):
        self.question_columns = [ ]
        super().__init__( **kwargs )


class Review( Activity ):
    """Representation of the peer review component of the
     assignment """
    title_base = "Peer review"
    regex = re.compile( r"\breview\b" )

    def __init__( self, **kwargs ):
        # Code used to open the review assignment
        self.access_code = None

        # Link to the activity on canvas so students can click
        # directly to it
        self.activity_link = None

        super().__init__( **kwargs )


class MetaReview( Activity ):
    """The review review"""
    """Representation of the peer review of 
    another student's submission"""
    title_base = "Metareview"

    regex = re.compile( r"\bmetareview\b" )

    def __init__( self, **kwargs ):
        super().__init__( **kwargs )


class DiscussionForum( Activity ):
    """Representation of the main discussion forum"""
    title_base = "Main discussion"

    regex = re.compile( r"\bforum\b" )

    def __init__( self, **kwargs ):
        super().__init__( **kwargs )


class DiscussionReview( Activity ):
    """Representation of the peer review of the main discussion forum"""
    title_base = "Discussion review"

    regex = re.compile( r"\bdiscussion review\b" )

    def __init__( self, **kwargs ):
        super().__init__( **kwargs )


class Unit:
    """The main SKAA. This holds the definitions of all the consituent parts"""
    __name__ = 'Unit'

    def __init__( self, course, unit_number ):
        self.component_types = [TopicalAssignment,
                                InitialWork,
                                Review,
                                MetaReview,
                                DiscussionForum,
                                DiscussionReview
                                ]
        self.components = [ ]

        self.course = course
        self.unit_number = unit_number
        if isinstance( course, canvasapi.course.Course ):
            # This check is here so can run tests without
            # needing a dummy Course object
            self._initialize()

    def _initialize( self ):
        # Get all assignments for the course
        assignments = [ a for a in self.course.get_assignments() ]
        print( "{} assignments in course".format( len( assignments ) ) )
        # Parse out the assignments which have the unit number in their names
        unit_assignments = self.find_for_unit( self.unit_number, assignments )
        print( "{} assignments found for unit # {}".format( len( unit_assignments ), self.unit_number ) )
        self.find_components( unit_assignments )

    def find_components( self, unit_assignments ):
        # Parse components of unit
        for t in self.component_types:
            for a in unit_assignments:
                if t.is_activity_type( a.name ):
                    self.components.append( t( **a.attributes ) )

    def find_for_unit( self, unit_number, assignments ):
        """Given a list of assignment names finds the one's
        relevant to this unit
        """
        rx = re.compile( r"\bunit {}\b".format( unit_number ) )
        return [ a for a in assignments if rx.search( a.name.strip().lower() ) ]

    @property
    def initial_work( self ):
        for c in self.components:
            if isinstance( c, InitialWork ):
                return c

    @property
    def meta_review( self ):
        for c in self.components:
            if isinstance( c, MetaReview ):
                return c

    @property
    def review( self ):
        for c in self.components:
            if isinstance( c, Review ):
                return c

    @property
    def discussion_forum( self ):
        for c in self.components:
            if isinstance( c, DiscussionForum ):
                return c

    @property
    def discussion_review( self ):
        for c in self.components:
            if isinstance( c, DiscussionReview ):
                return c

# class Assignment( StoreMixin ):
#     """Defines all constant values for the assignment"""
#
#     def __init__( self, initial_work: InitialWork, review: Review, meta_review: MetaReview, **kwargs ):
#         """
#         :param initial_work:
#         :param review:
#         :param meta_review:
#         """
#         self.initial_work = initial_work
#         self.meta_review = meta_review
#         self.review = review
#
#         self.handle_kwargs( kwargs )