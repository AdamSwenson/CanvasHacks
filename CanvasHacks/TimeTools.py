"""
Created by adam on 2/10/20
"""
import datetime

import pandas as pd

__author__ = 'adam'

if __name__ == '__main__':
    pass


def local_string_to_utc_dt( local_string ):
    """'2020-02-07T07:59:59Z'
    returns Timestamp('2020-02-06 23:59:59-0800', tz='US/Pacific')
    """
    return pd.to_datetime( local_string ).tz_localize('US/Pacific').tz_convert('UTC')


def utc_string_to_local_dt( utc_string ):
    """'2020-02-07T07:59:59Z'
    returns Timestamp('2020-02-06 23:59:59-0800', tz='US/Pacific')
    """
    return pd.to_datetime( utc_string ).tz_convert( 'US/Pacific' )


def check_is_date(date):
    """Checks that a value is a pd.Timestamp
       if not, it tries to make it into one"""
    return date if isinstance( date, pd.Timestamp ) else pd.to_datetime( date )


def getDateForMakingFileName():
    return datetime.date.isoformat( datetime.date.today() )