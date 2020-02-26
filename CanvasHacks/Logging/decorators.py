"""
Created by adam on 2/25/20
"""
from functools import wraps

from CanvasHacks.Logging.Logging import StudentWorkLogger
from CanvasHacks.Logging.messages import MessageLogger

__author__ = 'adam'

if __name__ == '__main__':
    pass


def log_student_work( func ):
    """Decorator for writing to the STUDENT_WORK_PROCESSING_LOGNAME log"""

    @wraps( func )
    def wrapper( *args, **kwargs ):
        # handle logging
        StudentWorkLogger.write( "\n".join( args ) )
        # call og function
        func( *args, **kwargs )

    return wrapper


def log_message( func ):
    """Wraps function which sends messages to students
    and writes outgoing message info to log
    """

    @wraps( func )
    def wrapper( *args, **kwargs ):
        margs = "\n".join( [ str( a ) for a in args ] )
        mkwargs = "\n".join( [ "{} \t: {}".format( k, v ) for k, v in kwargs.items() ] )
        to_log = "{}\n{}".format( margs, mkwargs )
        # handle logging
        # MessageLogger.write( to_log )
        try:
            # call og function
            result = func( *args, **kwargs )
            if result:
                to_log += " \n ------- RESULT ------- \n "
                to_log += str( result )
                MessageLogger.write( to_log )
                return result
            MessageLogger.write( to_log )

        except Exception as e:
            to_log += " \n ------- ERROR ------- \n "
            to_log += e.__str__()
            MessageLogger.write( to_log, is_error=False )
            raise e

    return wrapper

    #

    # def __init__( self, log_file_path=.format() ):
    #     self.log = ''
    #     super().__init__( )
    #     self.log_file = log_file
    #     # self.UPATH = os.getenv("HOME")
    #     # self.log_file = '%s/Desktop/%s' % self.UPATH, log_file
    #     # self.log_file = "application_search.log"
    #     self.set_log_file( self.log_file )
    #
    # def write_to_file( self ):
    #     self.write( self.log )
    #     self.log = ''
    #
    # def run_start( self, run_number ):
    #     self.log += '\n --------------------------------- %s --------------------------- ' % datetime.now()
    #     self.log += "\n Run number: %d " % run_number
    #     self.write_to_file()
    #     print( self.log )
    #
    # def record_saver_action( self, savername, num_tweets ):
    #     """
    #     This will be called inside the observer to log a saver class action
    #     Args:
    #         savername: String name of the saver (mysql, redis, couchdb)
    #         num_tweets: Integer number of tweets saved
    #     """
    #     self.log += '\n         Called saver for %s to save %s tweets' % (savername, num_tweets)
    #     self.write_to_file()
    #