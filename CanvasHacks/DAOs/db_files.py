"""
Standard naming of database files

Created by adam on 5/5/20
"""
__author__ = 'adam'

import CanvasHacks.environment as env


ESSAY_REVIEW_TEMPLATE = "{folder_path}/{test_string}{semester_name}-Unit-{unit_number}-review-assigns.db"
DISCUSSION_REVIEW_TEMPLATE = "{folder_path}/{test_string}{semester_name}-Unit-{unit_number}-discussion-review.db"
MESSAGE_QUEUE_TEMPLATE = "{folder_path}/{test_string}{semester_name}-message-queue.db"

class DBFilePathHandler:

    @staticmethod
    def _handle_defaults( unit_number, is_test=None, folder_path=None, semester_name=None ):
        """
        Creates a dictionary to use to make the path. Substitutes
        environmental values for the kwargs that are None
        :param unit_number:
        :param is_test:
        :param folder_path:
        :param semester_name:
        :return:
        """
        is_test = is_test if is_test is not None else env.CONFIG.is_test
        return {
            'test_string': 'TEST-' if is_test else "",
            'folder_path': folder_path if folder_path is not None else env.LOG_FOLDER,
            'semester_name': semester_name if semester_name is not None else env.CONFIG.semester_name,
            'unit_number': unit_number
        }

    @staticmethod
    def essay_review( unit_number, **kwargs):
        """
        Creates a standard filepath to the database holding associations
        for the peer review of an essay

        :param unit_number:
        :param is_test: Default env.CONFIG.is_test
        :param parent_folder: The name of the folder holding the db files. Default env.LOG_FOLDER
        :param semester_name: Default env.CONFIG.semester_name
        :return:
        """
        s = DBFilePathHandler._handle_defaults(unit_number, **kwargs)
        return ESSAY_REVIEW_TEMPLATE.format(**s)
        # is_test = is_test if is_test is not None else env.CONFIG.is_test
        # parent_folder = parent_folder if parent_folder is not None else env.LOG_FOLDER
        # semester_name = semester_name if semester_name is not None else env.CONFIG.semester_name
        #
        # t = 'TEST-' if is_test else ""
        # return "{}/{}{}-Unit-{}-review-assigns.db".format( parent_folder, t, semester_name, unit_number )

    @staticmethod
    def discussion_review( unit_number, **kwargs ):
        """
        Creates a standard filepath to the database holding associations
        for the peer review of an essay

        :param unit_number:
        :param is_test: Default env.CONFIG.is_test
        :param parent_folder: The name of the folder holding the db files. Default env.LOG_FOLDER
        :param semester_name: Default env.CONFIG.semester_name
        :return:
        """
        s = DBFilePathHandler._handle_defaults( unit_number, **kwargs )
        return DISCUSSION_REVIEW_TEMPLATE.format( **s )

    @staticmethod
    def message_queue( **kwargs):
        """
        Creates a standard filepath to the database holding the message queue. This is
        independent from the database which holds associations. It is relative to the
        entire semester:
        :param kwargs:
        :return:
        """
        s = DBFilePathHandler._handle_defaults(0, **kwargs)
        return MESSAGE_QUEUE_TEMPLATE.format(**s)


if __name__ == '__main__':
    pass
