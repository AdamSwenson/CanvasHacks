"""
Created by adam on 3/13/20
"""
__author__ = 'adam'
from CanvasHacks import environment
from CanvasHacks.DAOs.mixins import DaoMixin
from CanvasHacks.PeerReviewed.Definitions import DiscussionGroup, MetaReview, Review, DiscussionReview, SkaaReviewGroup,\
    InitialWork, DiscussionForum
from CanvasHacks.Repositories.reviewer_associations import AssociationRepository
from CanvasHacks.Repositories.status import InvitationStatusRepository, FeedbackStatusRepository
from CanvasHacks.Repositories.students import StudentRepository
import pandas as pd

if __name__ == '__main__':
    pass

SKAA_ORDER = [ 'student', 'reviewing', 'reviewed_by', 'invited_to_review',
                   'received_feedback_on_essay', 'invited_to_metareview',
                   'received_feedback_on_review', 'canvas_id', 'csun_id', 'reviewing_id', 'reviewee_id' ]


class SkaaDashboard(DaoMixin):

    def __init__(self, unit):
        self.unit = unit

        self.data = [ ]
        self.components = [ c for c in self.unit.components if isinstance( c, SkaaReviewGroup ) ]

        self.studentRepo = StudentRepository( environment.CONFIG.course )
        self.studentRepo.download()

        self._initialize_db()

        self.assignRepo = AssociationRepository( self.dao, self.unit.initial_work )


    def get_data( self ):
        #     feedback_fields = {Review: 'received_ca_feedback', MetaReview: 'received_meta_feedback', DiscussionReview: 'received_discussion_feedback'}

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

                self.add_invites(d, c, sid)

                self.add_reviews(d, c, sid)

            self.data.append( d )

        self.data = pd.DataFrame( self.data )
        self.data = self.data[ SKAA_ORDER ]
        # discussion_data = pd.DataFrame( discussion_data )

        # Divide up who has done initial work and been assigned a reviewer
        self.ca = self.data[ ~self.data.reviewing.isnull() ]
        self.no_ca = self.data[ self.data.reviewing.isnull() ]

        # Students whose reviewer has and has not turned in review
        self.reviewed = self.ca[ ~self.ca.received_feedback_on_essay.isnull() ]
        self.nonreviewed = self.ca[ self.ca.received_feedback_on_essay.isnull() ].drop( [ 'reviewing' ], axis=1 )

        # Metareviewer turned in
        self.metareviewed = self.ca[ ~self.ca.received_feedback_on_review.isnull() ].drop( [ 'reviewed_by' ],
                                                                                           axis=1 )
        self.nonmetareviewed = self.ca[ self.ca.received_feedback_on_review.isnull() ].drop( [ 'reviewed_by' ],                                                                                                 axis=1 )

    def add_invites( self, data_dict, component, student_id ):
        invite_fields = { Review: 'invited_to_review', MetaReview: 'invited_to_metareview',
                          DiscussionReview: 'invited_to_discussion_review' }

        invite_fieldname = invite_fields.get( type( component ) )

        if invite_fieldname is not None:
            inv = InvitationStatusRepository( self.dao, component )
            data_dict[ invite_fieldname ] = pd.to_datetime( inv.received_at( student_id ) )

    # skaa_data = get_data( studentRepo, skaa_components )
    # discussion_data = get_data( studentRepo, discussion_components )


    def print_counts( self ):
        print( "===================== initial work =====================" )
        print( "{} students have turned in essay and been paired up".format( len( self.ca ) ) )
        print( "{} students haven't turned in essay".format( len( self.no_ca ) ) )

        print( "===================== review =====================" )
        print( "{} students' reviewers has turned in the review".format( len( self.reviewed ) ) )
        print( "{} students have a reviewer who hasn't turned in the review".format( len( self.nonreviewed ) ) )

        print( "===================== metareview =====================" )
        print( "{} students' authors have turned in the metareview".format( len( self.metareviewed ) ) )
        print( "{} students' authors haven't turned in the metareview".format( len( self.nonmetareviewed ) ) )

    def add_reviews( self, data_dict, component, student_id ):
        # Note: can't do in similar way to invitations since invited to metareview and received ca feedback
        # use different activities. The invitation is for the upcoming one which provides feedback
        # on the previous one

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

        # set to none so won't overwrite on next time through
        fb_fieldname = None


