"""
Created by adam on 1/18/20
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

__author__ = 'adam'

if __name__ == '__main__':
    pass


class SqliteDAO( object ):
    """
    Makes a connection to sqlite database.
    [following is from import from twitter tools]
    Note that does not actually populate the database. That
    requires a call to: Base.metadata.create_all(SqliteConnection)
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
        connection_string = 'sqlite:///:memory:'
        print( "creating connection: %s " % connection_string )
        self.engine = create_engine( connection_string, echo=False )

        Base.metadata.create_all( self.engine )
        # print( "creating connection: %s " % conn )
        # self.engine = create_engine( conn, echo=False )

    def initialize_db_file( self ):
        """
        Creates tables in the database
        :return:
        """
        Base.metadata.create_all( self.engine )


    def _make_file_engine( self, filepath ):
        connection_string = 'sqlite:///{}'.format( filepath )
        print( "creating connection: %s " % connection_string )
        self.engine = create_engine( connection_string, echo=False )
