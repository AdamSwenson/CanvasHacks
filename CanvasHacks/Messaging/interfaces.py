"""
Created by adam on 2/28/20
"""
__author__ = 'adam'

if __name__ == '__main__':
    pass


class ISender:
    """Parent of all classes which handle sending
    messages to students"""

    def send( self ):
        """
        Handles sending through whatever channel
        :return:
        :raises MessageSendError which wraps the server's error
        """
        raise NotImplementedError