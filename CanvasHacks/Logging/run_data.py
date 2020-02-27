"""
Loggers for simple data about when ran, how many students affected etc
Created by adam on 2/25/20
"""
import CanvasHacks.environment as env
from CanvasHacks.Logging.Logging import TextLogger
from CanvasHacks.TimeTools import current_utc_timestamp

__author__ = 'adam'


class RunLogger( TextLogger ):
    """Logs simple things like when ran etc"""
    log_file_name = env.RUN_LOGNAME

    entry_template = """ 
        \n --------- {time} --------- \n
        Checked for new submissions on activity_inviting_to_complete: {activity_name}
        {message}
        \n -------------------------- \n
        """

    @classmethod
    def log_no_submissions( cls, submitted_activity, time_to_record=None ):
        if time_to_record is None:
            time_to_record = current_utc_timestamp()
        d = {
            'activity_name': submitted_activity.name,
            'time': time_to_record,
            'message': 'No new submissions. No actions taken.'
        }
        cls.write( cls.entry_template.format( **d ) )

    @classmethod
    def log_reviews_assigned( cls, assigned_activity, message, time_to_record=None ):
        if time_to_record is None:
            time_to_record = current_utc_timestamp()
        d = {
            'activity_name': assigned_activity.name,
            'time': time_to_record,
            'message': message
        }
        cls.write( cls.entry_template.format( **d ) )

    @classmethod
    def log_review_feedback_distributed( cls, assigned_activity, message, time_to_record=None ):
        if time_to_record is None:
            time_to_record = current_utc_timestamp()
        d = {
            'activity_name': assigned_activity.name,
            'time': time_to_record,
            'message': message
        }
        cls.write( cls.entry_template.format( **d ) )

    @classmethod
    def log_metareview_feedback_distributed( cls, assigned_activity, message, time_to_record=None ):
        if time_to_record is None:
            time_to_record = current_utc_timestamp()
        d = {
            'activity_name': assigned_activity.name,
            'time': time_to_record,
            'message': message
        }
        cls.write( cls.entry_template.format( **d ) )



if __name__ == '__main__':
    pass
