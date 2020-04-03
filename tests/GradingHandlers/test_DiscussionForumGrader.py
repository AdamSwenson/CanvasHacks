"""
Created by adam on 3/9/20
"""
__author__ = 'adam'
# first so will set globals
from CanvasHacks.Definitions.discussion import DiscussionForum
from TestingBase import TestingBase

from unittest.mock import MagicMock, create_autospec

from CanvasHacks.GradingHandlers.discussion import DiscussionForumGrader
from CanvasHacks.Repositories.discussions import DiscussionRepository

# from CanvasHacks.Repositories.discussions import DiscussionRepository
from factories.ModelFactories import student_factory

if __name__ == '__main__':
    pass


class TestDiscussionForumGrader( TestingBase ):

    def make_student_post( self, student, is_blank=False ):

        return {
            'student_id': student.student_id,
            'student_name': student.name,
            'text': '' if is_blank else self.fake.paragraph()
        }

    def make_post_data( self ):
        if len( self.students ) == 0:
            self.create_new_and_preexisting_students()

        self.data = [ ]
        self.number_w_required_or_more = 0
        for s in self.students:
            posts = self.fake.random.randint( 0, 50 )
            for _ in range( 0, posts ):
                self.data.append( self.make_student_post( s ) )

            if posts >= self.number_required:
                self.number_w_required_or_more += 1

    def setUp( self ):
        self.config_for_test()
        self.create_new_and_preexisting_students()

        self.number_required = self.fake.random.randint( 2, 30 )
        self.expected_per_post = 100 / self.number_required
        self.make_post_data()
        # use real graders
        self.activity = DiscussionForum()
        # self.work_repo = MagicMock( data=self.data,  )
        # creates problems when runnning offline
        self.work_repo = create_autospec( DiscussionRepository, data=self.data, activity=self.activity )

        self.grade_func = MagicMock()

    def test_initialize( self ):

        obj = DiscussionForumGrader( self.work_repo, num_posts_required=self.number_required )

        # check
        self.assertEqual( obj.credit_per_post, self.expected_per_post, "Correct credit per post set" )

    def test__prepare_results( self ):
        self.skipTest('fuck you testing lib')
        num_required = 2
        obj = DiscussionForumGrader( self.work_repo, num_posts_required=num_required )

        # below required
        expected = [ (1, 50), (2, 0) ]
        obj._raw = [ (1, 50), (2, 0) ]
        obj._prepare_results()

        self.assertEqual( obj.graded, expected, "Posts under required are untouched" )

        # at required
        expected = [ (1, 100), (2, 100) ]
        obj._raw = [ (1, 50), (1, 50), (2, 50), (2, 50) ]
        obj._prepare_results()

        self.assertEqual( obj.graded, expected, "Posts equal to required are summed" )

        # over required
        expected = [ (1, 100), (2, 100) ]
        obj._raw = [ (1, 50), (1, 50), (1, 50), (2, 50), (2, 50), (2, 50) ]
        obj._prepare_results()

        self.assertEqual( obj.graded, expected, "Posts over required are reduced to 100" )

    def test__calc_scores_blank( self ):
        student = self.students[ 0 ]
        data = self.make_student_post( student, is_blank=True )

        work_repo = create_autospec( DiscussionRepository, data=[ data ], activity=self.activity  )
        obj = DiscussionForumGrader( work_repo, num_posts_required=self.number_required )

        # call
        obj._calc_scores()

        # check
        self.assertEqual( obj._raw[ 0 ], (student.student_id, 0), "Receives 0 when blank" )

    def test__calc_scores( self ):
        student = self.students[ 0 ]
        data = self.make_student_post( student )

        work_repo = create_autospec( DiscussionRepository, data=[ data ], activity=self.activity  )
        obj = DiscussionForumGrader( self.work_repo )

        # call
        obj._calc_scores()

        # check
        self.assertEqual( obj._raw[ 0 ], (student.student_id, obj.credit_per_post),
                          "Receives credit_per_post when not blank" )

    def test_grade_eq_to_expected( self ):
        # student who does exactly what's required
        student = student_factory()
        student_posts = [ self.make_student_post(student) for _ in range(0, self.number_required)]

        work_repo = create_autospec( DiscussionRepository, data=student_posts, activity=self.activity   )
        obj = DiscussionForumGrader( work_repo, num_posts_required=self.number_required )

        # call
        obj.grade()

        # check
        self.assertEqual(len(obj.graded), 1, "correct number of students in output")
        self.assertEqual((student.student_id, 100), obj.graded[0], "Correct result stored in obj.graded")

    def test_grade_greater_than_expected( self ):
        # student who does more than what's required
        student = student_factory()
        student_posts = [ self.make_student_post(student) for _ in range(0, self.number_required + 10)]

        work_repo = create_autospec( DiscussionRepository, data=student_posts, activity=self.activity  )
        obj = DiscussionForumGrader( work_repo, num_posts_required=self.number_required )

        # call
        obj.grade()

        # check
        self.assertEqual( len( obj.graded), 1, "correct number of students in output" )
        self.assertEqual((student.student_id, 100), obj.graded[0], "Correct result stored in obj.graded")

    def test_grade_less_than_expected( self ):
        # student who does less than required
        num_posts = self.number_required - 1

        student = student_factory()
        student_posts = [ self.make_student_post( student ) for _ in range( 0,  num_posts) ]

        work_repo = create_autospec( DiscussionRepository, data=student_posts, activity=self.activity  )
        obj = DiscussionForumGrader( work_repo, num_posts_required=self.number_required )

        # call
        obj.grade()

        # check
        self.assertEqual( len( obj.graded), 1, "correct number of students in output" )
        expected_score =round( num_posts * self.expected_per_post)
        self.assertAlmostEqual(expected_score, obj.graded[0][1], places=3, msg="Correct result stored in obj.graded")



