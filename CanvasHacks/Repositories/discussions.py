"""
Created by adam on 1/27/20
"""
from CanvasHacks.Repositories.IRepositories import IRepo

__author__ = 'adam'


class DiscussionRepository(IRepo):

    def __init__(self, course):
        self.course = course
        self.data = []

    def download(self, topic_id):
        self._get_discussion_entries(topic_id)
        self._get_info_for_grading(topic_id)

    def _get_discussion_entries(self, topic_id):
        """Loads and returns a list of discussion objects.
            Objects look something like:
            {'id': 2132485, 'user_id': 169155,
            'parent_id': None, 'created_at': '2020-01-16T23:01:53Z',
            'updated_at': '2020-01-16T23:01:53Z', 'rating_count': None,
            'rating_sum': None, 'user_name': 'Test Student',
            'message': '<p>got em</p>', 'user': {'id': 169155,
            'display_name': 'Test Student',
            'avatar_image_url': 'https://canvas.csun.edu/images/messages/avatar-50.png',
            'html_url': 'https://canvas.csun.edu/courses/85210/users/169155',
            'pronouns': None, 'fake_student': True},
            'read_state': 'unread', 'forced_read_state': False,
            'discussion_id': 737847, 'course_id': 85210}
        """
        discussion = self.course.get_discussion_topic(topic_id)
        # result is lazy loaded, so iterate through it
        self.data = [e for e in discussion.get_topic_entries()]
        return self.data

    def _get_info_for_grading( self, topic_id ):
        """Retrieves all the information we'll need for grading"""
        topic = self.course.get_discussion_topic(topic_id)
        # Graded discussions will be tied to an assignment, so
        # we need the id
        self.assignment_id = topic.assignment_id
        print("Assignment {} is associated with topic {}".format(self.assignment_id, topic_id))
        # Load the assignment object
        self.assignment = self.course.get_assignment(self.assignment_id)
        # Load all submissions for the assignment
        self.submissions = {s.user_id : s for s in self.assignment.get_submissions()}
        print("Loaded {} submissions for the assignment".format(len(self.submissions.keys())))

    def upload_student_grade( self, student_id, pct_credit):
        pct = "{}%".format(pct_credit) if isinstance(pct_credit, int) or pct_credit[-1:] != '%' else pct_credit
        # Look up the student submission
        submission = self.submissions.get(student_id)
        return submission.edit(posted_grade=pct)


if __name__ == '__main__':
    pass