class DiscussionDashboard(DaoMixin):

    def __init__(self, unit):
        self.unit = unit


    def _initialize( self ):
        self.studentRepo = StudentRepository( environment.CONFIG.course )
        self.studentRepo.download()

        self._initialize_db()

        self.data = [ ]
        self.components =  [ c for c in self.unit.components if isinstance( c, DiscussionGroup ) ]

    def get_data( self ):
        invite_fields = { Review: 'invited_to_review', MetaReview: 'invited_to_metareview',
                          DiscussionReview: 'invited_to_discussion_review' }
        #     feedback_fields = {Review: 'received_ca_feedback', MetaReview: 'received_meta_feedback', DiscussionReview: 'received_discussion_feedback'}

        data = [ ]
        for sid, obj in studentRepo.data.items():
            d = {
                'student': obj.name,
                'canvas_id': sid,
                'csun_id': obj.sis_user_id
            }
            for c in components:
                assignRepo = AssociationRepository( dao, c )
                if len( assignRepo.get_associations() ) > 0:
                    try:
                        # get the record where the student is the reviwer
                        a = assignRepo.get_by_reviewer( sid )
                        # get the name of the student being assessed
                        d[ 'reviewing' ] = studentRepo.get_student_name( a.assessee_id )
                        d[ 'reviewing_id' ] = a.assessee_id
                        # get the record where the student is the author
                        b = assignRepo.get_by_author( sid )
                        # get the name
                        d[ 'reviewed_by' ] = studentRepo.get_student_name( b.assessor_id )
                        d[ 'reviewed_by_id' ] = b.assessor_id
                    except AttributeError:
                        pass

                invite_fieldname = invite_fields.get( type( c ) )

                if invite_fieldname is not None:
                    inv = InvitationStatusRepository( dao, c )
                    d[ invite_fieldname ] = pd.to_datetime( inv.received_at( sid ) )

                # Note: can't do in similar way to invitations since invited to metareview and received ca feedback
                # use different activities. The invitation is for the upcoming one which provides feedback
                # on the previous one

                if isinstance( c, InitialWork ):
                    # we can't use the review object because feedback on the review
                    # comes from the metareview
                    fb_fieldname = 'received_feedback_on_essay'

                if isinstance( c, Review ):
                    fb_fieldname = 'received_feedback_on_review'

                if isinstance( c, DiscussionForum ):
                    fb_fieldname = 'received_discussion_feedback'

                if fb_fieldname is not None:
                    fr = FeedbackStatusRepository( dao, c )
                    d[ fb_fieldname ] = pd.to_datetime( fr.received_at( sid ) )

                # set to none so won't overwrite on next time through
                fb_fieldname = None

            data.append( d )
        return data

    skaa_data = get_data( studentRepo, skaa_components )
    discussion_data = get_data( studentRepo, discussion_components )

    skaa_data = pd.DataFrame( skaa_data )
    skaa_data = skaa_data[ SKAA_ORDER ]
    discussion_data = pd.DataFrame( discussion_data )

    # Divide up who has done initial work and been assigned a reviewer
    ca = skaa_data[ ~skaa_data.reviewing.isnull() ]
    no_ca = skaa_data[ skaa_data.reviewing.isnull() ]

    # Students whose reviewer has and has not turned in review
    reviewed = ca[ ~ca.received_feedback_on_essay.isnull() ]
    nonreviewed = ca[ ca.received_feedback_on_essay.isnull() ].drop( [ 'reviewing' ], axis=1 )

    # Metareviewer turned in
    metareviewed = ca[ ~ca.received_feedback_on_review.isnull() ].drop( [ 'reviewed_by' ], axis=1 )
    nonmetareviewed = ca[ ca.received_feedback_on_review.isnull() ].drop( [ 'reviewed_by' ], axis=1 )

    print( "===================== initial work =====================" )
    print( "{} students have turned in essay and been paired up".format( len( ca ) ) )
    print( "{} students haven't turned in essay".format( len( no_ca ) ) )

    print( "===================== review =====================" )
    print( "{} students' reviewers has turned in the review".format( len( reviewed ) ) )
    print( "{} students have a reviewer who hasn't turned in the review".format( len( nonreviewed ) ) )

    print( "===================== metareview =====================" )
    print( "{} students' authors have turned in the metareview".format( len( metareviewed ) ) )
    print( "{} students' authors haven't turned in the metareview".format( len( nonmetareviewed ) ) )
