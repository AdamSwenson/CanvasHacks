"""
Created by adam on 1/18/20
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from CanvasHacks.DAOs.dao_parent import DAO
from CanvasHacks.DAOs.db_files import DBFilePathHandler

QueueBase = declarative_base()

__author__ = 'adam'

class QueueSqliteDAO( DAO ):
    """
    Makes a connection to sqlite database holding the message queue.

    This will check environment to determine if it is a test and
    if so, create an in-memory SQLite database (unless CanvasHacks.testglobals.TEST_WITH_FILE_DB
    is set to true).

    Otherwise, it will use environmental variables create and
    connect to the queue database for the semester.
    """

    def __init__( self, db_filepath=None ):
        """
        :param db_filepath: Optional path to the database file (mainly for testing)
        :type db_filepath: str
        """
        super().__init__( db_filepath)

    def _set_db_filepath(self, db_filepath=None):
        try:
            if db_filepath is not None:
                self.db_filepath = db_filepath
            else:
                self.db_filepath = DBFilePathHandler.message_queue()

        except AttributeError as e:
            # This is likely to happen during testing
            print(e)

    def _initialize_db_file( self ):
        """
        Creates tables in the database
        :return:
        """
        QueueBase.metadata.create_all( self.engine )


    # def _create_file_engine( self, filepath ):
    #     connection_string = 'sqlite:///{}'.format( filepath )
    #     print( "creating connection: %s " % connection_string )
    #     self.engine = create_engine( connection_string, echo=False )

    # def _create_memory_engine( self ):
    #     """
    #     Creates an in-memory sqlite db engine
    #     """
    #     connection_string = 'sqlite:///:memory:'
    #     print( "creating connection: %s " % connection_string )
    #     self.engine = create_engine( connection_string, echo=False )
    #
    #     QueueBase.metadata.create_all( self.engine )
    #     # print( "creating connection: %s " % conn )
    #     # self.engine = create_engine( conn, echo=False )









if __name__ == '__main__':
    pass