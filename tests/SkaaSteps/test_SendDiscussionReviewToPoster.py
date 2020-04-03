"""
Created by adam on 3/2/20
"""
__author__ = 'adam'

from unittest.mock import MagicMock, create_autospec, patch

from faker import Faker

from CanvasHacks.DAOs.sqlite_dao import SqliteDAO
from CanvasHacks.Messaging.discussions import FeedbackFromDiscussionReviewMessenger
from CanvasHacks.Definitions.discussion import DiscussionReview
from CanvasHacks.Repositories.status import FeedbackStatusRepository
from CanvasHacks.SkaaSteps.SendDiscussionReviewToPoster import SendDiscussionReviewToPoster
from tests.TestingBase import TestingBase
from tests.factories.ModelFactories import student_factory
from tests.factories.PeerReviewedFactories import unit_factory
from tests.factories.RepositoryMocks import ContentRepositoryMock

fake = Faker()

if __name__ == '__main__':
    pass


class TestUnitTests(TestingBase):
    """Unit tests with all dependencies mocked"""
    def setUp( self ):
        self.config_for_test()
        self.unit = unit_factory()
        self.activity = self.unit.discussion_review
        self.course = MagicMock()

        # student recieiving the message
        self.author = student_factory()
        self.reviewer = student_factory()

        # This would be the content unit
        self.work = fake.text()
        # Set to none so that loader thinks not a quiz
        self.activity_id = self.unit.discussion_review.id
        self.dao = SqliteDAO()
        self.session = self.dao.session
        self.create_new_and_preexisting_students()
        # Prepare fake work repo to give values to calling  objects

        # self.studentRepo = StudentRepository()
        # self.studentRepo.get_student = MagicMock( return_value=self.reviewer )
        self.contentRepo = ContentRepositoryMock()
        self.contentRepo.get_formatted_work_by = MagicMock( return_value=self.work )
        self.review_assign = MagicMock( assessor_id=self.reviewer.id, assessee_id=self.author.id )
        self.statusRepo = MagicMock()
        # Prepare fake work repo to give values to calling  objects
        self.workRepo = ContentRepositoryMock()
        self.workRepo.create_test_content( self.student_ids )
        self.workRepo.add_students_to_data( self.student_ids, make_dataframe=True )

    def test_instantiates_correct_status_repos( self ):
        """The sending of metareview results requires a
        special status repository"""
        obj = SendDiscussionReviewToPoster( course=self.course, unit=self.unit, is_test=True, send=True )

        self.assertIsInstance(obj.statusRepos, list, "status repos is a list")
        self.assertTrue(len(obj.statusRepos) == 1)
        self.assertIsInstance(obj.feedback_status_repo, FeedbackStatusRepository, "Invite repo instantiated")

    @patch( 'CanvasHacks.SkaaSteps.SendDiscussionReviewToPoster.FeedbackStatusRepository' )
    @patch( 'CanvasHacks.Messaging.base.ConversationMessageSender.send' )
    @patch( 'CanvasHacks.SkaaSteps.ISkaaSteps.StudentRepository' )
    @patch( 'CanvasHacks.SkaaSteps.SendDiscussionReviewToPoster.WorkRepositoryLoaderFactory' )
    def test__message_step( self, workLoaderMock, studentRepoMock, messengerMock, statusRepoMock ):
        students = { s.student_id: s for s in self.students }

        def se( sid ):
            return students.get( sid )

        obj = SendDiscussionReviewToPoster( course=self.course, unit=self.unit, is_test=True, send=True )

        # setup work repository (use all students since no filtering occurs here)
        self.workRepo.submitter_ids = self.student_ids
        obj.work_repo = self.workRepo
        # setup students
        obj.studentRepo.get_student = MagicMock( side_effect=se )
        obj.studentRepo.download = MagicMock( return_value=self.students )
        # setup review pairings
        preexisting_pairings = self.create_preexisting_review_pairings( self.activity_id, self.students,
                                                                        obj.dao.session )
        obj.associations = preexisting_pairings

        # call
        obj._message_step()

        # ================== Events on Messenger
        # Check that mocked objects were called with expected data
        messengerMock.assert_called()
        self.assertEqual( messengerMock.call_count, len( self.student_ids ),
                          "Send method called expected number of times" )
        messenger_args = [ (c[ 1 ][ 'student_id' ], c[ 1 ][ 'subject' ], c[ 1 ][ 'body' ]) for c in
                           messengerMock.call_args_list ]
        # print(args)

        # Check that all messages have the correct subject
        for sid, subj, body in messenger_args:
            expect_subj = FeedbackFromDiscussionReviewMessenger.email_subject_templ.format(self.unit.unit_number)
            self.assertEqual( expect_subj, subj, "Correct subject line" )

        # Status repo calls on messenger
        obj.messenger.status_repositories[0].record.assert_called()
        call_list = obj.messenger.status_repositories[0].record.call_args_list
        status_args = [ c[ 0 ][ 0 ] for c in call_list ]
        self.assertEqual( len( self.students ), len( call_list ),
                          "Status repo record called expected number of times" )
        for sid in self.student_ids:
            self.assertIn( sid, status_args, "StatusRepo.record called on all students" )

        # student repo calls on messenger
        for sid in self.student_ids:
            obj.messenger.student_repository.get_student.assert_any_call( sid )

        # Check the content sent
        for record in obj.associations:
            # This is the review which the assessor has submitted
            author_text = self.workRepo.get_formatted_work_by( record.assessor_id )
            # which we are sending to the person who created the posts
            sent_text = [ t[ 2 ] for t in messenger_args if t[ 0 ] == record.assessee_id ][ 0 ]
            rx = r'{}'.format( author_text )
            self.assertRegex( sent_text, rx, "Author's work in message sent to reviewer" )

    @patch( 'CanvasHacks.SkaaSteps.ISkaaSteps.DisplayManager' )
    def test__assign_step( self, displayManagerMock ):
        # self.workRepo.remove_student_records = MagicMock()
        # workLoaderMock.make = MagicMock( return_value=self.workRepo )

        obj = SendDiscussionReviewToPoster( course=self.course, unit=self.unit, is_test=True, send=True )
        obj.work_repo = MagicMock( submitter_ids=self.preexisting_student_ids )
        obj._filter_notified = MagicMock()
        self.preexisting_pairings = self.create_preexisting_review_pairings( self.activity_id, self.students, obj.dao.session )

        # call
        obj._assign_step()

        # check
        obj._filter_notified.assert_called()
        self.assertEqual( len( self.preexisting_student_ids ), len( obj.associations ) )

    def test__filter_notified( self ):
        num_previous = 2
        # Instantiate so can use its dao for setup
        obj = SendDiscussionReviewToPoster( course=self.course, unit=self.unit, is_test=True, send=True )
        self.create_preexisting_review_pairings( self.activity_id, self.students, obj.dao.session )

        self.make_feedback_received_records( num_previous, session=obj.dao.session )

        self.workRepo = MagicMock()
        obj.work_repo = self.workRepo

        reviewers_with_notified_authors = [ r.assessor_id for r in self.pairings if r.assessee_id in self.previously_sent ]

        # print(reviewers_with_authors_sent_feedback)
        # ra = obj.dao.session.query(ReviewAssociation).all()
        # fb = obj.dao.session.query(FeedbackReceivedRecord).all()

        # call
        obj._filter_notified()

        # check
        self.assertIsInstance( obj.statusRepos[0], FeedbackStatusRepository, "Correct status repo used" )

        self.workRepo.remove_student_records.assert_called()

        call_args = [ c[ 0 ][ 0 ] for c in self.workRepo.remove_student_records.call_args_list ]

        print(call_args)

        expected = [r for r in self.student_ids if r in reviewers_with_notified_authors]
        self.assertEqual( expected, call_args[ 0 ],
                          "Submitters whose authors have already been sent feedback were removed" )

        #
        #
        # num_previously_sent_results = 3
        # previously_notified_authors = self.student_ids[ :num_previously_sent_results ]
        # non_notified_authors = self.student_ids[ num_previously_sent_results: ]
        # self.assertEqual( len( self.student_ids ),
        #                   len( non_notified_authors ) + len( previously_notified_authors ),
        #                   "dummy check of setup" )
        #
        # # Instantiate so can use its dao for setup
        # obj = SendDiscussionReviewToPoster( course=self.course, unit=self.unit, is_test=True, send=True )
        # self.create_preexisting_review_pairings( self.activity_id, self.students, obj.dao.session )
        #
        # for sid in non_notified_authors:
        #     obj.statusRepos.record_sent_feedback(sid)
        #
        # assocs = obj.dao.session.query( ReviewAssociation )\
        #     .filter( ReviewAssociation.activity_id == self.activity_id) \
        #     .all()
        #
        # submitters_whose_authors_have_been_notified = [ s for s in assocs if s.assessee_id in previously_notified_authors ]
        #
        # # submitters_whose_authors_have_been_notified = [ obj.associationRepo.get_by_assessee( self.activity, sid ) for sid in previously_notified_authors ]
        #
        # submitters_whose_authors_have_been_notified = [ s.assessor_id for s in
        #                                                 submitters_whose_authors_have_been_notified ]
        #
        # submitters_whose_authors_not_notified = [ s for s in self.student_ids if
        #                                           s not in submitters_whose_authors_have_been_notified ]
        #
        # # Suppose that everyone has submitted their review before this run
        # self.workRepo.submitter_ids = self.student_ids
        #
        # # obj.statusRepos = create_autospec( FeedbackStatusRepository,
        # #                                               previously_received_feedback=non_notified_authors )
        #
        # self.workRepo.remove_student_records = MagicMock()
        # obj.work_repo = self.workRepo
        #
        # # call
        # obj._filter_notified()


    @patch( 'CanvasHacks.SkaaSteps.ISkaaSteps.DisplayManager' )
    @patch( 'CanvasHacks.SkaaSteps.SendDiscussionReviewToPoster.WorkRepositoryLoaderFactory' )
    def test__load_step( self, workLoaderMock, displayManagerMock ):
        self.workRepo.remove_student_records = MagicMock()
        workLoaderMock.make = MagicMock( return_value=self.workRepo )

        obj = SendDiscussionReviewToPoster( course=self.course, unit=self.unit, is_test=True, send=True )
        # obj.display_manager = create_autospec(DisplayManager)

        # obj.statusRepos = create_autospec(FeedbackStatusRepository,  previously_sent_students=self.preexisting_student_ids)
        # call
        obj._load_step()

        # check
        workLoaderMock.make.assert_called()
        displayManagerMock.assert_called()

        call_args = [ c[ 0 ][ 0 ] for c in workLoaderMock.call_args_list ]
        print( call_args )
        # self.assertEqual()

        # obj.display_manager.assert_called()

        # self.workRepo.remove_student_records.assert_called()
        # call_args = [  c[ 0 ][ 0 ] for c in self.workRepo.remove_student_records.call_args_list]
        # self.assertEqual(self.preexisting_student_ids, call_args[0] )

    def test_audit_frame( self ):
        self.skipTest( "todo" )


