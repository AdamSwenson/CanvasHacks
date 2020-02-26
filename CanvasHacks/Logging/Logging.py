"""
Created by adam on 1/22/20
"""
import csv

from CanvasHacks.Logging.interfaces import ILogger
from CanvasHacks.Logging.templates import entry_separator, error_entry_separator

__author__ = 'adam'

if __name__ == '__main__':
    pass

import CanvasHacks.environment as env


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

# ---------------------------- Decorators


