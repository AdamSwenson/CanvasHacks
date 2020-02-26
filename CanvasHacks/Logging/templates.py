"""
Created by adam on 2/25/20
"""
from datetime import datetime

__author__ = 'adam'

if __name__ == '__main__':
    pass


def entry_separator():
    """Standard separator between log entries for all text logs"""
    return '\n --------------------------------- {} --------------------------- \n'.format( datetime.now() )


def error_entry_separator():
    """Standard separator between log entries for all text logs"""
    return '\n ===================== ERROR ===== {} ===== ERROR ===================== \n'.format( datetime.now() )