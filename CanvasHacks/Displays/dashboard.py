"""
Created by adam on 3/13/20
"""
__author__ = 'adam'

from CanvasHacks.Repositories.overview import SkaaOverviewRepository

if __name__ == '__main__':
    pass

SKAA_ORDER = [ 'student', 'reviewing', 'reviewed_by', 'invited_to_review',
               'received_feedback_on_essay', 'invited_to_metareview',
               'received_feedback_on_review', 'canvas_id', 'csun_id', 'reviewing_id', 'reviewed_by_id' ]

DISCUSSION_ORDER = [ 'student', 'reviewing', 'reviewed_by', 'invited_to_discussion_review',
                     'received_discussion_feedback', 'canvas_id', 'csun_id', 'reviewing_id', 'reviewed_by_id' ]


class SkaaDashboard:
    """
    This is in charge of displaying information from the
    skaa overview repo
    """

    def __init__( self, overview_repo: SkaaOverviewRepository ):
        self.repo = overview_repo

    #
    # def load( self, unit ):
    #     """
    #     Initializes and loads all data.
    #
    #     :return:
    #     """
    #     # define here so will reset every load
    #     self.data = [ ]
    #
    #     self.unit = unit
    #     # The activity whose id is used to store review pairings for the whole SKAA
    #     self.activity_for_review_pairings = self.unit.initial_work
    #
    #     self.components = [ c for c in self.unit.components if isinstance( c, SkaaReviewGroup ) ]
    #
    #     self.studentRepo = StudentRepository( environment.CONFIG.course )
    #     self.studentRepo.download()
    #
    #     self._initialize_db()
    #
    #     self.assignRepo = AssociationRepository( self.dao, self.activity_for_review_pairings )
    #
    #     # Load and display counts
    #     self.get_data()
    #     self.print_counts()
    #
    # def get_data( self ):
    #     #     feedback_fields = {Review: 'received_ca_feedback', MetaReview: 'received_meta_feedback', DiscussionReview: 'received_discussion_feedback'}
    #
    #     for sid, obj in self.studentRepo.data.items():
    #         d = {
    #             'student': obj.name,
    #             'canvas_id': sid,
    #             'csun_id': obj.sis_user_id
    #         }
    #         for c in self.components:
    #             if len( self.assignRepo.get_associations() ) > 0:
    #                 try:
    #                     # get the record where the student is the reviwer
    #                     a = self.assignRepo.get_by_reviewer( sid )
    #                     # get the name of the student being assessed
    #                     d[ 'reviewing' ] = self.studentRepo.get_student_name( a.assessee_id )
    #                     d[ 'reviewing_id' ] = a.assessee_id
    #                     # get the record where the student is the author
    #                     b = self.assignRepo.get_by_author( sid )
    #                     # get the name
    #                     d[ 'reviewed_by' ] = self.studentRepo.get_student_name( b.assessor_id )
    #                     d[ 'reviewed_by_id' ] = b.assessor_id
    #                 except AttributeError:
    #                     pass
    #
    #             self.add_invites( d, c, sid )
    #
    #             self.add_reviews( d, c, sid )
    #
    #         self.data.append( d )
    @property
    def data( self ):
        return self.repo.data[ SKAA_ORDER ]

        # self.data = pd.DataFrame( self.data )
        # self.data = self.data[ SKAA_ORDER ]
        # discussion_data = pd.DataFrame( discussion_data )

    @property
    def essay( self ):
        """
        Return students who have done initial work and been assigned a reviewer

        :return: DataFrame
        """
        return self.repo.essay
        # return self.data[ ~self.data.reviewing.isnull() ]

    @property
    def no_essay( self ):
        """
        Students who have not submitted the initial work
        :return: DataFrame
        """
        return self.repo.no_essay
        # return self.data[ self.data.reviewing.isnull() ]

    @property
    def reviewed( self ):
        """
        Returns the subset of students who have turned in the initial work
        whose reviewer has turned in the review

        :return: DataFrame
        """
        return self.repo.reviewed
        # Students whose reviewer has and has not turned in review
        # return self.essay[ ~self.essay.received_feedback_on_essay.isnull() ]

    @property
    def non_reviewed( self ):
        """
        Returns the subset of students who have turned in the initial work
        whose reviewer has NOT turned in the review

        Drops the 'reviewing' column in results since that can be
        confusing in this context
        :return: DataFrame
        """
        return self.repo.non_reviewed.drop( [ 'reviewing' ], axis=1 )
        # return self.essay[ self.essay.received_feedback_on_essay.isnull() ]

    @property
    def metareviewed( self ):
        """
        Returns the subset of students who have turned in the initial work
        whose author has turned in the metareview

        Drops the 'reviewed_by' column in results since that can be
        confusing in this context

        :return: DataFrame
        """
        # Metareviewer turned in
        return self.repo.metareviewed.drop( [ 'reviewed_by' ], axis=1 )
        # self.metareviewed = self.ca[ ~self.ca.received_feedback_on_review.isnull() ].drop( [ 'reviewed_by' ], axis=1 )

    @property
    def non_metareviewed( self ):
        """
        Returns the subset of students who have turned in the initial work
        whose author has turned in the metareview

        Drops the 'reviewed_by' column in results since that can be
        confusing in this context

        :return: DataFrame
        """
        return self.repo.non_metareviewed.drop( [ 'reviewed_by' ], axis=1 )
        # return self.essay[ self.essay.received_feedback_on_review.isnull() ].drop( [ 'reviewed_by' ], axis=1 )

    #
    # def add_invites( self, data_dict, component, student_id ):
    #     invite_fields = { Review: 'invited_to_review', MetaReview: 'invited_to_metareview',
    #                       DiscussionReview: 'invited_to_discussion_review' }
    #
    #     invite_fieldname = invite_fields.get( type( component ) )
    #
    #     if invite_fieldname is not None:
    #         inv = InvitationStatusRepository( self.dao, component )
    #         data_dict[ invite_fieldname ] = pd.to_datetime( inv.received_at( student_id ) )
    #
    # skaa_data = load( studentRepo, skaa_components )
    # discussion_data = load( studentRepo, discussion_components )

    def print_counts( self ):
        print( "\n~~~~~~~~~~~~~~~~~~~~~ SKAA ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~" )
        print( "===================== initial work =====================" )
        print( "{} students have turned in essay and been paired up".format( len( self.essay ) ) )
        print( "{} students haven't turned in essay".format( len( self.no_essay ) ) )

        print( "\n===================== review =====================" )
        print( "{} students' reviewers has turned in the review".format( len( self.reviewed ) ) )
        print( "{} students have a reviewer who hasn't turned in the review".format( len( self.non_reviewed ) ) )

        print( "\n===================== metareview =====================" )
        print( "{} students' authors have turned in the metareview".format( len( self.metareviewed ) ) )
        print( "{} students' authors haven't turned in the metareview".format( len( self.non_metareviewed ) ) )
        print( "\n" )

    # def add_reviews( self, data_dict, component, student_id ):
    #     # Note: can't do in similar way to invitations since invited to metareview and received ca feedback
    #     # use different activities. The invitation is for the upcoming one which provides feedback
    #
    #     # on the previous one
    #     # set to none so won't overwrite on next time through
    #     fb_fieldname = None
    #
    #     if isinstance( component, InitialWork ):
    #         # we can't use the review object because feedback on the review
    #         # comes from the metareview
    #         fb_fieldname = 'received_feedback_on_essay'
    #
    #     if isinstance( component, Review ):
    #         fb_fieldname = 'received_feedback_on_review'
    #
    #     if isinstance( component, DiscussionForum ):
    #         fb_fieldname = 'received_discussion_feedback'
    #
    #     if fb_fieldname is not None:
    #         fr = FeedbackStatusRepository( self.dao, component )
    #         data_dict[ fb_fieldname ] = pd.to_datetime( fr.received_at( student_id ) )


