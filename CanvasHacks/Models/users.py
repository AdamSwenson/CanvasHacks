"""
Created by adam on 1/21/20
"""

from canvasapi import Canvas
from canvasapi.quiz import QuizReport, Quiz
from canvasapi.requester import Requester
from canvasapi.conversation import Conversation

from CanvasHacks.Models.model import Model

__author__ = 'adam'
import CanvasHacks.environment as env


class StudentUser(Model):

    def __init__(self, token, course_id, **kwargs):
        self.course_id = course_id
        self.token = token
        self.topic_id = None
        self.assignment_id = None
        self.quiz_id = None
        self.discussion_entries = []
        super().__init__(**kwargs)

        self._initialize()

    def _initialize( self ):
        canvas = Canvas(env.CONFIG.canvas_url_base, self.token)
        self.course = canvas.get_course(self.course_id)
        if self.topic_id:
            self.get_discussion(self.topic_id)
        if self.assignment_id:
            self.get_assignment(self.assignment_id)

    def get_discussion( self, topic_id ):
        self.discussion = self.course.get_discussion_topic(topic_id)

    def get_assignment( self, assignment_id ):
        self.assignment = self.course.get_assignment(assignment_id)

    def get_entries( self ):
        """Refresh he list of all entries for he discussion"""
        self.can_entries = self.discussion.get_entries()

    def post_entry( self, message_text ):
        entry = self.discussion.post_entry(message=message_text)
        self.discussion_entries.append(entry)
        # self.discussion_entries[entry.id] = entry
        return entry



if __name__ == '__main__':
    pass