"""
Created by adam on 2/25/20
"""
from logbook import Logger

__author__ = 'adam'

if __name__ == '__main__':
    pass


class ILogger( object ):

    def __init__( self, **kwargs ):
        self.logger = Logger( self.name )

    def _process_kwargs( self, kwargs ):
        for key, value in kwargs.items():
            setattr( self, key, value )

    def log( self, msg ):
        """Records record at notice level"""
        self.logger.notice( msg )

    def log_error( self, msg ):
        """Records record at error level"""
        self.logger.error( msg )

    def write( self, msg ):
        """Writes to a file"""
        raise NotImplementedError
