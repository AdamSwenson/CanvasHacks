"""
Created by adam on 3/2/20
"""
__author__ = 'adam'

from faker import Faker

fake = Faker()
from unittest.mock import MagicMock

from CanvasHacks.Repositories.discussions import DiscussionRepository
from factories.PeerReviewedFactories import unit_factory
from tests.TestingBase import TestingBase

if __name__ == '__main__':
    pass


def discussion_repo_data_factory( students, per_student=1 ):
    out = [ ]
    for _ in range( 0, per_student ):
        for student in students:
            out.append(
                { 'student_id': student.student_id,
                  'student_name': student.name,
                  'text': fake.text()
                  } )
    return out


class TestDiscussionRepository( TestingBase ):
    def setUp( self ):
        self.config_for_test()
        self.unit = unit_factory()
        self.course = MagicMock()
        self.create_new_and_preexisting_students()

        self.activity = self.unit.discussion_forum
        self.obj = DiscussionRepository( activity=self.activity, course=self.course )

    def test_course_id( self ):
        self.skipTest( 'todo' )

    def test_download( self ):
        self.skipTest( 'todo' )

    def test__get_submissions( self ):
        self.skipTest( 'todo' )

    def test__parse_posts_from_submissions( self ):
        self.skipTest( 'todo' )

    def test_get_student_posts( self ):
        self.skipTest( 'todo' )

    def test_get_formatted_work( self ):
        self.skipTest( 'todo' )

    def test_upload_student_grade( self ):
        self.skipTest( 'todo' )

    def test_display_for_grading( self ):
        self.skipTest( 'todo' )

    def test_post_counts( self ):
        self.skipTest( 'todo' )

    def test_filter_by_count( self ):
        min_posts = fake.random.randint(2, 10)
        half_idx = round(len(self.new_students)/2)
        equal_to = discussion_repo_data_factory(self.new_students[half_idx :], min_posts)
        gtr = discussion_repo_data_factory(self.new_students[ : half_idx + 1 ], min_posts)

        to_remain = equal_to + gtr
        to_remove = discussion_repo_data_factory(self.preexisting_students, min_posts -1)

        self.obj.data = to_remove + to_remain

        # call
        result = self.obj.filter_by_count(min_posts)

        # check
        self.assertEqual(len(result), len(to_remain), "expected length returned")

        for s in to_remain:
            self.assertIn(s, result, "expected entries in returned")

        for s in to_remove:
            self.assertNotIn(s, result, "removed entries not in returned")
