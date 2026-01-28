"""
Created by adam on 1/18/20
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


__author__ = 'adam'


class DAO( object ):
    """
    Parent of dao objects which connect to sqlite databases.

    The methods need to be populated by the child classes because they
    require different instances of declarative_base base.

    """

    def __init__( self, db_filepath=None ):
        if db_filepath:
            self._make_file_engine( db_filepath )
        else:
            self._create_memory_engine()

        self._connect()

    def _connect( self ):
        """
        Creates a session on self.session
        :return:
        """
        self.session_factory = sessionmaker( bind=self.engine )
        self.session = self.session_factory()

    def _create_memory_engine( self ):
        """
        Creates an in-memory sqlite db engine
        """
        pass
        # connection_string = 'sqlite:///:memory:'
        # print( "creating connection: %s " % connection_string )
        # self.engine = create_engine( connection_string, echo=False )
        #
        # Base.metadata.create_all( self.engine )

    def initialize_db_file( self ):
        """
        Creates tables in the database
        :return:
        """
        pass

        # Base.metadata.create_all( self.engine )


    def _make_file_engine( self, filepath ):
        pass
        # connection_string = 'sqlite:///{}'.format( filepath )
        # print( "creating connection: %s " % connection_string )
        # self.engine = create_engine( connection_string, echo=False )


if __name__ == '__main__':
    pass
