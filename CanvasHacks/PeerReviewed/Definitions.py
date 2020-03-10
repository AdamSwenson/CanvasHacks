"""
Objects which define the parameters/ values for the entire unit

Created by adam on 12/24/19
"""
from CanvasHacks.FileTools import read_text_block
from CanvasHacks.GradingTools.nonempty import CreditForNonEmpty
from CanvasHacks.GradingTools.penalities import HalfLate, NoLatePenalty

__author__ = 'adam'

import re

import canvasapi
import pandas as pd
from CanvasHacks import environment as env
from CanvasHacks.Models.QuizModels import StoredDataFileMixin, QuizDataMixin
from CanvasHacks.Models.model import Model
from CanvasHacks.TimeTools import utc_string_to_local_dt, check_is_date

if __name__ == '__main__':
    pass


class SkaaReviewGroup:
    """Activities which are part of a skaa"""
    pass


class DiscussionGroup:
    """Activities which are part of a discussion-review sequence"""
    pass


class Activity( Model ):
    """A wrapper around the canvas provided properties for a quiz which adds
     properties and methods specific to the peer review assignments

    NOT SPECIFIC TO ANY GIVEN STUDENT
    """

    @classmethod
    def is_activity_type( cls, assignment_name ):
        """Given the name of an unit, determines
        whether it is an instance of this unit type"""
        return cls.regex.search( assignment_name.strip().lower() )

    def __init__( self, **kwargs ):
        # when the activity_inviting_to_complete is due
        # ": "2013-01-23T23:59:00-07:00"
        self.due_at = None
        # Set this date if want to give half credit for
        # assignments turned in after this.
        # Normally won't be used, unless manually set
        self.quarter_credit_deadline = None
        # when to lock the activity_inviting_to_complete
        self.lock_at = None
        # // when to unlock the activity_inviting_to_complete
        self.unlock_at = None
        self.points_possible = None
        self._unit_number = None
        self._description_text = ''

        self.creation_dict = { }
        """A dictionary of all the values needed to
        create one of these activities on canvas"""

        super().__init__( **kwargs )

    @property
    def is_quiz_type( self ):
        """Returns whether this is the sort of unit
        that uses a quiz report or not
        """
        try:
            return self.quiz_id > 0
        except AttributeError:
            return False

    @property
    def is_discussion_type( self ):
        """Returns whether this is a discussion.
        Mainly used to simplify decisions elsewhere
        so that we don't have to check for discussion
        type """
        return isinstance( self, DiscussionForum )

    @property
    def last_half_credit_date( self ):
        """If a quarter credit deadline has been set
        this will return that value, otherwise it will just
        use the lock date"""
        if self.quarter_credit_deadline is not None:
            return self.quarter_credit_deadline
        return self.lock_at

    @property
    def make_title( self ):
        # if self.unit_number:
        return "Unit {} {}".format( self.unit_number, self.title_base )

    @property
    def assignable_points( self ):
        """How many points are assigned by the reviewer"""
        return self.max_points - self.completion_points

    @property
    def string_due_date( self ):
        """Returns a human readable date for the due date with
        the format yyyy-mm-dd
        """
        if self.due_at is None: return ''
        t = utc_string_to_local_dt( self.due_at )
        return t.date().isoformat()

    @staticmethod
    def _check_date( date ):
        """Checks that a value is a pd.Timestamp
        if not, it tries to make it into one"""
        return check_is_date( date )

    @property
    def unit_number( self ):
        try:
            # preference if has been set internally
            return self._unit_number
        except AttributeError:
            return env.CONFIG.unit.unit_number

    @unit_number.setter
    def unit_number( self, unit_number ):
        self._unit_number = unit_number

    @property
    def description( self ):
        try:
            if len( self._description_text ) > 0:
                return self._description_text
            fname = "{}/assignment-templates/{}".format( env.DATA_FOLDER, self.instructions_filename )
            self._description_text = read_text_block( fname )
            return self._description_text

        except (AttributeError, FileNotFoundError) as e:
            print( 'no file for activity', e )
            # In case there is no file for the activity
            return ""

    @description.setter
    def description( self, text ):
        self._description_text = text

    # def creation_dict( self ):
    #     """A dictionary of all the values needed to
    #     create one of these activities on canvas"""
    #     exclude = ['title_base', 'instructions_filename']

    # @property
    # def dates_dict( self ):
    #     return {'assign' self.make_title


class TopicalAssignment( Activity, QuizDataMixin, StoredDataFileMixin ):
    title_base = 'Topical assignment'
    instructions_filename = 'topical-assignment-instructions.txt'
    creation_type = 'quiz'

    regex = re.compile( r"\btopical assignment\b" )

    def __init__( self, **kwargs ):
        super().__init__( **kwargs )
        self.grace_period = pd.Timedelta( '2 days' )

        # The object which will be used to penalize late assignments
        self.penalizer = HalfLate( self.due_at, self.grace_period )

        # The object which will be used to assign the score
        self.grade_method = CreditForNonEmpty(min_words=2, count_stopwords=True)



