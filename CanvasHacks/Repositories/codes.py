"""
Created by adam on 1/18/20
"""
__author__ = 'adam'

import pandas as pd

class AccessCodeRepo:
    """Manages access codes for assignments which require them"""

    def __init__(self, access_codes_filepath, unit_number):
        print("Loading access codes from ", access_codes_filepath)
        self.data = pd.read_excel(access_codes_filepath)
        self.data = self.data[self.data.unit == unit_number]

    @property
    def review_code(self):
        return self.data[self.data.assignment == 'review'].code.values[0]

    @property
    def metareview_code(self):
        return self.data[self.data.assignment == 'metareview'].code.values[0]



if __name__ == '__main__':
    pass