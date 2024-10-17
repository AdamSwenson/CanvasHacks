"""
Created by adam on 10/18/20
"""
__author__ = 'adam'

if __name__ == '__main__':
    pass

from CanvasHacks.TimeTools import utc_string_to_local_dt


class DateFormatterMixin:

    def make_date_for_message( self, utc_string ):
        """Returns a date formatted for sending in a
         message to a student.
        The date format will be: yyyy-mm-dd
        """
        if utc_string is None: return ''

        try:

            t = utc_string_to_local_dt( utc_string )
        except TypeError as e:
            # This likely happened because the date passed in was time
            # zone naive. That's not enough to kill the whole thing and there's
            # no general resolution (since we don't know what the timezone was
            # when the timestamp was stored). Thus we display an error but
            # continue
            print(e)
            t = utc_string

        return t.date().isoformat()
