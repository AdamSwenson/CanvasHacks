
from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.sqlite import DATETIME
from sqlalchemy.dialects.sqlite import JSON

# from sqlalchemy.ext.declarative import declarative_base

from CanvasHacks import environment as env
from CanvasHacks.Models.model import Model

from CanvasHacks.DAOs.sqlite_dao import Base

class MessageQueueItem(Base, Model):
    """
    A message that needs to be sent to a student
    """
    __tablename__ = env.MESSAGE_QUEUE_TABLE_NAME
    id = Column(Integer, primary_key=True)
    """Id of the queue item"""

    activity_id = Column(Integer)
    """Id of the activity this message is related to"""

    student_id = Column(Integer)
    """The canvas id of the student who will receive the message"""

    subject = Column(String)
    """The subject line of the message that needs sending"""

    body = Column(String)
    """The body of the message to send"""

    status_repos = Column(JSON, nullable=True)
    """The type and activity id of each status repository to call when message is sent"""

    created_at = Column(DATETIME, nullable=True)
    """Timestamp of when the item was queued"""


    def __repr__( self ):
        return f"<Message to send(id={self.id}, activity_id={self.activity_id}, student_id={self.student_id}, created_at={self.created_at}, subject={self.subject}, body={self.body}"



if __name__ == '__main__':
    pass
