"""
Created by adam on 1/27/20
"""
from CanvasHacks.Processors.cleaners import TextCleaner
from CanvasHacks.Repositories.interfaces import IContentRepository
from CanvasHacks.Repositories.mixins import StudentWorkMixin
from CanvasHacks.Api.UploadGradeTools import upload_credit

__author__ = 'adam'

from CanvasHacks.Text.stats import WordCount


class DiscussionRepository( IContentRepository, StudentWorkMixin ):
    """Manages the data for one discussion unit"""

    def __init__( self, activity, course ):
        self.activity = activity
        self.topic_id = activity.topic_id
        self.course = course

        # List of dictionaries from parsed data:
        # [{'student_id', 'student_name', 'text'}]
        self.data = [ ]

        # The cleaner class that will be called to
        # remove html and other messy stuff from student
        # work
        self.text_cleaner = TextCleaner()

        self.analyzer = WordCount()


    @property
    def course_id( self ):
        return self.course.id

    def download( self ):
        # self._get_discussion_entries(topic_id)
        self._get_submissions( self.topic_id )
        self._parse_posts_from_submissions()
        print( "Loaded {} posts".format( len( self.data ) ) )

    def _get_submissions( self, topic_id ):
        """Retrieves all the information we'll need for grading
        Not using self.topic_id to allow method to be called
        independently for testing
        """
        topic = self.course.get_discussion_topic( topic_id )
        # Graded discussions will be tied to an unit, so
        # we need the id
        self.assignment_id = topic.assignment_id
        print( "Assignment {} is associated with topic {}".format( self.assignment_id, topic_id ) )
        # Load the unit object
        self.assignment = self.course.get_assignment( self.assignment_id )
        # Load all submissions for the unit
        self.submissions = { s.user_id: s for s in self.assignment.get_submissions() }
        print( "Loaded {} submissions for the unit".format( len( self.submissions.keys() ) ) )

    def _parse_posts_from_submissions( self ):
        """The submission objects downloaded for the unit will
        have the post information stored in a list called dicussion_entries.
        This takes all of those and loads the user id, name and text into
        posts"""
        for sid, submission in self.submissions.items():
            for entry in submission.discussion_entries:
                # Remove html and other artifacts from student answers
                # DO NOT UNCOMMENT UNTIL CAN-59 HAS BEEN FULLY TESTED
                content = self.text_cleaner.clean(entry[ 'message' ])

                self.data.append( { 'student_id': entry[ 'user_id' ],
                                    'student_name': entry[ 'user_name' ],
                                    'text': content
                                    } )
            #
            # self.posts.append( (entry.user_id, entry.user_name, entry.message) )

    def get_student_posts( self, student_id ):
        """Returns a list of all posts by student for the topic"""
        return [ p[ 'text' ] for p in self.data if p[ 'student_id' ] == student_id ]

        # return [ p.message for p in self.data if p.user_id == student_id ]

    def get_formatted_work_by( self, student_id ):
        """Returns all posts by the student, formatted for
        sending out for review or display"""
        posts = self.get_student_posts( student_id )
        # self._check_empty(posts)
        posts = "\n        -------        \n".join( posts )
        return posts

    def upload_student_grade( self, student_id, pct_credit ):
        upload_credit( self.course_id, self.assignment_id, student_id, pct_credit )
        # Not sure why this doesn't work, but doing it manually does
        # pct = "{}%".format(pct_credit) if isinstance(pct_credit, int) or pct_credit[-1:] != '%' else pct_credit
        # Look up the student submission
        # submission = self.submissions.get( student_id )
        # return submission.edit(posted_grade=pct)

    def display_for_grading( self ):
        """Returns student submissions in format expected for
        ipython display
        "Returns a list of dictionaries of all dicussion posts for the topic
        Format:
        """
        return self.data
        # [ e for e in self.data ]

    @property
    def submitter_ids( self ):
        """Returns a list of canvas ids of students who have submitted the unit"""
        # try:
        return list( set( [ s[ 'student_id' ] for s in self.data ] ) )

    # return [ (e.user_id, e.user_name, e.message) for e in self.data ]

    # @property
    # def student_ids( self ):
    #     uids = list( set( [ k['student_id'] for k in self.data ] ) )
    #     uids.sort()
    #     return uids

    @property
    def post_counts( self ):
        """Returns list of tuples
        ( student id, # of posts )
        """
        counts = [ ]
        for sid in self.student_ids:
            counts.append( (sid, len( [ s for s in self.data if s[ 'student_id' ] == sid ] )) )
        return counts

    def filter_by_count( self, min_post_count ):
        """
        Returns a copy of data without students who have not reached
        the minimum count
        :param min_post_count:
        :return:
        """
        students_to_keep = [ sid for sid, cnt in self.post_counts if cnt >= min_post_count ]
        return [ s for s in filter( lambda x: x[ 'student_id' ] in students_to_keep, self.data ) ]

    # def _get_discussion_entries(self, topic_id):
    #     """
    #     THIS WON'T WORK BECAUSE ONLY RETURNS TOP LEVEL ENTRIES
    #     Loads and returns a list of discussion objects.
    #         Objects look something like:
    #         {'id': 2132485, 'user_id': 169155,
    #         'parent_id': None, 'created_at': '2020-01-16T23:01:53Z',
    #         'updated_at': '2020-01-16T23:01:53Z', 'rating_count': None,
    #         'rating_sum': None, 'user_name': 'Test Student',
    #         'message': '<p>got em</p>', 'user': {'id': 169155,
    #         'display_name': 'Test Student',
    #         'avatar_image_url': 'https://canvas.csun.edu/images/messages/avatar-50.png',
    #         'html_url': 'https://canvas.csun.edu/courses/85210/users/169155',
    #         'pronouns': None, 'fake_student': True},
    #         'read_state': 'unread', 'forced_read_state': False,
    #         'discussion_id': 737847, 'course_id': 85210}
    #     """
    #     discussion = self.course.get_discussion_topic(topic_id)
    #     # result is lazy loaded, so iterate through it
    #     # self.data = [e for e in discussion.get_entries()]
    #     self.data = [e for e in discussion.get_topic_entries()]
    #     return self.data


if __name__ == '__main__':
    pass
