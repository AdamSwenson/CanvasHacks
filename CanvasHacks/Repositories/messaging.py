from CanvasHacks.DAOs.sqlite_dao import SqliteDAO
from CanvasHacks.Models.message_queue import MessageQueueItem
from sqlalchemy import delete
from CanvasHacks.Definitions.activity import Activity


class MessageRepository(object):
    """
    Handles interaction with the messaging queue
    """

    def __init__(self, dao: SqliteDAO):
        self.session = dao.session
        self.message_queue_address = ''

    def add_to_queue(self, activity, student_id, subject, body):
        """Pushes a message onto the sending queue
        :param activity: The assignment this message is related to
        :type activity: Activity
        :param student_id: The canvas id of the student who should receive the message
        :type student_id: int
        :param subject: Subject line of message
        :type subject: str
        :param body: Message body to send
        :type body: str
        """

        m = MessageQueueItem(activity_id=activity.id, student_id=student_id, subject=subject, body=body)
        self.session.add(m)
        self.session.commit()

    def remove_from_queue(self, message_item):
        """
        Removes a sent message from the queue
        :param message_item: The message item object to remove
        :return:
        """
        self.session.delete(message_item)
        self.session.commit()

    # def message_iterator(self, activity):
    #     """generator which returns a message iterator"""
    #     messages = self._load_message_queue(activity_id=activity.id)
    #     for m in messages:
    #         yield m

    def get_message_queue(self, activity_id=None):
        if activity_id is None:
            return self.session.query(MessageQueueItem).all()

        return self.session.query(MessageQueueItem) \
            .filter(MessageQueueItem.activity_id == activity_id) \
            .all()
