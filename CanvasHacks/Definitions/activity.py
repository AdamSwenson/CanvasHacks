"""
Created by adam on 3/16/20
"""
__author__ = 'adam'

from CanvasHacks import environment as env
from CanvasHacks.Definitions.base import DiscussionType
from CanvasHacks.Files.FileTools import read_text_block
from CanvasHacks.Models.model import Model
from CanvasHacks.TimeTools import utc_string_to_local_dt, check_is_date

if __name__ == '__main__':
    pass


class Activity( Model ):
    """A wrapper around the canvas provided properties for a quiz which adds
     properties and methods specific to the peer review assignments

    NOT SPECIFIC TO ANY GIVEN STUDENT
    """

    @classmethod
    def is_activity_type( cls, assignment_name ):
        """Given the name of an activity, determines
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
        return isinstance( self, DiscussionType )

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

    @property
    def string_lock_date( self ):
        """Returns a human readable date for the last chance to turn in with
        the format yyyy-mm-dd
        """
        if self.due_at is None: return ''
        t = utc_string_to_local_dt( self.lock_at )
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