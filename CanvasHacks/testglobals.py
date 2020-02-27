"""
Only used to influence variables in environoment upon
first load during testing.

Created by adam on 2/24/20
"""
__author__ = 'adam'

TEST = False
"""Whether environment should load into test state"""

use_api = True
"""Whether to interact with the server during testing"""

TEST_WITH_FILE_DB = False
"""Whether to connect to a file based db. If false, we use an in-memory db"""


if __name__ == '__main__':
    pass