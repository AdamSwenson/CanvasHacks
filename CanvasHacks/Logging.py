"""
Created by adam on 1/22/20
"""
import csv
from functools import wraps

__author__ = 'adam'

if __name__ == '__main__':
    pass

from datetime import datetime

from logbook import Logger
import CanvasHacks.environment as env


def entry_separator():
    """Standard separator between log entries for all text logs"""
    return '\n --------------------------------- {} --------------------------- \n'.format( datetime.now() )


def error_entry_separator():
    """Standard separator between log entries for all text logs"""
    return '\n ===================== ERROR ===== {} ===== ERROR ===================== \n'.format( datetime.now() )


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


class CsvLogger( ILogger ):
    """Parent for loggers which write to csv file"""

    def __init__( self, log_file_path, logger_name='csvlogger', **kwargs ):
        self.logger_name = logger_name
        self.log_file_path = log_file_path

        # self.initialize_logger()

    def write( self, record ):
        """Writes a row to a csv log file
        Record should be a list of values
        """
        with open( self.log_file_path, 'a' ) as csvfile:
            writer = csv.writer( csvfile )
            writer.writerow( record )


class TextLogger( ILogger ):
    """
    Parent class for loggers which write to a textfile
    """

    def __init__( self, log_file_path=None, logger_name='csvlogger', **kwargs ):
        self.logger_name = logger_name
        # self.log_file_path = log_file_path

        # self.initialize_logger()

    @classmethod
    def initialize_logger( cls, log_file_path=None ):
        if log_file_path:
            cls.log_file_path = log_file_path
        t = "TEST-" if env.CONFIG.is_test else ""
        cls.log_file_path = "{}/{}{}".format( env.LOG_FOLDER, t, cls.log_file_name )

    # else:
        #     # todo raise error if LOG_FOLDER is none to indicate we want streaming log
        #     cls.log_file_path = env.STUDENT_WORK_PROCESSING_LOGNAME.format(env.LOG_FOLDER)

    @classmethod
    def write( cls, stuff, is_error=False ):
        """Writes to text log"""
        try:
            cls._actually_write( stuff, is_error )
        except AttributeError:
            cls.initialize_logger()
            cls._actually_write( stuff, is_error )

    @classmethod
    def _actually_write( cls, stuff, is_error=False ):
        """Abstracted out to allow automatic initialization"""
        with open( cls.log_file_path, 'a' ) as f:
            if is_error:
                f.write( error_entry_separator() )
                f.write( stuff.__str__() )
            else:
                f.write( entry_separator() )
                f.write( stuff )

    #
    # def initialize_logger( self ):
    #     try:
    #         if self.logger is not None:
    #             pass
    #     except:
    #         self.logger = Logger()
    #         # self.logger = FileHandler(self.log_file)
    #         # self.logger.push_application() #Pushes handler onto stack of log handlers
    #
    # def write( self, stuff ):
    #     with open( self.log_file_path, 'a' ) as f:
    #         f.write(entry_separator())
    #         f.write( stuff )
    #         # f.close()


class StudentWorkLogger( TextLogger ):
    """
    Handles logging student work
    """
    log_file_name = env.STUDENT_WORK_PROCESSING_LOGNAME

    # t = "TEST-" if env.CONFIG.is_test else ""
    # log_file_path = "{}/{}{}".format( env.LOG_FOLDER, t, env.STUDENT_WORK_PROCESSING_LOGNAME )


class MessageLogger( TextLogger ):
    """All outgoing messages logged with this"""
    log_file_name = env.MESSAGE_LOGNAME
    #
    # t = "TEST-" if env.CONFIG.is_test else ""
    # log_file_path = "{}/{}{}".format( env.LOG_FOLDER, t, env.MESSAGE_LOGNAME )


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
