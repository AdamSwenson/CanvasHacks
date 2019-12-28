"""
Created by adam on 12/26/19
"""
from unittest import TestCase

from faker import Faker

fake = Faker()

from CanvasHacks.PeerReviewed.Notifications import *

__author__ = 'adam'

if __name__ == '__main__':
    pass


def prompt_response_factory( number=3 ):
    return [ { 'prompt': fake.sentence(), 'response': fake.paragraph() } for _ in range( 0, number ) ]


class TestMake_conversation_data( TestCase ):
    def test_make_conversation_data( self ):
        self.fail()


class TestStudentNotices( TestCase ):

    def test_make_prompt_and_response( self ):
        w = prompt_response_factory()
        j = make_prompt_and_response( w )

        self.assertTrue( len( j ) > 1, "Created string is non empty" )

    def test_make_notice( self ):
        w = prompt_response_factory()
        d = { 'name': fake.name(),
              'response_list': w,
              'review_assignment_name': fake.job(),
              'access_code': fake.slug()
              }
        j = make_notice(d)
        # self.assertEquals(  j, 1, "Created string is non empty" )
        self.assertTrue( len( j ) > 1, "Created string is non empty" )
