"""
Created by adam on 3/3/20
"""
__author__ = 'adam'


class DisplayManager:
    """Holds data on an iskaa step and handles reporting"""

    def __init__(self, activity):
        self.activity = activity
        # Loading and preparing data
        self._initial_load_count = None
        self._post_filter_count = None

        # Sending notifications
        self._number_to_send = None
        self._number_sent = None

    @property
    def initially_loaded( self ):
        return self._initial_load_count

    @initially_loaded.setter
    def initially_loaded( self, countable ):
        num = countable if isinstance(countable, int) else len(countable)
        self._initial_load_count = num
        print("{} \nLoaded students' work: \t {}".format(self.activity.name, self._initial_load_count ))

    @property
    def number_filtered( self ):
        try:
            return self._initial_load_count - self._post_filter_count
        except Exception as e:
            # print('dm' , e)
            pass

    @property
    def post_filter( self ):
        return self._post_filter_count

    @post_filter.setter
    def post_filter( self, countable ):
        num = countable if isinstance(countable, int) else len(countable)
        self._post_filter_count = num

        print("Previously notified : \t {}".format(self.number_filtered))
        print("Remaining after filtration : \t {}".format(self._post_filter_count))

    @property
    def number_to_send( self ):
        return self._number_to_send

    @number_to_send.setter
    def number_to_send( self, countable):
        num = countable if isinstance( countable, int ) else len( countable )
        self._number_to_send = num

        print("To send: \t {}".format(self._number_to_send))

    @property
    def number_sent( self ):
        return self._number_sent

    @number_sent.setter
    def number_sent( self, countable ):
        num = countable if isinstance( countable, int ) else len( countable )
        self._number_sent = num

        print("Error sending: \t {}".format(self.send_errors_count))
        print("Successfully sent: \t {}".format(self._number_sent))


    @property
    def send_errors_count( self ):
        try:
            return self._number_to_send - self._number_sent
        except Exception as e:
            pass




if __name__ == '__main__':
    pass