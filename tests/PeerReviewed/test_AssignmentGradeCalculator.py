# """
# Created by adam on 12/20/19
# """
# from unittest import TestCase
#
# from faker import Faker
#
# fake = Faker()
#
# __author__ = 'adam'
#
# from CanvasHacks.PeerReviewed.PeerReviewTools import *
#
# from tests.factories.PeerReviewedFactories import *
# from tests.factories.ModelFactories import *
#
#
# class TestAssignmentGradeCalculator( TestCase ):
#     def setUp( self ):
#         # Create the unit
#         self.assignment = unit_factory()
#
#         self.student1 = student_factory()
#         self.student2 = student_factory()
#
#         self.submissions = submissions_factory( self.student1, self.student2, self.assignment )
#
#         self.obj = UnitGradeCalculator( self.assignment, self.submissions )
#
#     def test_get_submissions_for_all_subs( self ):
#         c = self.obj._get_submissions( InitialWork )
#         self.assertIsInstance( c[ 0 ], Submission )
#
#     def test_get_work_as_submitter( self ):
#         # check starting point
#         self.assertEqual( 6, len( self.obj.submissions ), "Starting with correct number" )
#
#         work = self.obj.get_work_as_submitter( self.student1 )
#         self.assertEqual( 3, len( work ), "Returns expected number of subs" )
#
#         for w in work:
#             self.assertIsInstance( w, Submission, "Returns expected type" )
#             # if isinstance(w, InitialWork):
#             self.assertEqual( w.submitter.student_id, self.student1.student_id,
#                               "Student is submitter of the work (including cases where another student reviewed it)" )
#
#     def test_get_work_as_reviewer( self ):
#         # check starting point
#         self.assertEqual( 6, len( self.obj.submissions ), "Starting with correct number" )
#
#         work = self.obj.get_work_as_reviewer( self.student1 )
#         self.assertEqual( 2, len( work ), "Returns expected number of subs" )
#
#         for w in work:
#             self.assertIsInstance( w, Submission, "Returns expected type" )
#             if isinstance( w, InitialWork ):
#                 self.fail( "Returned submitter when looking for reviewer" )
#             else:
#                 self.assertEqual( w.reviewer.student_id, self.student1.student_id, "Review by expected student" )
#
#     def test_get_student_work( self ):
#         # check starting point
#         self.assertEqual( 6, len( self.obj.submissions ), "Starting with correct number" )
#
#         work = self.obj.get_student_work( self.student1 )
#         self.assertEqual( 5, len( work ), "Returns expected number of subs" )
#         for w in work:
#             self.assertIsInstance( w, Submission, "Returns expected type" )
#             if isinstance( w, InitialWork ):
#                 self.assertEqual( w.submitter, self.student1.student_id )
#
#     def test_calculate( self ):
#         self.obj.calculate()
#
#         self.assertEqual( len( self.obj.scores ), 2, "Number of scores matches number of students" )
#
#         for s in self.obj.scores:
#             self.assertIsInstance( s, UnitScores )
#             self.assertGreater( s.total, 0, "Total score greater than 0" )
#
#
# class TestAssignmentGradeCalculatorAbarrentCases( TestCase ):
#     def setUp( self ):
#         # Create the unit
#         self.assignment = unit_factory()
#
#         self.student1 = student_factory()
#         self.student2 = student_factory()
#
#         self.submissions = submissions_factory( self.student1, self.student2, self.assignment )
#
#         self.obj = UnitGradeCalculator( self.assignment, self.submissions )
#
#     def test_reviewer_flakes( self ):
#         """The student should receive full credit for the
#         unit if the reviewer doesn't do their part
#         """
#         pass
#
#     def test_missing_metareview( self ):
#         """The reviewer should receive full credit
#         if the original submitter does not complete the
#         metareview
#         """
#         pass
