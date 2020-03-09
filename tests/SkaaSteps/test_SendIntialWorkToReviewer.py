"""
Assigns a randomly selected reviewer and sends them the work

"""
from unittest.mock import MagicMock, patch

import CanvasHacks.testglobals
from CanvasHacks.Models.review_association import ReviewAssociation
from CanvasHacks.Repositories.status import InvitationStatusRepository
from tests.factories.ModelFactories import student_factory
from tests.factories.PeerReviewedFactories import unit_factory
from tests.factories.RepositoryMocks import ContentRepositoryMock

CanvasHacks.testglobals.use_api = False
from CanvasHacks.Errors.review_pairings import AllAssigned, NoAvailablePartner

from CanvasHacks.DAOs.sqlite_dao import SqliteDAO
from tests.TestingBase import TestingBase

from CanvasHacks.SkaaSteps.SendInitialWorkToReviewer import SendInitialWorkToReviewer
from faker import Faker

fake = Faker()


class TestCallsAllExpected( TestingBase ):
    """Makes sure that everything gets called with expected values.
      Not super diagnostic since many of the mocked calls are
      where we'd actually expect failure. Still, useful for catching
      problems when update code etc"""

    def setUp( self ):
        self.config_for_test()
        self.dao = SqliteDAO()

        self.course = MagicMock()
        # review = Review(**activity_data_factory())
        self.unit = unit_factory()
        # self.unit.components.append(review)

    @patch( 'CanvasHacks.SkaaSteps.SendInitialWorkToReviewer.InvitationStatusRepository' )
    @patch( 'CanvasHacks.SkaaSteps.ISkaaSteps.StudentRepository' )
    @patch( 'CanvasHacks.SkaaSteps.SendInitialWorkToReviewer.PeerReviewInvitationMessenger' )
    @patch( 'CanvasHacks.SkaaSteps.ISkaaSteps.AssociationRepository' )
    @patch( 'CanvasHacks.SkaaSteps.SendInitialWorkToReviewer.WorkRepositoryLoaderFactory' )
    def test_run( self, workLoaderMock, assocRepoMock, messengerMock, studentRepoMock, statusRepoMock ):
        """Check that each student receives the expected message
        containing the correct student's submission
        """
        students = [ student_factory(), student_factory() ]

        def student_getter( sid ):
            return [ s for s in students if s.student_id == sid ][ 0 ]

        submitter_ids = [ s.student_id for s in students ]
        workRepo = MagicMock()
        workRepo.submitter_ids = submitter_ids
        workLoaderMock.make = MagicMock( return_value=workRepo )

        studentRepoMock.download = MagicMock( return_value=students )
        studentRepoMock.get_student = student_getter

        obj = SendInitialWorkToReviewer( course=self.course, unit=self.unit, is_test=True, send=True )

        assignments = [ ReviewAssociation( assessee_id=students[ 0 ], assessor_id=students[ 1 ] ),
                        ReviewAssociation( assessee_id=students[ 1 ], assessor_id=students[ 0 ] ), ]
        obj.associationRepo.assign_reviewers = MagicMock( return_value=assignments )

        # call
        obj.run()

        # check
        workLoaderMock.make.assert_called()
        workLoaderMock.make.assert_called_with( self.unit.initial_work, self.course) # only_new=False, rest_timeout=5 )

        obj.studentRepo.download.assert_called()

        obj.associationRepo.assign_reviewers.assert_called()
        obj.associationRepo.assign_reviewers.assert_called_with( submitter_ids )

        obj.messenger.notify.assert_called()
        obj.messenger.notify.assert_called_with( assignments, True )
        # obj.messenger.notify.assert_called_with( obj.associationRepo.data, True )

        # obj.statusRepo.record_invited.assert_called()
        # obj.statusRepo.record_invited.assert_called_with(submitter_ids[0])
        # obj.statusRepo.record_invited.assert_called_with(submitter_ids[1])


