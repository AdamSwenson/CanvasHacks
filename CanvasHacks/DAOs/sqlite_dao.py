"""
Created by adam on 1/18/20
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from CanvasHacks.DAOs.dao_parent import DAO
from CanvasHacks.DAOs.db_files import DBFilePathHandler

Base = declarative_base()

__author__ = 'adam'

if __name__ == '__main__':
    pass


class SqliteDAO(DAO):
    """
    Makes a connection to sqlite database.

    This will check environment to determine if it is a test and
    if so, create an in-memory SQLite database (unless CanvasHacks.testglobals.TEST_WITH_FILE_DB
    is set to true).

    Otherwise, it will use environmental variables and the provided unit number to create and
    connect to the main database for the unit.

    """

    def __init__(self, unit_number, db_filepath=None):
        """
        :param unit_number: The unit number to create the database access for
        :param db_filepath: Optional path to the database file (mainly for testing)
        :type db_filepath: str
        :type unit_number: int
        """
        self.unit_number = unit_number

        super().__init__(db_filepath)

    def _set_db_filepath(self, db_filepath=None):
        try:
            if db_filepath is not None:
                self.db_filepath = db_filepath
            else:
                self.db_filepath = DBFilePathHandler.essay_review(unit_number=self.unit_number)

        except AttributeError as e:
            # This is likely to happen during testing
            print(e)

    def _initialize_db_file(self):
        """
        Creates tables in the database
        :return:
        """
        Base.metadata.create_all(self.engine)

    # def _initialize_db( self, db_filepath=None ):
    #     """Decides on the appropriate filepath if needed and then
    #     calls the relevant method to initialize the database
    #     """
    #
    #     if env.CONFIG.is_test:
    #         try:
    #             if CanvasHacks.testglobals.TEST_WITH_FILE_DB:
    #                 # testing: file db
    #                 self.initialize_db_file()
    #                 print("Connected to TEST db file. {}".format(self.db_filepath))
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
    #         # real: file db
    #         self._initialize_file_db()
    #         print("Connected to REAL db. {}".format(self.db_filepath))

    # print( "creating connection: %s " % conn )
    # self.engine = create_engine( conn, echo=False )
