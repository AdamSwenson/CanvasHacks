from CanvasHacks import environment
from CanvasHacks.DAOs.dao_access_point import DAOHolder
from CanvasHacks.DAOs.db_files import DBFilePathHandler

from CanvasHacks.DAOs.sqlite_dao import SqliteDAO
from CanvasHacks.DAOs.sqlite_message_dao import QueueSqliteDAO
from CanvasHacks.Messaging.SendTools import ExchangeMessageSender, DummyEmailSender
from CanvasHacks.Messaging.interfaces import ISender
from CanvasHacks.Models.message_queue import MessageQueueItem
from CanvasHacks.Repositories.messaging import MessageQueueRepository
from CanvasHacks.Repositories.status import StatusRepository, InvitationStatusRepository, FeedbackStatusRepository
from CanvasHacks.Repositories.students import StudentRepository


class QueuedMessageSender(object):
    """
    Job class which handles sending messages that are stored in the queue and
    updating the queue.
    """

    def __init__(self, student_repository=None, message_repository=None, sender: ISender = None, **kwargs):
        """
        NB, since this is a job class which could be called to run independently it
        has a lot of options for whether it is passed repositories or whether it creates them.
        However, message_repository will always be what holds the message queue dao (QueueSqliteDAO)
        dev Nope. Not after CAN-99

        :type student_repository: StudentRepository
        :param student_repository: Optionally accepts an existing repo object so won't have to download again
        """
        self.status_repositories = {}
        """Will have keys (activity_id, repo_name)"""

        if message_repository is None:
            # dev CAN-99 This will create the queue dao internally
            message_repository = MessageQueueRepository()#use_file_db=use_file_db)
        self.message_repository = message_repository

        # dev CAN-99 This cannot be the case. Changed to make the dao mandatory
        # Ensure using same dao as message repo to help with testing
        # self.dao = message_repository.dao
        # self.dao = SqliteDAO(unit_number)
        # """This is the dao that accesses the main db with invites etc for the current unit"""

        if student_repository is None:
            student_repository = StudentRepository(environment.CONFIG.course)
            student_repository.download()
        self.student_repository = student_repository

        if sender is None:
            sender = ExchangeMessageSender(student_repository=self.student_repository)
        self.sender = sender

        self.unit_daos = {}
        """This will hold sqliteDAO objects as they are created in rehydrating repositories"""

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
        """Instantiates the correct status repositories, with correct daos for the
        status repositories stored in the db"""
        dao = self.unit_daos.get(message_queue_item.unit_number, None)
        if dao is None:
            # Instantiate the required dao and store in unit_daos
            # It has to work this way because we could have messages
            # from different units stored on the queue
            dao = DAOHolder.get_unit_dao( message_queue_item.unit_number )
            # dao = SqliteDAO(message_queue_item.unit_number)
            # self.unit_daos[message_queue_item.unit_number] = dao

        # dev This should really use a factory pattern to be more extensible
        for sr in message_queue_item.status_repos:
            # Not sure if there are cases where there would be 2 different repos
            # for the same activity, but just in case we check type too
            if (sr['activity_id'], sr['type']) not in self.status_repositories.keys():
                if sr['type'] == 'InvitationStatusRepository':
                    print('invite status repo rehydrated')
                    print(dao)

                    # dev CAN-99
                    # These need to be the reqular dao

                    r = InvitationStatusRepository(dao, sr['activity_id'])
                    # self.status_repositories[(sr['activity_id'], sr['type'])] = InvitationStatusRepository(self.dao, sr['activity_id'])
                elif sr['type'] == 'FeedbackStatusRepository':
                    r = FeedbackStatusRepository(dao, sr['activity_id'], sr['review_pairings_activity_id'])
                    print('feedback status repo rehydrated')

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