class InitialWork( SkaaReviewGroup, Activity, QuizDataMixin, StoredDataFileMixin ):
    title_base = "Content assignment"
    instructions_filename = 'content-assignment-instructions.txt'
    creation_type = 'assignment'

    regex = re.compile( r"\bcontent assignment\b" )

    def __init__( self, **kwargs ):
        self.question_columns = [ ]
        super().__init__( **kwargs )

        # Code for accessing the subsequent unit
        self.access_code_for_next_on = Review
        self.access_code_for_next = None

        # Tools which handle the grade
        self.grace_period = pd.Timedelta( '2 days' )

        # The object which will be used to penalize late assignments
        self.penalizer = HalfLate( self.due_at, self.grace_period )

        # The object which will be used to assign the score
        self.grade_method = CreditForNonEmpty(min_words=2, count_stopwords=True)


class Review( SkaaReviewGroup, Activity, QuizDataMixin, StoredDataFileMixin ):
    """Representation of the peer review component of the
     unit """
    title_base = "Peer review"
    instructions_filename = 'peer-review-instructions.txt'
    creation_type = 'survey'

    regex = re.compile( r"\breview\b" )

    def __init__( self, **kwargs ):
        # Code used to open the review unit
        self.access_code = None

        # todo access_code_for_next_on probably not needed; created without looking at what already have
        self.access_code_for_next_on = MetaReview
        self.access_code_for_next = None

        # Link to the activity_inviting_to_complete on canvas so students can click
        # directly to it
        self.activity_link = None

        # The object which will be used to penalize late assignments
        self.penalizer = NoLatePenalty(  )

        # The object which will be used to assign the score
        # NB, min_words is 1 for now so as to not create problems with multiple-choice answers
        # This could be fixed in CAN-57
        self.grade_method = CreditForNonEmpty(min_words=1, count_stopwords=True)

        super().__init__( **kwargs )
        self.email_intro = "Here is another student's unit for you to review:"

    @property
    def email_subject( self ):
        """Since unit number will be set after initialization
        we need to do this as a property"""
        return "Unit {} peer-review of content unit".format( self.unit_number )


class MetaReview( SkaaReviewGroup, Activity, QuizDataMixin, StoredDataFileMixin ):
    """Representation of the peer review of
    another student's submission"""
    title_base = "Metareview"
    instructions_filename = 'metareview-instructions.txt'
    access_code_for_next_on = None
    creation_type = 'survey'

    regex = re.compile( r"\bmetareview\b" )

    def __init__( self, **kwargs ):
        super().__init__( **kwargs )

        self.email_intro = "Here is the feedback on your assignment:"

        # The object which will be used to penalize late assignments
        self.penalizer = NoLatePenalty(  )

        # The object which will be used to assign the score
        # NB, min_words is 1 for now so as to not create problems with multiple-choice answers
        # This could be fixed in CAN-57
        self.grade_method = CreditForNonEmpty(min_words=1, count_stopwords=True)


    @property
    def email_subject( self ):
        """Since unit number will be set after initialization
        we need to do this as a property"""
        return "Unit {} metareview of peer-review".format( self.unit_number )


class DiscussionForum(DiscussionGroup, Activity ):
    """Representation of the main discussion forum"""
    title_base = "Main discussion"
    instructions_filename = 'discussion-forum-instructions.txt'
    regex = re.compile( r"\bforum\b" )
    creation_type = 'discussion'

    def __init__( self, **kwargs ):
        super().__init__( **kwargs )

        # The object which will be used to penalize late assignments
        self.penalizer = NoLatePenalty(  )

        # The object which will be used to assign the score
        self.grade_method = CreditForNonEmpty(min_words=2, count_stopwords=True)

    def create_on_canvas( self, course ):
        course.create_quiz()

    @property
    def topic_id( self ):
        try:
            return self.discussion_topic[ 'id' ]
        except KeyError:
            print( "No topic id set on discussion " )


class DiscussionReview(DiscussionGroup, Activity, QuizDataMixin, StoredDataFileMixin ):
    """Representation of the peer review of the main discussion forum"""
    title_base = "Discussion review"
    instructions_filename = 'discussion-review-instructions.txt'
    regex = re.compile( r"\bdiscussion review\b" )
    creation_type = 'survey'

    def __init__( self, **kwargs ):
        super().__init__( **kwargs )
        self.email_intro = "Here are the discussion forum posts from another student for you to review:"

        # The object which will be used to penalize late assignments
        self.penalizer = NoLatePenalty(  )

        # The object which will be used to assign the score
        # NB, min_words is 1 for now so as to not create problems with multiple-choice answers
        # This could be fixed in CAN-57
        self.grade_method = CreditForNonEmpty(min_words=1, count_stopwords=True)

    @property
    def email_subject( self ):
        """Since unit number will be set after initialization
        we need to do this as a property"""
        return "Unit {} peer-review of discussion forum posts".format( self.unit_number )


