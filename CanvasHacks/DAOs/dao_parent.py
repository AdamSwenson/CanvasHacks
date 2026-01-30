"""
Created by adam on 1/18/20
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import CanvasHacks.environment as env
import CanvasHacks.testglobals


__author__ = 'adam'


class DAO( object ):
    """
    Parent of dao objects which connect to sqlite databases.

    The methods need to be populated by the child classes because they
    require different instances of declarative_base base.

    On initialization, connects to the relevant database and creates tables, if needed.

    """

    def __init__( self, db_filepath=None):

        if self._use_file_db():
            self._set_db_filepath(db_filepath)
            self._create_file_engine()
        else:
            self._create_memory_engine()

        # Now that we have the engine, actually create the connection
        self._connect()
        # Populate the database tables if necessary
        self._initialize_db_file()

    def _use_file_db(self):
        """
        Returns true if we are going to create a file-based db.
        Returns false if we are going to create a memory db
        :return:
        """
        if env.CONFIG.is_test:
            try:
                if CanvasHacks.testglobals.TEST_WITH_FILE_DB:
                    return True
                else:
                    return False
            except (NameError, AttributeError) as e:
                print(e)
                # The variable might not be defined under in any
                # number of circumstances. So default to the in-memory db
                return False
        return True

    @property
    def session(self):
        return self.session_factory()


    def _connect( self ):
        """
        Creates a session on self.session
        :return:
        """
        self.session_factory = sessionmaker( bind=self.engine )
        # self.session = self.session_factory()


    def _create_file_engine( self ):
        """Connects to the database at the filepath set in db_filepath and creates
        an engine"""
        connection_string = 'sqlite:///{}'.format( self.db_filepath )
        print( "creating connection: %s " % connection_string )
        self.engine = create_engine( connection_string, echo=False )

    def _create_memory_engine( self ):
        """
        Creates an in-memory sqlite db engine
        """
        connection_string = 'sqlite:///:memory:'
        print( "creating connection: %s " % connection_string )
        self.engine = create_engine( connection_string, echo=False )


    def _initialize_db_file( self ):
        """
        Creates tables in the database
        :return:
        """
        pass


    def _set_db_filepath(self, db_filepath=None):
        """Determines what filepath to use for the database.
        If passed a path, sets that one.
        If not passed a path, calls the relevant method on DBFilePathHandler
        :type db_filepath: str
        :param db_filepath: The optional filepath to use. If set, this path will be used.
        """
        pass

if __name__ == '__main__':
    pass
