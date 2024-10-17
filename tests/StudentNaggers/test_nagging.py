"""
Created by adam on 10/18/20
"""
__author__ = 'adam'

from unittest.mock import MagicMock, patch

import pytz
from faker import Faker

import CanvasHacks.testglobals
from tests.TestingBase import TestingBase
from tests.factories.PeerReviewedFactories import unit_factory

CanvasHacks.testglobals.use_api = False

from CanvasHacks.Messaging.nagging import ReviewNonSubmittersMessaging, REVIEW_NON_SUBMITTER_TEMPLATE

fake = Faker()

if __name__ == '__main__':
    pass


class TestReviewNonSubmittersMessaging( TestingBase ):

    def setUp( self ):
        self.config_for_test()

        self.unit = unit_factory()
        # self.unit.components.append(review)

        # _____________
        self.number_students = 3
        sr = { 'get_student_first_name.return_value': fake.first_name() }
        self.studentRepo = MagicMock( **sr )

        self.sids = [ fake.random.randint( 111111, 999999 ) for _ in range( 0, self.number_students ) ]
        ovr = { 'non_reviewed.reviewed_by_id.tolist.return_value': self.sids,
                'studentRepo': self.studentRepo }
        self.overviewRepo = MagicMock( **ovr )

    @patch( 'CanvasHacks.Messaging.nagging.ConversationMessageSender' )
    @patch( 'CanvasHacks.Messaging.nagging.InvitationStatusRepository' )
    def test_prepare_message( self, inviteRepo, messenger ):
        send = True
        dao = MagicMock()
        name = fake.first_name()

        obj = ReviewNonSubmittersMessaging( unit=self.unit, send=send, dao=dao )

        # Configure the thing that will return the date the student was invited
        # to do the review.
        invited_date = fake.date()
        obj.get_review_invitation_date = MagicMock( return_value=invited_date )

        d = { 'name': name,
              'assignment_name': self.unit.review.name,
              'original_due_date': self.unit.review.string_due_date,
              'invite_sent_date': invited_date
              }
        expected_body = REVIEW_NON_SUBMITTER_TEMPLATE.format( **d )

        # call
        result = obj.prepare_message( name, self.sids[ 0 ] )

        # check
        self.assertEqual(expected_body, result, "Returned the expected message text")
        obj.get_review_invitation_date.assert_called_once_with( self.sids[ 0 ] )



    @patch( 'CanvasHacks.Messaging.nagging.ConversationMessageSender' )
    @patch( 'CanvasHacks.Messaging.nagging.InvitationStatusRepository' )
    def test_get_review_invitation_date( self, inviteStatusRepo, messenger ):
        send = True
        dao = MagicMock()

        obj = ReviewNonSubmittersMessaging( unit=self.unit, send=send, dao=dao )

        # Configure the thing that will return the date the student was invited
        # to do the review.
        invited_date = fake.date( )
        invite = MagicMock( sent_at=invited_date )
        obj.invite_status_repo.get = MagicMock( return_value=invite )

        obj.make_date_for_message = MagicMock(return_value=invited_date)

        # call
        result = obj.get_review_invitation_date( self.sids[ 0 ] )

        # check
        obj.invite_status_repo.get.assert_called_once_with( self.sids[ 0 ] )

        obj.make_date_for_message.assert_called_once_with(invited_date)

        self.assertEqual( result, invited_date, "Returned the result of the mock" )

    @patch( 'CanvasHacks.Messaging.nagging.ConversationMessageSender' )
    @patch( 'CanvasHacks.Messaging.nagging.InvitationStatusRepository' )
    def test_send_message_to_student( self, inviteStatusRepo, messenger ):
        send = True
        dao = MagicMock()
        name = fake.first_name()

        obj = ReviewNonSubmittersMessaging( unit=self.unit, send=send, dao=dao )

        # Configure the thing that will return the date the student was invited
        # to do the review.
        invited_date = fake.date_time( tzinfo=pytz.utc )
        invite = MagicMock( sent_at=invited_date )
        obj.invite_status_repo.get = MagicMock( return_value=invite )

        # call
        obj.send_message_to_student( self.sids[ 0 ], name )

        # check
        obj.invite_status_repo.get.assert_called_once_with( self.sids[ 0 ] )

        subject = ReviewNonSubmittersMessaging.SUBJECT_TEMPLATE.format( self.unit.unit_number )
        expected_body = ''
        # obj.messenger.send.assert_called_once_with(student_id=self.sids[0], subject=subject)
        obj.messenger.send.assert_called()

        # record kept
        self.assertEqual( len( obj.sent ), 1, "record stored in sent" )
        self.assertEqual( obj.sent[ 0 ][ 0 ], self.sids[ 0 ], "stored record has correct student id" )


    @patch( 'CanvasHacks.Messaging.nagging.ConversationMessageSender' )
    @patch( 'CanvasHacks.Messaging.nagging.InvitationStatusRepository' )
    def test_send_message_to_student_when_send_is_false( self, inviteStatusRepo, messenger ):
        send = False
        dao = MagicMock()
        name = fake.first_name()

        obj = ReviewNonSubmittersMessaging( unit=self.unit, send=send, dao=dao )

        # Configure the thing that will return the date the student was invited
        # to do the review.
        invited_date = fake.date_time( tzinfo=pytz.utc )
        invite = MagicMock( sent_at=invited_date )
        obj.invite_status_repo.get = MagicMock( return_value=invite )

        # call
        obj.send_message_to_student( self.sids[ 0 ], name )

        # check
        obj.invite_status_repo.get.assert_called_once_with( self.sids[ 0 ] )

        subject = ReviewNonSubmittersMessaging.SUBJECT_TEMPLATE.format( self.unit.unit_number )
        obj.messenger.send.assert_not_called()

        # record kept nonetheless
        self.assertEqual( len( obj.sent ), 1, "record stored in sent" )
        self.assertEqual( obj.sent[ 0 ][ 0 ], self.sids[ 0 ], "stored record has correct student id" )
