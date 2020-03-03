"""
Created by adam on 3/2/20
"""
__author__ = 'adam'

from unittest import TestCase

from factories.PeerReviewedFactories import unit_factory
from tests.TestingBase import TestingBase

if __name__ == '__main__':
    pass


class TestDiscussionRepository( TestingBase ):
    def setUp(self):
        self.config_for_test()
        self.unit = unit_factory()
        self.activity = self.unit.discussion_forum

    def test_course_id( self ):
        self.fail()

    def test_download( self ):
        self.fail()

    def test__get_submissions( self ):
        self.fail()

    def test__parse_posts_from_submissions( self ):
        self.fail()

    def test_get_student_posts( self ):
        self.fail()

    def test_get_formatted_work( self ):
        self.fail()

    def test_upload_student_grade( self ):
        self.fail()

    def test_display_for_grading( self ):
        self.fail()

    def test_post_counts( self ):
        self.fail()