class TestUnitTests(TestingBase):
    """Unit tests with all dependencies mocked"""
    def setUp( self ):
        self.config_for_test()
        self.unit = unit_factory()
        self.course = MagicMock()
        self.activity_id = self.unit.review.id
        # self.dao = SqliteDAO()
        # self.create_new_and_preexisting_students()
        # # Prepare fake work repo to give values to calling  objects
        # self.workRepo = ContentRepositoryMock()
        # self.workRepo.create_test_content( self.student_ids )
        # self.workRepo.add_students_to_data(self.student_ids, make_dataframe=True)

    def test_instantiates_correct_status_repos( self ):
        """The sending of metareview results requires a
        special status repository"""
        obj = SendInitialWorkToReviewer( course=self.course, unit=self.unit, is_test=True, send=True )

        self.assertIsInstance(obj.statusRepos, list, "status repos is a list")
        self.assertTrue(len(obj.statusRepos) == 1)
        self.assertIsInstance(obj.invite_status_repo, InvitationStatusRepository, "Invite repo instantiated")



class TestFunctionalTestWhenQuizType( TestingBase ):
    """
    Tests the entire process in various use cases using
    local data when the unit is some flavor of quiz (and thus
    uses a quiz report)

    For tests of whole process which hit server, see tests.EndToEnd
    """

    def setUp( self ):
        self.config_for_test()
        self.unit = unit_factory()
        self.course = MagicMock()

        self.activity_id = self.unit.initial_work.id
        # self.dao = SqliteDAO()
        # self.session = self.dao.session
        self.create_new_and_preexisting_students()
        # Prepare fake work repo to give values to calling  objects
        self.workRepo = ContentRepositoryMock()
        self.workRepo.create_test_content( self.student_ids )
        self.workRepo.add_students_to_data(self.student_ids, make_dataframe=True)

    @patch( 'CanvasHacks.SkaaSteps.SendInitialWorkToReviewer.InvitationStatusRepository' )
    @patch( 'CanvasHacks.Messaging.base.ConversationMessageSender.send' )
    @patch( 'CanvasHacks.SkaaSteps.ISkaaSteps.StudentRepository' )
    @patch( 'CanvasHacks.SkaaSteps.SendInitialWorkToReviewer.WorkRepositoryLoaderFactory' )
    def test_does_not_send_to_people_already_assigned( self, workLoaderMock, studentRepoMock, messengerMock,
                                                       statusRepoMock ):
        """
        Simulates a run where some students have already been assigned
        peer reviewers and a new group is being processed.

        Focus in testing is on making sure that the two groups don't get mixed up

        :param workLoaderMock:
        :param studentRepoMock:
        :param messengerMock:
        :return:
        """

        # Prepare fake work repo to give values to calling  objects
        # workRepo = ContentRepositoryMock()
        # workRepo.create_test_content( self.student_ids )
        # workRepo = create_autospec( QuizRepository )
        # workRepo.get_formatted_work_by = MagicMock( return_value=testText )
        self.workRepo.submitter_ids = self.new_students_ids
        workLoaderMock.make = MagicMock( return_value=self.workRepo )

        # prepare student repo
        students = { s.student_id: s for s in self.students }

        def se( sid ):
            return students.get( sid )

        # studentRepoMock.get_student = MagicMock(side_effect=se)
        # studentRepoMock.download = MagicMock( return_value=self.students )
        # feedbackStatusRepoMock.record_invited = MagicMock()
        # call
        obj = SendInitialWorkToReviewer( course=self.course, unit=self.unit, is_test=True, send=True )
        # obj.studentRepo = MagicMock()
        obj.studentRepo.get_student = MagicMock( side_effect=se )
        obj.studentRepo.download = MagicMock( return_value=self.students )

        # Have to do this after object creation so that we can use the
        # same in-memory db
        self.session = obj.dao.session
        preexisting_pairings = self.create_preexisting_review_pairings( self.activity_id, self.preexisting_students )

        obj.run()

        # check
        self.assertEqual( len( obj.associations ), len( self.new_students_ids ),
                          "Correct number of students assigned" )

        # Check that new assignments don't involve previously assigned sudents
        for rec in obj.associations:
            self.assertNotIn( rec.assessor_id, self.preexisting_student_ids,
                              "Newly assigned assessor not among previously assigned students" )
            self.assertNotIn( rec.assessee_id, self.preexisting_student_ids,
                              "Newly assigned assessee not among previously assigned students" )

        # Check whether each new student has been assigned
        new_assessor_ids = [ r.assessor_id for r in obj.associations ]
        new_assessee_ids = [ r.assessee_id for r in obj.associations ]
        self.assertEqual( len( set( new_assessor_ids ) ), len( self.new_students_ids ),
                          "No duplicate assessor assignments" )
        self.assertEqual( len( set( new_assessee_ids ) ), len( self.new_students_ids ),
                          "No duplicate assessee assignments" )
        for sid in self.new_students_ids:
            self.assertIn( sid, new_assessee_ids, "Student is an assessee" )
            self.assertIn( sid, new_assessor_ids, "Student is an assessor" )

        # ================== Events on Messenger
        # Check that mocked objects were called with expected data
        messengerMock.assert_called()
        self.assertEqual( messengerMock.call_count, len( self.new_students_ids ),
                          "Send method called expected number of times" )
        messenger_args = [ (c[ 1 ][ 'student_id' ], c[ 1 ][ 'subject' ], c[ 1 ][ 'body' ]) for c in
                           messengerMock.call_args_list ]
        # print(args)

        # Status repo calls on messenger
        # feedbackStatusRepoMock.record_invited.assert_called()
        obj.messenger.status_repositories[0].record.assert_called()
        call_list = obj.messenger.status_repositories[0].record.call_args_list
        status_args = [ c[ 0 ][ 0 ] for c in call_list ]
        self.assertEqual( len( self.new_students ), len( call_list ),
                          "Status repo record_invited called expected number of times" )
        for sid in self.new_students_ids:
            self.assertIn( sid, status_args, "StatusRepo.record called on all students" )

        # student repo calls on messenger
        for sid in self.new_students_ids:
            obj.messenger.student_repository.get_student.assert_any_call( sid )

        # Check the content sent
        for record in obj.associations:
            # print(record.assessee_id)
            author_text = self.workRepo.get_formatted_work_by( record.assessee_id )
            # see if sent to assessor
            sent_text = [ t[ 2 ] for t in messenger_args if t[ 0 ] == record.assessor_id ][ 0 ]
            rx = r'{}'.format( author_text )
            self.assertRegex( sent_text, rx, "Author's work in message sent to reviewer" )

    @patch( 'CanvasHacks.SkaaSteps.ISkaaSteps.StudentRepository' )
    @patch( 'CanvasHacks.SkaaSteps.SendInitialWorkToReviewer.WorkRepositoryLoaderFactory' )
    def test_raises_when_all_submitters_already_assigned( self, workLoaderMock, studentRepoMock ):

        # Prepare fake work repo to give values to calling  objects
        # workRepo = ContentRepositoryMock()
        # workRepo.create_test_content( self.preexisting_student_ids )
        # workRepo = create_autospec( QuizRepository )
        # workRepo.get_formatted_work_by = MagicMock( return_value=testText )

        # Setting to return all the previously assigned students.
        # this should cause all the students to be filtered out
        # and the errror raised
        self.workRepo.submitter_ids = self.preexisting_student_ids
        workLoaderMock.make = MagicMock( return_value=self.workRepo )

        studentRepoMock.download = MagicMock( return_value=self.students )

        # call
        obj = SendInitialWorkToReviewer( course=self.course, unit=self.unit, is_test=True, send=True )
        self.session = obj.dao.session
        preexisting_pairings = self.create_preexisting_review_pairings( self.activity_id, self.preexisting_students )

        with self.assertRaises( AllAssigned ):
            obj.run()

    @patch( 'CanvasHacks.SkaaSteps.ISkaaSteps.StudentRepository' )
    @patch( 'CanvasHacks.SkaaSteps.SendInitialWorkToReviewer.WorkRepositoryLoaderFactory' )
    def test_raises_when_only_one_submission( self, workLoaderMock, studentRepoMock ):

        # Prepare fake work repo to give values to calling  objects
        # workRepo = ContentRepositoryMock()
        # workRepo.create_test_content( self.preexisting_student_ids )
        # workRepo = create_autospec( QuizRepository )
        # workRepo.get_formatted_work_by = MagicMock( return_value=testText )

        # Setting to return all the previously assigned students.
        # this should cause all the students to be filtered out
        # and the errror raised
        self.workRepo.submitter_ids = self.preexisting_student_ids
        workLoaderMock.make = MagicMock( return_value=self.workRepo )

        studentRepoMock.download = MagicMock( return_value=self.students )

        # call
        obj = SendInitialWorkToReviewer( course=self.course, unit=self.unit, is_test=True, send=True )
        # Have to do this after object creation so that we can use the
        # same in-memory db
        self.session = obj.dao.session
        preexisting_pairings = self.create_preexisting_review_pairings( self.activity_id, self.preexisting_students )

        with self.assertRaises( AllAssigned ):
            obj.run()


