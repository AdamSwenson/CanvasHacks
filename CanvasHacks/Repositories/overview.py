"""
Repositories which give an overiew of statuses etc
Created by adam on 3/14/20
"""
__author__ = 'adam'

from CanvasHacks import environment
from CanvasHacks.DAOs.mixins import DaoMixin
from CanvasHacks.Definitions.skaa import InitialWork,\
    MetaReview, Review
from CanvasHacks.Definitions.discussion import DiscussionForum, DiscussionReview
from CanvasHacks.Definitions.groups import SkaaReviewGroup, DiscussionGroup
from CanvasHacks.Repositories.reviewer_associations import AssociationRepository
from CanvasHacks.Repositories.status import FeedbackStatusRepository, InvitationStatusRepository
from CanvasHacks.Repositories.students import StudentRepository

if __name__ == '__main__':
    pass
import pandas as pd


class SkaaOverviewRepository( DaoMixin ):
    """
    Holds consolidated information about statuses etc for
    Skaa assignments

    Other classes like dashboard.skaaDashboard are in
    charge of displaying the information
    """

    def __init__( self, unit=None ):
        self.unit = unit
        self.studentRepo = StudentRepository( environment.CONFIG.course )
        self.studentRepo.download()

        if unit is not None:
            # Load and display counts
            self.load( unit )

    def _initialize( self, unit ):
        self.data = [ ]

        self.unit = unit
        # The activity whose id is used to store review pairings for the whole SKAA
        self.activity_for_review_pairings = self.unit.initial_work

        self.components = [ c for c in self.unit.components if isinstance( c, SkaaReviewGroup ) ]


        self._initialize_db()

        self.assignRepo = AssociationRepository( self.dao, self.activity_for_review_pairings )

    def load( self, unit ):
        """
        Main called method which initializes and loads data
        Often will have to be called later than initialization
        so that we can have the object existing and then specify
        which unit to load.

        :param unit:
        :return:
        """
        self._initialize( unit )

        for sid, obj in self.studentRepo.data.items():
            d = {
                'student': obj.name,
                'canvas_id': sid,
                'csun_id': obj.sis_user_id
            }
            for c in self.components:
                if len( self.assignRepo.get_associations() ) > 0:
                    try:
                        # get the record where the student is the reviwer
                        a = self.assignRepo.get_by_reviewer( sid )
                        # get the name of the student being assessed
                        d[ 'reviewing' ] = self.studentRepo.get_student_name( a.assessee_id )
                        d[ 'reviewing_id' ] = a.assessee_id
                        # get the record where the student is the author
                        b = self.assignRepo.get_by_author( sid )
                        # get the name
                        d[ 'reviewed_by' ] = self.studentRepo.get_student_name( b.assessor_id )
                        d[ 'reviewed_by_id' ] = b.assessor_id
                    except AttributeError:
                        pass

                self.add_invites( d, c, sid )

                self.add_reviews( d, c, sid )

            self.data.append( d )

        self.data = pd.DataFrame( self.data )

    def add_invites( self, data_dict, component, student_id ):
        invite_fields = { Review: 'invited_to_review', MetaReview: 'invited_to_metareview',
                          DiscussionReview: 'invited_to_discussion_review' }

        invite_fieldname = invite_fields.get( type( component ) )

        if invite_fieldname is not None:
            inv = InvitationStatusRepository( self.dao, component )
            data_dict[ invite_fieldname ] = pd.to_datetime( inv.received_at( student_id ) )

    def add_reviews( self, data_dict, component, student_id ):
        # Note: can't do in similar way to invitations since invited to metareview and received ca feedback
        # use different activities. The invitation is for the upcoming one which provides feedback

        # on the previous one
        # set to none so won't overwrite on next time through
        fb_fieldname = None

        if isinstance( component, InitialWork ):
            # we can't use the review object because feedback on the review
            # comes from the metareview
            fb_fieldname = 'received_feedback_on_essay'

        if isinstance( component, Review ):
            fb_fieldname = 'received_feedback_on_review'

        if isinstance( component, DiscussionForum ):
            fb_fieldname = 'received_discussion_feedback'

        if fb_fieldname is not None:
            fr = FeedbackStatusRepository( self.dao, component )
            data_dict[ fb_fieldname ] = pd.to_datetime( fr.received_at( student_id ) )

    @property
    def essay( self ):
        """
        Return students who have done initial work and been assigned a reviewer

        :return: DataFrame
        """
        return self.data[ ~self.data.reviewing.isnull() ]

    @property
    def no_essay( self ):
        """
        Students who have not submitted the initial work
        :return: DataFrame
        """
        return self.data[ self.data.reviewing.isnull() ]

    @property
    def reviewed( self ):
        """
        Returns the subset of students who have turned in the initial work
        whose reviewer has turned in the review

        :return: DataFrame
        """
        # Students whose reviewer has and has not turned in review
        return self.essay[ ~self.essay.received_feedback_on_essay.isnull() ]

    @property
    def non_reviewed( self ):
        """
        Returns the subset of students who have turned in the initial work
        whose reviewer has NOT turned in the review

        :return: DataFrame
        """
        return self.essay[ self.essay.received_feedback_on_essay.isnull() ]\
            # .drop( [ 'reviewing' ], axis=1 )

    @property
    def metareviewed( self ):
        """
        Returns the subset of students who have turned in the initial work
        whose author has turned in the metareview

        :return: DataFrame
        """
        return self.essay[ ~self.essay.received_feedback_on_review.isnull() ]

    @property
    def non_metareviewed( self ):
        """
        Returns the subset of students who have turned in the initial work
        whose author has turned in the metareview

        :return: DataFrame
        """
        return self.essay[ self.essay.received_feedback_on_review.isnull() ]


