from CanvasHacks import environment
from CanvasHacks.DAOs.db_files import DBFilePathHandler

from CanvasHacks.DAOs.mixins import DaoMixin
from CanvasHacks.Messaging.SendTools import ExchangeMessageSender, DummyEmailSender
from CanvasHacks.Models.message_queue import MessageQueueItem
from CanvasHacks.Repositories.messaging import MessageRepository
from CanvasHacks.Repositories.status import StatusRepository, InvitationStatusRepository, FeedbackStatusRepository
from CanvasHacks.Repositories.students import StudentRepository


class QueuedMessageSender(object):
    """
    Job class which handles sending messages that are stored in the queue and
    updating the queue.
    """

    def __init__( self, student_repository=None, message_repository=None, sender=None, dao=None, use_file_db=True ):
        """
        NB, since this is a job class which could be called to run independently it
        has a lot of options for whether it is passed repositories or whether it creates them
        :type student_repository: StudentRepository
        :param student_repository: Optionally accepts an existing repo object so won't have to download again
        :param dao: Optional sqlite dao to use instead of internally created instance
        :type dao: SqliteDAO
        :param use_file_db: Whether to use the file database. False tells MessageRepo to use in-memory for testing.
        """
        self.status_repositories = {}
        """Will have keys (activity_id, repo_name)"""

        if message_repository is None:
            message_repository = MessageRepository(dao=dao, use_file_db=use_file_db)
        self.message_repository = message_repository
        # Ensure using same dao as message repo to help with testing
        self.dao = message_repository.dao

        if student_repository is None:
            student_repository = StudentRepository(environment.CONFIG.course)
            student_repository.download()
        self.student_repository = student_repository

        if sender is None:
            sender =
            sender = ExchangeMessageSender(student_repository=self.student_repository)
        self.sender = sender

    @property
    def cnt(self):
        return self.message_repository.to_send_count

    def send_all( self, send=True):
        """Sends all messages that are on the queue
        :param send:Whether to actually send. If False, prints the message instead
        """
        if self.message_repository.to_send_count == 0:
            print("No queued messages to send")
            return False
        print("Sending {} messages".format(self.message_repository.to_send_count))

        try:
            for m in self.message_repository.all_to_send:
                if send:
                    self.sender.send(m.student_id, m.subject, m.body)
                    self.update_status(m)
                else:
                    print(f"{m}\n------\n")

                self.message_repository.remove_from_queue(m)

        except Exception as e:
            print(f"Failed to send message \n {m}\n{e}")

    def rehydrate_status_repos(self, message_queue_item):
        # dev This should really use a factory pattern to be more extensible
        for sr in message_queue_item.status_repos:
            # Not sure if there are cases where there would be 2 different repos
            # for the same activity, but just in case we check type too
            if (sr['activity_id'], sr['type']) not in self.status_repositories.keys():
                if sr['type'] == 'InvitationStatusRepository':
                    r = InvitationStatusRepository(self.dao, sr['activity_id'])
                    # self.status_repositories[(sr['activity_id'], sr['type'])] = InvitationStatusRepository(self.dao, sr['activity_id'])
                elif sr['type'] == 'FeedbackStatusRepository':
                    r = FeedbackStatusRepository(self.dao, sr['activity_id'], sr['review_pairings_activity_id'])

                self.status_repositories[(sr['activity_id'], sr['type'])] = r


    def update_status( self, message_queue_item: MessageQueueItem ):
        """
        Call the record method on all status repos
        :param message_queue_item: The item which has the status repos stored
        :param message_data:
        :return:
        """
        # Make sure the repos exist
        self.rehydrate_status_repos(message_queue_item)

        for sr in message_queue_item.status_repos:
            repo = self.status_repositories[(sr['activity_id'], sr['type'])]
            repo.record( message_queue_item.student_id )


if __name__ == '__main__':
    qm = QueuedMessageSender()
    qm.send_all()