class TestFunctionalTestWhenNonQuizType( TestingBase ):
    """
    Tests the entire process in various use cases using
    local data when the unit is NOT some flavor of quiz (and thus
    does not use a quiz report)

    For tests of whole process which hit server, see tests.EndToEnd
    """

    def setUp( self ):
        self.config_for_test()
        self.unit = unit_factory()
        self.course = MagicMock()

        # Set to none so that loader thinks not a quiz
        self.unit.initial_work.quiz_id = None
        self.activity_id = self.unit.initial_work.id
        self.dao = SqliteDAO()
        self.session = self.dao.session
        self.create_new_and_preexisting_students()
        # Prepare fake work repo to give values to calling  objects
        self.workRepo = ContentRepositoryMock()
        self.workRepo.create_test_content( self.student_ids )
        self.workRepo.add_students_to_data(self.student_ids, make_dataframe=True)

        # workRepo = create_autospec( QuizRepository )
        # workRepo.get_formatted_work_by = MagicMock( return_value=testText )

    @patch( 'CanvasHacks.SkaaSteps.SendInitialWorkToReviewer.InvitationStatusRepository' )
    @patch( 'CanvasHacks.Messaging.base.ConversationMessageSender.send' )
    @patch( 'CanvasHacks.SkaaSteps.ISkaaSteps.StudentRepository' )
    @patch( 'CanvasHacks.SkaaSteps.SendInitialWorkToReviewer.WorkRepositoryLoaderFactory' )
    def test_does_not_send_to_people_already_assigned( self, workLoaderMock, studentRepoMock, messengerMock,
                                                       statusRepoMock ):
        """
        Simulates a run where some students have already been assigned
        peer reviewers and a new group is being processed.

        Focus in testing is on making sure that the two groups don't get mixed up

        :param workLoaderMock:
        :param studentRepoMock:
        :param messengerMock:
        :return:
        """
        self.workRepo.submitter_ids = self.new_students_ids

        workLoaderMock.make = MagicMock( return_value=self.workRepo )

        # prepare student repo
        students = { s.student_id: s for s in self.students }

        def se( sid ):
            return students.get( sid )

        # studentRepoMock.get_student = MagicMock(side_effect=se)
        # studentRepoMock.download = MagicMock( return_value=self.students )

        # call
        obj = SendInitialWorkToReviewer( course=self.course, unit=self.unit, is_test=True, send=True )
        # obj.studentRepo = MagicMock()
        obj.studentRepo.get_student = MagicMock( side_effect=se )
        obj.studentRepo.download = MagicMock( return_value=self.students )
        preexisting_pairings = self.create_preexisting_review_pairings( self.activity_id, self.preexisting_students,
                                                                        obj.dao.session )

        obj.run()

        # check
        self.assertEqual( len( obj.associations ), len( self.new_students_ids ),
                          "Correct number of students assigned" )

        # Check that new assignments don't involve previously assigned sudents
        for rec in obj.associations:
            self.assertNotIn( rec.assessor_id, self.preexisting_student_ids,
                              "Newly assigned assessor not among previously assigned students" )
            self.assertNotIn( rec.assessee_id, self.preexisting_student_ids,
                              "Newly assigned assessee not among previously assigned students" )

        # Check whether each new student has been assigned
        new_assessor_ids = [ r.assessor_id for r in obj.associations ]
        new_assessee_ids = [ r.assessee_id for r in obj.associations ]
        self.assertEqual( len( set( new_assessor_ids ) ), len( self.new_students_ids ),
                          "No duplicate assessor assignments" )
        self.assertEqual( len( set( new_assessee_ids ) ), len( self.new_students_ids ),
                          "No duplicate assessee assignments" )
        for sid in self.new_students_ids:
            self.assertIn( sid, new_assessee_ids, "Student is an assessee" )
            self.assertIn( sid, new_assessor_ids, "Student is an assessor" )

        # ================== Events on Messenger
        # Check that mocked objects were called with expected data
        messengerMock.assert_called()
        self.assertEqual( messengerMock.call_count, len( self.new_students_ids ),
                          "Send method called expected number of times" )
        messenger_args = [ (c[ 1 ][ 'student_id' ], c[ 1 ][ 'subject' ], c[ 1 ][ 'body' ]) for c in
                           messengerMock.call_args_list ]
        # print(args)

        # Check that all messages have the correct subject
        for sid, subj, body in messenger_args:
            self.assertEqual(self.unit.review.email_subject, subj, "Correct subject line")

        # Status repo calls on messenger (only 1 repo)
        obj.messenger.status_repositories[0].record.assert_called()
        call_list = obj.messenger.status_repositories[0].record.call_args_list

        # obj.messenger.status_repositories.record_invited.assert_called()
        # call_list = obj.messenger.status_repositories.record_invited.call_args_list
        status_args = [ c[ 0 ][ 0 ] for c in call_list ]
        self.assertEqual( len( self.new_students ), len( call_list ),
                          "Status repo record_invited called expected number of times" )
        for sid in self.new_students_ids:
            self.assertIn( sid, status_args, "StatusRepo.record_invited called on all students" )

        # student repo calls on messenger
        for sid in self.new_students_ids:
            obj.messenger.student_repository.get_student.assert_any_call( sid )

        # Check the content sent
        for record in obj.associations:
            # print(record.assessee_id)
            author_text = self.workRepo.get_formatted_work_by( record.assessee_id )
            # see if sent to assessor
            sent_text = [ t[ 2 ] for t in messenger_args if t[ 0 ] == record.assessor_id ][ 0 ]
            rx = r'{}'.format( author_text )
            self.assertRegex( sent_text, rx, "Author's work in message sent to reviewer" )

    @patch( 'CanvasHacks.SkaaSteps.ISkaaSteps.StudentRepository' )
    @patch( 'CanvasHacks.SkaaSteps.SendInitialWorkToReviewer.WorkRepositoryLoaderFactory' )
    def test_raises_when_all_submitters_already_assigned( self, workLoaderMock, studentRepoMock ):
        # Prepare fake work repo to give values to calling  objects
        # workRepo = ContentRepositoryMock()
        # workRepo.create_test_content( self.preexisting_student_ids )
        # workRepo.add_students_to_data(self.student_ids, make_dataframe=True)

        # Setting to return all the previously assigned students.
        # this should cause all the students to be filtered out
        # and the errror raised
        self.workRepo.submitter_ids = self.preexisting_student_ids
        workLoaderMock.make = MagicMock( return_value=self.workRepo )

        studentRepoMock.download = MagicMock( return_value=self.students )

        # call
        obj = SendInitialWorkToReviewer( course=self.course, unit=self.unit, is_test=True, send=True )
        self.session = obj.dao.session
        preexisting_pairings = self.create_preexisting_review_pairings( self.activity_id, self.preexisting_students )

        with self.assertRaises( AllAssigned ):
            obj.run()

    @patch( 'CanvasHacks.SkaaSteps.ISkaaSteps.StudentRepository' )
    @patch( 'CanvasHacks.SkaaSteps.SendInitialWorkToReviewer.WorkRepositoryLoaderFactory' )
    def test_raises_when_only_one_submission( self, workLoaderMock, studentRepoMock ):

        # Prepare fake work repo to give values to calling  objects
        workRepo = ContentRepositoryMock()
        workRepo.create_test_content( self.new_students_ids )
        workRepo.add_students_to_data(self.student_ids, make_dataframe=True)

        # Setting to return all the previously assigned students.
        # this should cause all the students to be filtered out
        # and the errror raised
        self.workRepo.submitter_ids = [ self.new_students[ 0 ] ]
        workLoaderMock.make = MagicMock( return_value=self.workRepo )

        studentRepoMock.download = MagicMock( return_value=self.students )

        # call
        obj = SendInitialWorkToReviewer( course=self.course, unit=self.unit, is_test=True, send=True )
        # Have to do this after object creation so that we can use the
        # same in-memory db
        self.session = obj.dao.session
        preexisting_pairings = self.create_preexisting_review_pairings( self.activity_id, self.preexisting_students )

        with self.assertRaises( NoAvailablePartner ):
            obj.run()