class UnitEndSurvey( Activity ):
    """Representation of the survey at the end of each unit"""
    title_base = "Unit-end survey"
    instructions_filename = 'unit-end-survey-instructions.txt'
    regex = re.compile( r"\bunit-end survey\b" )
    creation_type = 'survey'

    def __init__( self, **kwargs ):
        super().__init__( **kwargs )

        # The object which will be used to penalize late assignments
        self.penalizer = NoLatePenalty(  )

        # The object which will be used to assign the score
        # NB, min_words is 1 for now so as to not create problems with multiple-choice answers
        # This could be fixed in CAN-57
        self.grade_method = CreditForNonEmpty(min_words=1, count_stopwords=True)


class Journal( Activity ):
    """Representation of a journal unit.
    Not related to assignments within a Unit
    """
    title_base = "Journal"

    regex = re.compile( r"\bjournal\b" )
    creation_type = 'assignment'

    def __init__( self, **kwargs ):
        self.grace_period = pd.Timedelta( '2 days' )
        super().__init__( **kwargs )

        # The object which will be used to penalize late assignments
        self.penalizer = HalfLate( self.due_at, self.grace_period )

        # The object which will be used to assign the score
        self.grade_method = CreditForNonEmpty(min_words=2, count_stopwords=True)


class Unit:
    """The main SKAA. This holds the definitions of all the consituent parts"""
    __name__ = 'Unit'

    def __init__( self, course, unit_number ):
        self.component_types = [ TopicalAssignment,
                                 InitialWork,
                                 Review,
                                 MetaReview,
                                 DiscussionForum,
                                 DiscussionReview,
                                 UnitEndSurvey
                                 ]
        self.components = [ ]

        self.course = course
        self.unit_number = unit_number
        if isinstance( course, canvasapi.course.Course ):
            # This check is here so can run tests without
            # needing a dummy Course object
            self._initialize()

    # def __repr__(self):
    #     """This way can still use unit in format statements """
    #     return self.unit_number

    def _initialize( self ):
        # Get all assignments for the course
        assignments = [ a for a in self.course.get_assignments() ]
        print( "{} assignments in course".format( len( assignments ) ) )
        # Parse out the assignments which have the unit number in their names
        unit_assignments = self.find_for_unit( self.unit_number, assignments )
        print( "{} assignments found for unit # {}".format( len( unit_assignments ), self.unit_number ) )
        self.find_components( unit_assignments )
        for c in self.components:
            # todo access_code_for_next_on probably not needed; created without looking at what already have
            self._set_access_code_for_next( c )
            # Set the unit number for the assignment
            setattr( c, 'unit_number', self.unit_number )

    def find_components( self, unit_assignments ):
        # Parse components of unit
        for t in self.component_types:
            for a in unit_assignments:
                if t.is_activity_type( a.name ):
                    o = t( **a.attributes )
                    o.access_code = self._set_access_code( o )
                    self.components.append( o )

    def find_for_unit( self, unit_number, assignments ):
        """Given a list of unit names finds the one's
        relevant to this unit
        """
        rx = re.compile( r"\bunit {}\b".format( unit_number ) )
        try:
            return [ a for a in assignments if rx.search( a.name.strip().lower() ) ]
        except AttributeError:
            # Things like discussion forums have a title, not a name
            return [ a for a in assignments if rx.search( a.title.strip().lower() ) ]

    def _set_access_code_for_next( self, obj ):
        """Sets the access code students will need for the subsequent
        unit on the present unit as access_code_for_next.
        NB, this must be run after all the unit.components have been
        discovered and had their access codes set
        """
        # todo access_code_for_next_on probably not needed; created without looking at what already have

        try:
            if obj.access_code_for_next_on is not None:
                next_assign = self.get_by_class( obj.access_code_for_next_on )
                obj.access_code_for_next = next_assign.access_code
        except AttributeError:
            print( "No access code for subsequent unit set for {}".format( obj.name ) )

    def _set_access_code( self, obj ):
        """Some things will have an access code stored
        on them. Others have no access code. Some have
        the access code stored elsewhere.
        This sorts that out and sets the access code if possible.
        NB, this sets the code for the present unit, not the unit
        we will be notifying about
        """
        try:
            # first we try to set from self
            return obj.access_code
        except AttributeError:
            # check to see if we ahve a quiz id
            try:
                return self.course.get_quiz( obj.quiz_id ).access_code
            except AttributeError:
                print( "No access code for {}".format( obj.name ) )
                return None

    def get_by_class( self, component_class ):
        """
        Returns the unit component given an unistantiated
        class definition object
        :param component_class:
        :return:
        """
        for c in self.components:
            if isinstance( c, component_class ):
                return c

    @property
    def topical_assignment( self ):
        for c in self.components:
            if isinstance( c, TopicalAssignment ):
                return c

    @property
    def initial_work( self ):
        for c in self.components:
            if isinstance( c, InitialWork ):
                return c

    @property
    def metareview( self ):
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

    @property
    def unit_end_survey( self ):
        for c in self.components:
            if isinstance( c, UnitEndSurvey ):
                return c

# class Assignment( StoreMixin ):
#     """Defines all constant values for the unit"""
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