class TestFunctionalTests( TestingBase ):

    def setUp( self ):
        self.config_for_test()
        self.unit = unit_factory()
        self.activity = self.unit.discussion_review
        self.course = MagicMock()

        # student recieiving the message
        self.author = student_factory()
        self.reviewer = student_factory()

        # This would be the content unit
        self.work = fake.text()
        # Set to none so that loader thinks not a quiz
        self.activity_id = self.unit.discussion_review.id
        self.dao = SqliteDAO()
        self.session = self.dao.session
        self.create_new_and_preexisting_students()
        # Prepare fake work repo to give values to calling  objects

        # self.studentRepo = StudentRepository()
        # self.studentRepo.get_student = MagicMock( return_value=self.reviewer )
        self.contentRepo = ContentRepositoryMock()
        self.contentRepo.get_formatted_work_by = MagicMock( return_value=self.work )
        self.review_assign = MagicMock( assessor_id=self.reviewer.id, assessee_id=self.author.id )
        self.statusRepo = MagicMock()
        # Prepare fake work repo to give values to calling  objects
        self.workRepo = ContentRepositoryMock()
        self.workRepo.create_test_content( self.student_ids )
        self.workRepo.add_students_to_data( self.student_ids, make_dataframe=True )

    def test_instantiates_w_correct_values( self ):
        """Dummy checking in case some of the main variables used change"""
        obj = SendDiscussionReviewToPoster( course=self.course, unit=self.unit, is_test=True, send=True )

        self.assertIsInstance( obj.statusRepos[0], FeedbackStatusRepository, "Correct status repo instantiated" )
        self.assertEqual( obj.statusRepos[0].activity, self.activity, "Status repo instantiated with correct activity" )

        self.assertIsInstance(obj.activity_notifying_about, DiscussionReview, "Notifying about expected type of activity")
        self.assertEqual(obj.activity_notifying_about, self.unit.discussion_review, "Expected activity")

        self.assertIsInstance( obj.activity_for_review_pairings, DiscussionReview,
                               "Review pairings based on expected activity type: Discussion review" )
        self.assertEqual( obj.activity_for_review_pairings, self.unit.discussion_review, "Expected activity" )

        self.assertIsInstance( obj.activity, DiscussionReview,
                               "Working on results from expected  activity type" )
        self.assertEqual( obj.activity, self.unit.discussion_review, "Expected activity" )

    @patch( 'CanvasHacks.Messaging.base.ConversationMessageSender.send' )
    @patch( 'CanvasHacks.SkaaSteps.ISkaaSteps.StudentRepository' )
    @patch( 'CanvasHacks.SkaaSteps.SendDiscussionReviewToPoster.WorkRepositoryLoaderFactory' )
    def test_run_first_time_for_activity( self, workLoaderMock, studentRepoMock, messengerMock ):
        # even though this will be the result of the filtering
        # we need to limit here since the mock doesn't have the property
        self.workRepo.submitter_ids = self.student_ids
        workLoaderMock.make = MagicMock( return_value=self.workRepo )

        students = { s.student_id: s for s in self.students }

        def se( sid ):
            return students.get( sid )

        obj = SendDiscussionReviewToPoster( course=self.course, unit=self.unit, is_test=True, send=True )

        # setup students
        obj.studentRepo.get_student = MagicMock( side_effect=se )
        obj.studentRepo.download = MagicMock( return_value=self.students )
        # setup review pairings
        preexisting_pairings = self.create_preexisting_review_pairings( self.activity_id, self.students,
                                                                        obj.dao.session )
        obj.statusRepos = [create_autospec( FeedbackStatusRepository, previously_sent_students=[ ] )]

        # call
        obj.run()

        # ================== Events on Messenger
        # Check that mocked objects were called with expected data
        # Every student should've been messaged
        messengerMock.assert_called()
        self.assertEqual( messengerMock.call_count, len( self.student_ids ),
                          "Send method called expected number of times" )
        messenger_args = [ (c[ 1 ][ 'student_id' ], c[ 1 ][ 'subject' ], c[ 1 ][ 'body' ]) for c in
                           messengerMock.call_args_list ]

        # Check that all messages have the correct subject
        for sid, subj, body in messenger_args:
            expect_subj = FeedbackFromDiscussionReviewMessenger.email_subject_templ.format( self.unit.unit_number )
            self.assertEqual( expect_subj, subj, "Correct subject line" )

        # Status repo calls on messenger
        obj.messenger.status_repositories[0].record.assert_called()
        call_list = obj.messenger.status_repositories[0].record.call_args_list
        status_args = [ c[ 0 ][ 0 ] for c in call_list ]
        self.assertEqual( len( self.student_ids ), len( call_list ),
                          "Status repo record called expected number of times" )
        for sid in self.student_ids:
            self.assertIn( sid, status_args, "StatusRepo.record called on all students" )

        # student repo calls on messenger
        for sid in self.student_ids:
            obj.messenger.student_repository.get_student.assert_any_call( sid )

        # Check the content sent
        for record in obj.associations:
            # This is the review which the assessor has submitted
            author_text = self.workRepo.get_formatted_work_by( record.assessor_id )
            # which we are sending to the person who created the posts
            sent_text = [ t[ 2 ] for t in messenger_args if t[ 0 ] == record.assessee_id ][ 0 ]
            rx = r'{}'.format( author_text )
            self.assertRegex( sent_text, rx, "Author's work in message sent to reviewer" )

    # @patch( 'CanvasHacks.SkaaSteps.ISkaaSteps.FeedbackStatusRepository' )
    @patch( 'CanvasHacks.Messaging.base.ConversationMessageSender.send' )
    @patch( 'CanvasHacks.SkaaSteps.ISkaaSteps.StudentRepository' )
    @patch( 'CanvasHacks.SkaaSteps.SendDiscussionReviewToPoster.WorkRepositoryLoaderFactory' )
    def test_run_previously_sent( self, workLoaderMock, studentRepoMock, messengerMock ):
        authors_who_have_not_been_notified = self.new_students_ids
        authors_who_have_been_previously_notified = self.preexisting_student_ids

        students = { s.student_id: s for s in self.students }

        def se( sid ):
            return students.get( sid )

        obj = SendDiscussionReviewToPoster( course=self.course, unit=self.unit, is_test=True, send=True )

        # setup students
        obj.studentRepo.get_student = MagicMock( side_effect=se )
        obj.studentRepo.download = MagicMock( return_value=self.students )
        # setup review pairings
        preexisting_pairings = self.create_preexisting_review_pairings( self.activity_id, self.students,
                                                                        obj.dao.session )
        reviewers_with_notified_authors = [r.assessor_id for r in preexisting_pairings if r.assessee_id in authors_who_have_been_previously_notified]
        reviewers_without_notified_authors = [s for s in self.student_ids if s not in reviewers_with_notified_authors]
        obj.statusRepos = [create_autospec( FeedbackStatusRepository, reviewers_with_notified_authors=reviewers_with_notified_authors )]

        # This will be handled by the _filter_notified step. But since
        # we are using a dummy work repo, calling remove_student_records won't do anything
        # Thus we need to pretend that it did its job. (We've tested it elsewhere)
        self.workRepo.submitter_ids = reviewers_without_notified_authors
        workLoaderMock.make = MagicMock( return_value=self.workRepo )

        # call
        obj.run()

        # ================== Events on Messenger
        # Check that mocked objects were called with expected data
        messengerMock.assert_called()
        self.assertEqual( messengerMock.call_count, len( authors_who_have_not_been_notified ),
                          "Send method called expected number of times" )
        messenger_args = [ (c[ 1 ][ 'student_id' ], c[ 1 ][ 'subject' ], c[ 1 ][ 'body' ]) for c in
                           messengerMock.call_args_list ]

        # Check that all messages have the correct subject
        for sid, subj, body in messenger_args:
            expect_subj = FeedbackFromDiscussionReviewMessenger.email_subject_templ.format( self.unit.unit_number )
            self.assertEqual( expect_subj, subj, "Correct subject line" )

        # Status repo calls on messenger which
        # record the message having been sent to authors
        obj.messenger.status_repositories[0].record.assert_called()
        call_list = obj.messenger.status_repositories[0].record.call_args_list
        status_args = [ c[ 0 ][ 0 ] for c in call_list ]
        self.assertEqual( len( authors_who_have_not_been_notified ), len( call_list ),
                          "Status repo record called expected number of times" )
        for sid in authors_who_have_not_been_notified:
            self.assertIn( sid, status_args,
                           "StatusRepo.record called on authors who have now received their feedback (i.e., from newly submitted reviewers)" )

        # student repo calls on messenger
        for sid in authors_who_have_not_been_notified:
            obj.messenger.student_repository.get_student.assert_any_call( sid )

        # Check the content sent
        for record in obj.associations:
            # This is the review which the assessor has submitted
            author_text = self.workRepo.get_formatted_work_by( record.assessor_id )
            # which we are sending to the person who created the posts
            sent_text = [ t[ 2 ] for t in messenger_args if t[ 0 ] == record.assessee_id ][ 0 ]
            rx = r'{}'.format( author_text )
            self.assertRegex( sent_text, rx, "Author's work in message sent to reviewer" )

    #
    # @patch( 'CanvasHacks.SkaaSteps.ISkaaSteps.StatusRepository' )
    #     @patch( 'CanvasHacks.Messaging.base.ConversationMessageSender.send' )
    #     @patch( 'CanvasHacks.SkaaSteps.ISkaaSteps.StudentRepository' )
    #     @patch( 'CanvasHacks.SkaaSteps.SendDiscussionReviewToPoster.WorkRepositoryLoaderFactory' )
    #     def test_run( self, workLoaderMock, studentRepoMock, messengerMock, feedbackStatusRepoMock ):
    #         self.workRepo.submitter_ids = self.new_students_ids
    #
    #         workLoaderMock.make = MagicMock( return_value=self.workRepo )
    #
    #         # prepare student repo
    #         students = { s.student_id: s for s in self.students }
    #
    #         def se( sid ):
    #             return students.get( sid )
    #
    #         # studentRepoMock.get_student = MagicMock(side_effect=se)
    #         # studentRepoMock.download = MagicMock( return_value=self.students )
    #
    #         # call
    #         obj = SendDiscussionReviewToPoster( course=self.course, unit=self.unit, is_test=True, send=True )
    #         # obj.studentRepo = MagicMock()
    #         obj.studentRepo.get_student = MagicMock( side_effect=se )
    #         obj.studentRepo.download = MagicMock( return_value=self.students )
    #         self.preexisting_pairings = self.create_preexisting_review_pairings( self.activity_id, self.students,
    #                                                                         obj.dao.session )
    #
    #         obj.run()
    #
    #         # check
    #
    #         # Check that new assignments don't involve students who haven't submitted
    #         for rec in obj.associations:
    #             self.assertNotIn( rec.assessor_id, self.preexisting_student_ids,
    #                               "Newly assigned assessor not among previously assigned students" )
    #             self.assertNotIn( rec.assessee_id, self.preexisting_student_ids,
    #                               "Newly assigned assessee not among previously assigned students" )
    #
    #         # Check whether each new student has been assigned
    #         new_assessor_ids = [ r.assessor_id for r in obj.associations ]
    #         new_assessee_ids = [ r.assessee_id for r in obj.associations ]
    #         self.assertEqual( len( set( new_assessor_ids ) ), len( self.new_students_ids ),
    #                           "No duplicate assessor assignments" )
    #         self.assertEqual( len( set( new_assessee_ids ) ), len( self.new_students_ids ),
    #                           "No duplicate assessee assignments" )
    #         for sid in self.new_students_ids:
    #             self.assertIn( sid, new_assessee_ids, "Student is an assessee" )
    #             self.assertIn( sid, new_assessor_ids, "Student is an assessor" )
    #
    #         # ================== Events on Messenger
    #         # Check that mocked objects were called with expected data
    #         messengerMock.assert_called()
    #         self.assertEqual( messengerMock.call_count, len( self.new_students_ids ),
    #                           "Send method called expected number of times" )
    #         messenger_args = [ (c[ 1 ][ 'student_id' ], c[ 1 ][ 'subject' ], c[ 1 ][ 'body' ]) for c in
    #                            messengerMock.call_args_list ]
    #         # print(args)
    #
    #         # Check that all messages have the correct subject
    #         for sid, subj, body in messenger_args:
    #             self.assertEqual( FeedbackFromDiscussionReviewMessenger.email_subject, subj, "Correct subject line" )
    #
    #         # Status repo calls on messenger
    #         obj.messenger.status_repositories.record.assert_called()
    #         call_list = obj.messenger.status_repositories.record.call_args_list
    #
    #         # obj.messenger.status_repositories.record_invited.assert_called()
    #         # call_list = obj.messenger.status_repositories.record_invited.call_args_list
    #         status_args = [ c[ 0 ][ 0 ] for c in call_list ]
    #         self.assertEqual( len( self.new_students ), len( call_list ),
    #                           "Status repo record_invited called expected number of times" )
    #         for sid in self.new_students_ids:
    #             self.assertIn( sid, status_args, "StatusRepo.record_invited called on all students" )
    #
    #         # student repo calls on messenger
    #         for sid in self.new_students_ids:
    #             obj.messenger.student_repository.get_student.assert_any_call( sid )
    #
    #         # Check the content sent
    #         for record in obj.associations:
    #             # print(record.assessee_id)
    #             author_text = self.workRepo.get_formatted_work_by( record.assessee_id )
    #             # see if sent to assessor
    #             sent_text = [ t[ 2 ] for t in messenger_args if t[ 0 ] == record.assessor_id ][ 0 ]
    #             rx = r'{}'.format( author_text )
    #             self.assertRegex( sent_text, rx, "Author's work in message sent to reviewer" )