class DiscussionDashboard:
    """
    This is in charge of displaying information from the
    discussion overview repository

    """

    def __init__( self, overview_repo ):
        self.repo = overview_repo

    # def load( self, unit):
    #     """
    #     Initializes and loads all data.
    #
    #     :return:
    #     """
    #
    #     # define here so will reset every load
    #     self.data = [ ]
    #
    #     self.unit = unit
    #     # The activity whose id is used to store review pairings for the whole SKAA
    #     self.activity_for_review_pairings = self.unit.discussion_review
    #     self.components = [ c for c in self.unit.components if isinstance( c, DiscussionGroup ) ]
    #
    #     self.studentRepo = StudentRepository( environment.CONFIG.course )
    #     self.studentRepo.download()
    #
    #     self._initialize_db()
    #
    #     self.assignRepo = AssociationRepository( self.dao, self.activity_for_review_pairings )
    #
    #     # Load and display counts
    #     self.get_data()
    #     self.print_counts()

    # def get_data( self ):
    # invite_fields = { Review: 'invited_to_review', MetaReview: 'invited_to_metareview',
    #                   DiscussionReview: 'invited_to_discussion_review' }
    #     feedback_fields = {Review: 'received_ca_feedback', MetaReview: 'received_meta_feedback', DiscussionReview: 'received_discussion_feedback'}

    # for sid, obj in self.studentRepo.data.items():
    #     d = {
    #         'student': obj.name,
    #         'canvas_id': sid,
    #         'csun_id': obj.sis_user_id
    #     }
    #     for c in self.components:
    #         if len( self.assignRepo.get_associations() ) > 0:
    #             try:
    #                 # get the record where the student is the reviwer
    #                 a = self.assignRepo.get_by_reviewer( sid )
    #                 # get the name of the student being assessed
    #                 d[ 'reviewing' ] = self.studentRepo.get_student_name( a.assessee_id )
    #                 d[ 'reviewing_id' ] = a.assessee_id
    #                 # get the record where the student is the author
    #                 b = self.assignRepo.get_by_author( sid )
    #                 # get the name
    #                 d[ 'reviewed_by' ] = self.studentRepo.get_student_name( b.assessor_id )
    #                 d[ 'reviewed_by_id' ] = b.assessor_id
    #             except AttributeError:
    #                 pass
    #
    #         self.add_invites( d, c, sid )
    #
    #         self.add_reviews( d, c, sid )
    #
    #     self.data.append( d )
    #
    # self.data = pd.DataFrame( self.data )

    @property
    def data( self ):
        return self.repo.data[ DISCUSSION_ORDER ]

    @property
    def posters( self ):
        """
        Students who have posted and been assigned reviewers
        :return: DataFrame
        """
        return self.repo.posters

    @property
    def non_posters( self ):
        """
        Students who have not posted and thus not been assigned a reviewer
        :return: DataFrame
        """
        return self.repo.non_posters

    @property
    def reviewed( self ):
        return self.repo.reviewed

    @property
    def non_reviewed( self ):
        """
        Returns students whose reviewer hasn't turned in the review.

        Drops the reviewing column to avoid confusion
        :return:
        """
        return self.repo.non_reviewed.drop( [ 'reviewing' ], axis=1 )

    #     #
    #     # # Students whose reviewer has and has not turned in review
    #     # self.reviewed = self.posters[ ~self.posters.received_discussion_feedback.isnull() ]
    #     # self.non_reviewed = self.posters[ self.posters.received_discussion_feedback.isnull() ].drop( [ 'reviewing' ],
    #     #                                                                                             axis=1 )
    #
    # def add_invites( self, data_dict, component, student_id ):
    #     invite_fields = { DiscussionReview: 'invited_to_discussion_review' }
    #
    #     invite_fieldname = invite_fields.get( type( component ) )
    #
    #     if invite_fieldname is not None:
    #         inv = InvitationStatusRepository( self.dao, component )
    #         data_dict[ invite_fieldname ] = pd.to_datetime( inv.received_at( student_id ) )
    #
    # def add_reviews( self, data_dict, component, student_id ):
    #     # Note: can't do in similar way to invitations since invited to metareview and received ca feedback
    #     # use different activities. The invitation is for the upcoming one which provides feedback
    #     # on the previous one
    #
    #     # set to none so won't overwrite on next time through
    #     fb_fieldname = None
    #
    #     if isinstance( component, DiscussionForum ):
    #         fb_fieldname = 'received_discussion_feedback'
    #
    #     if fb_fieldname is not None:
    #         fr = FeedbackStatusRepository( self.dao, component )
    #         data_dict[ fb_fieldname ] = pd.to_datetime( fr.received_at( student_id ) )

    def print_counts( self ):
        print( "\n~~~~~~~~~~~~~~~~~~~ DISCUSSION ~~~~~~~~~~~~~~~~~~~~~~~~~" )
        print( "===================== Discussion posts =====================" )
        print( "{} students have turned in posts and been paired up".format( len( self.posters ) ) )
        print( "{} students have not posted".format( len( self.non_posters ) ) )

        print( "\n===================== review =====================" )
        print( "{} students' reviewers has turned in the review".format( len( self.reviewed ) ) )
        print( "{} students have a reviewer who hasn't turned in the review".format( len( self.non_reviewed ) ) )
        print( "\n" )
