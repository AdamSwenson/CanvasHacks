"""
Handles logging sent messages to students
Created by adam on 2/25/20
"""
from CanvasHacks import environment as env
from CanvasHacks.Logging.Logging import TextLogger

__author__ = 'adam'

if __name__ == '__main__':
    pass


class MessageLogger( TextLogger ):
    """All outgoing messages logged with this"""
    log_file_name = env.MESSAGE_LOGNAME
    #
    # t = "TEST-" if env.CONFIG.is_test else ""
    # log_file_path = "{}/{}{}".format( env.LOG_FOLDER, t, env.MESSAGE_LOGNAME )
