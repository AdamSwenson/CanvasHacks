import datetime

from CanvasHacks.DAOs.db_files import DBFilePathHandler
from CanvasHacks.DAOs.mixins import DaoMixin, MessageDaoMixin
from CanvasHacks.DAOs.sqlite_message_dao import QueueSqliteDAO
from CanvasHacks.Models.message_queue import MessageQueueItem
from sqlalchemy import delete
from CanvasHacks.Definitions.activity import Activity


class MessageQueueRepository(MessageDaoMixin):
    """
    Handles interaction with the messaging queue.
    Always creates its own instance of QueueSqliteDAO.
    Only operates on the message queue database. Does not
    interact with the main database.
    """

    def __init__(self, **kwargs):
        """

        """
        # if dao is not None:
        #     self.dao = dao
        # else:
        self._initialize_db()

        self.session = self.dao.session


    def add_to_queue(self, activity, unit_number, student_id, subject, body, status_repos=[]):
        """Pushes a message onto the sending queue
        :param unit_number: The number of the unit. This will be used in rehydrating status repos
        :param status_repos: List containing status repo objects which should be called once the message is sent
        :param activity: The assignment this message is related to
        :type activity: Activity
        :param student_id: The canvas id of the student who should receive the message
        :type student_id: int
        :param subject: Subject line of message
        :type subject: str
        :param body: Message body to send
        :type body: str

        """
        status_repos = self._make_status_repos_entry(status_repos)
        m = MessageQueueItem(activity_id=activity.id,
                             unit_number=unit_number,
                             student_id=student_id,
                             subject=subject,
                             body=body,
                             status_repos=status_repos,
                             created_at=datetime.datetime.now())
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

    @property
    def all_to_send(self):
        """A list of messages to send """
        return self.get_message_queue()

    @property
    def to_send_count(self):
        """Count of messages in the queue"""
        return len(self.get_message_queue())

    def get_message_queue(self, activity_id=None):
        """Returns an iterable of all messages on the queue"""
        if activity_id is None:
            return self.session.query(MessageQueueItem).all()

        return self.session.query(MessageQueueItem) \
            .filter(MessageQueueItem.activity_id == activity_id) \
            .all()

    def _make_status_repos_entry(self, status_repos: list):
        """
        Creates the information necessary for recreating the status repositories
        in the relevant field.
        NB, when these repos are rehydrated by another process, that process will need to
        pass them the main db SQLiteDAO.
        :return: list
        """
        entries = []
        for s in status_repos:
            if s.__class__.__name__ == 'InvitationStatusRepository':
                entries.append({'type' : s.__class__.__name__, 'activity_id': s.activity_id})

            elif s.__class__.__name__ == 'FeedbackStatusRepository':
                entries.append({'type': s.__class__.__name__,
                                'activity_id': s.activity_id,
                               'review_pairings_activity_id': s.review_pairings_activity_id})

        return entries
