"""
These actually populate assignments in the
canvas sandbox with test data

Created by adam on 1/22/20
"""
__author__ = 'adam'

if __name__ == '__main__':
    pass

from CanvasHacks.Models.users import StudentUser
from faker import Faker

fake = Faker()


def populate_discussion( tokens: list, topic_id: int, deep: int, course_id: int ):
    """Uploads test data to a discussion forum
    :param topic_id: The identifier of the canvas discussion to populate
    :param deep: The number of mutual replies to each post
    :param course_id: The canvas id of the course
    :param tokens: List of student access token strings
    """
    posts = [ ]
    student_users = [ ]
    for t in tokens:
        student_users.append( StudentUser( t, course_id, topic_id=topic_id ) )

    for su in student_users:
        msg = fake.paragraph()
        e = su.post_entry( msg )
        posts.append( e )
    for i in range( 0, deep ):
        for s1 in student_users:
            for entry in s1.discussion_entries:
                # every other student comments on each entry
                for s2 in student_users:
                    msg = fake.paragraph()
                    e = s2.discussion.get_entries( [ entry.id ] )
                    r = e[ 0 ].post_reply( message=msg )
                    posts.append( r )


def populate_assignment( tokens: list, assignment_id: int, course_id:int ):
    """Uploads a paragraph of response text for each token provided
    in tokens.
    :param assignment_id: The identifier of the canvas assignment to populate
    :param course_id: The canvas id of the course
    :param tokens: List of student access token strings
    :returns List of Submission objects returned from server
    """
    submissions = [ ]

    for t in tokens:
        msg = fake.paragraph()
        sub = {
            'submission_type': 'online_text_entry',
            'body': msg,
        }
        s1 = StudentUser( t, course_id, assignment_id=assignment_id )
        result = s1.assignment.submit( sub )
        submissions.append( result )
    return submissions
