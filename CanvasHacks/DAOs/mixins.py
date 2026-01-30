"""
Created by adam on 3/13/20
"""
__author__ = 'adam'
import CanvasHacks.environment as env
from CanvasHacks.DAOs.dao_access_point import DAOHolder
from CanvasHacks.DAOs.db_files import DBFilePathHandler
from CanvasHacks.DAOs.sqlite_message_dao import QueueSqliteDAO
from CanvasHacks.DAOs.sqlite_dao import SqliteDAO
import CanvasHacks.testglobals

if __name__ == '__main__':
    pass


class DaoMixin:
    """
    Provides database access initialization for the main database (relative
    to a unit and containing associations etc).

    Requires that self.unit_number be set if use _initialize_db
    """

    def _initialize_db( self ):
        try:
            self.unit_number = self.unit.unit_number
        except AttributeError:
            self.unit_number = self.activity.unit_number

        self.dao = DAOHolder.get_unit_dao( self.unit_number )
        # self.dao = SqliteDAO(self.unit_number)



        # try:
        #     t = 'TEST-' if env.CONFIG.is_test else ""
        #     self.db_filepath = DBFilePathHandler.essay_review(unit_number=unit_number)
        #     # make_essay_review_db_filepath(unit_number)
        #     # "{}/{}{}-Unit-{}-review-assigns.db".format( env.LOG_FOLDER, t, env.CONFIG.semester_name, unit_number )
        # except AttributeError as e:
        #     # This is likely to happen during testing
        #     print(e)
        #
        # if env.CONFIG.is_test:
        #     try:
        #         if CanvasHacks.testglobals.TEST_WITH_FILE_DB:
        #             # testing: file db
        #             self._initialize_file_db()
        #             print( "Connected to TEST db file. {}".format( self.db_filepath ) )
        #         else:
        #             # testing: in memory db
        #             self._initialize_memory_db()
        #     except (NameError, AttributeError) as e:
        #         print(e)
        #         # The variable might not be defined under in any
        #         # number of circumstances. So default to the in-memory db
        #         self._initialize_memory_db()
        #
        # else:
        #     # real: file db
        #     self._initialize_file_db()
        #     print( "Connected to REAL db. {}".format( self.db_filepath ) )

    # def _initialize_file_db( self ):
    #     self.dao = SqliteDAO(self.unit_number)
    #
    #     # self.dao = SqliteDAO( self.db_filepath )
    #     self.dao.initialize_db_file()
    #
    # def _initialize_memory_db( self ):
    #     self.dao = SqliteDAO()
    #     print( "Connected to in-memory testing db" )


class MessageDaoMixin:
    """
    Provides database access initialization for the message queue database.
    There is only one such database for each semester
    """

    def _initialize_db(self):
        """Sets the appropriate filepath if applicable and initializes the database. """

        self.dao = DAOHolder.message_queue_dao

    #
    #     try:
    #         self.db_filepath = DBFilePathHandler.message_queue()
    #     except AttributeError as e:
    #         # This is likely to happen during testing
    #         print(e)
    #
    #     if env.CONFIG.is_test:
    #         try:
    #             if CanvasHacks.testglobals.TEST_WITH_FILE_DB:
    #                 # testing: file db
    #                 self._initialize_file_db()
    #                 print("Connected to TEST queue db file. {}".format(self.db_filepath))
    #             else:
    #                 # testing: in memory db
    #                 self._initialize_memory_db()
    #         except (NameError, AttributeError) as e:
    #             print(e)
    #             # The variable might not be defined under in any
    #             # number of circumstances. So default to the in-memory db
    #             self._initialize_memory_db()
    #
    #     else:
    #         # This is what gets called in production
    #         # real: file db
    #         self._initialize_file_db()
    #         print("Connected to queue db file. {}".format(self.db_filepath))
    #
    #
    # def _initialize_file_db(self):
    #     self.dao = QueueSqliteDAO(self.db_filepath)
    #     self.dao.initialize_db_file()
    #
    # def _initialize_memory_db(self):
    #     self.dao = QueueSqliteDAO()
    #     print("Connected to in-memory testing queue db")