class DiscussionOverviewRepository( DaoMixin ):
    """
    Holds information about the discussion and discussion
    review for a unit

    Other classes like dashboard.discussionDashboard are in
    charge of displaying the information
    """

    def __init__( self, unit=None ):
        """
        Initializes and loads all data or
        waits to have load called

        :return:
        """
        self.unit = unit
        self.studentRepo = StudentRepository( environment.CONFIG.course )
        self.studentRepo.download()

        if unit is not None:
            # Load and display counts
            self.load( unit )

    def _initialize( self, unit ):
        self.data = [ ]
        self.unit = unit

        # The activity whose id is used to store review pairings for the whole SKAA
        self.activity_for_review_pairings = self.unit.discussion_review
        self.components = [ c for c in self.unit.components if isinstance( c, DiscussionGroup ) ]
        self.studentRepo = StudentRepository( environment.CONFIG.course )
        self.studentRepo.download()
        self._initialize_db()
        self.assignRepo = AssociationRepository( self.dao, self.activity_for_review_pairings )

    def load( self, unit ):

        self._initialize( unit )

        for sid, obj in self.studentRepo.data.items():
            d = {
                'student': obj.name,
                'canvas_id': sid,
                'csun_id': obj.sis_user_id
            }
            for c in self.components:
                if len( self.assignRepo.get_associations() ) > 0:
                    try:
                        # get the record where the student is the reviwer
                        a = self.assignRepo.get_by_reviewer( sid )
                        # get the name of the student being assessed
                        d[ 'reviewing' ] = self.studentRepo.get_student_name( a.assessee_id )
                        d[ 'reviewing_id' ] = a.assessee_id
                        # get the record where the student is the author
                        b = self.assignRepo.get_by_author( sid )
                        # get the name
                        d[ 'reviewed_by' ] = self.studentRepo.get_student_name( b.assessor_id )
                        d[ 'reviewed_by_id' ] = b.assessor_id
                    except AttributeError:
                        pass

                self.add_invites( d, c, sid )

                self.add_reviews( d, c, sid )

            self.data.append( d )

        self.data = pd.DataFrame( self.data )

    def add_invites( self, data_dict, component, student_id ):
        invite_fields = { DiscussionReview: 'invited_to_discussion_review' }

        invite_fieldname = invite_fields.get( type( component ) )

        if invite_fieldname is not None:
            inv = InvitationStatusRepository( self.dao, component )
            data_dict[ invite_fieldname ] = pd.to_datetime( inv.received_at( student_id ) )

    def add_reviews( self, data_dict, component, student_id ):
        # Note: can't do in similar way to invitations since invited to metareview and received ca feedback
        # use different activities. The invitation is for the upcoming one which provides feedback
        # on the previous one

        # set to none so won't overwrite on next time through
        fb_fieldname = None

        if isinstance( component, DiscussionForum ):
            fb_fieldname = 'received_discussion_feedback'

        if fb_fieldname is not None:
            fr = FeedbackStatusRepository( self.dao, component )
            data_dict[ fb_fieldname ] = pd.to_datetime( fr.received_at( student_id ) )

    @property
    def posters( self ):
        """
        Students who have posted and been assigned reviewers
        todo Consider whether should be using the assignment of reviewers or a status object
        :return: DataFrame
        """
        return self.data[ ~self.data.reviewing.isnull() ]

    @property
    def non_posters( self ):
        """
        Students who have not posted and thus not been assigned a reviewer
        :return: DataFrame
        """
        return self.data[ self.data.reviewing.isnull() ]

    @property
    def reviewed( self ):
        """
        Students whose reviewer has turned in the review
        :return: DataFrame
        """
        return self.posters[ ~self.posters.received_discussion_feedback.isnull() ]

    @property
    def non_reviewed( self ):
        """
        Students whose reviewer has NOT turned in the review
        :return: DataFrame
        """
        return self.posters[ self.posters.received_discussion_feedback.isnull() ]

    def add_invites( self, data_dict, component, student_id ):
        invite_fields = { DiscussionReview: 'invited_to_discussion_review' }

        invite_fieldname = invite_fields.get( type( component ) )

        if invite_fieldname is not None:
            inv = InvitationStatusRepository( self.dao, component )
            data_dict[ invite_fieldname ] = pd.to_datetime( inv.received_at( student_id ) )

    def add_reviews( self, data_dict, component, student_id ):
        # Note: can't do in similar way to invitations since invited to metareview and received ca feedback
        # use different activities. The invitation is for the upcoming one which provides feedback
        # on the previous one

        # set to none so won't overwrite on next time through
        fb_fieldname = None

        # todo this probably should be changed to discussion forum everywhere
        if isinstance( component, DiscussionReview ):
            fb_fieldname = 'received_discussion_feedback'

        if fb_fieldname is not None:
            fr = FeedbackStatusRepository( self.dao, component )
            data_dict[ fb_fieldname ] = pd.to_datetime( fr.received_at( student_id ) )


class NonSkaaAssignmentOverviewRepository:

    def __init__( self ):
        pass
