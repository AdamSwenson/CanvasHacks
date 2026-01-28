from unittest import TestCase
from CanvasHacks.DAOs.db_files import DBFilePathHandler


class TestDBFilePathHandler(TestCase):
    def test__handle_defaults(self):
        r = DBFilePathHandler._handle_defaults(3, True, 'path', 'S29')
        expect = {'folder_path': 'path',
                  'semester_name': 'S29',
                  'test_string': 'TEST-',
                  'unit_number': 3}

        self.assertEqual(r, expect, "Returns expected dictionary")

    def test_essay_review(self):
        nontest = "path/s88-Unit-100-review-assigns.db"
        r = DBFilePathHandler.essay_review(100, is_test=False, folder_path='path', semester_name='s88' )
        self.assertEqual(r, nontest, "Returns nontest path")

        test = "path/TEST-s88-Unit-100-review-assigns.db"
        r = DBFilePathHandler.essay_review(100, is_test=True, folder_path='path', semester_name='s88')
        self.assertEqual(r, test, "Returns test path ")


    # def test_discussion_review(self):
    #     self.fail()

    def test_message_queue(self):
        non_test = "path/s88-message-queue.db"
        r = DBFilePathHandler.message_queue(is_test=False, folder_path='path', semester_name='s88' )
        self.assertEqual(r, non_test, "Returns non test path")

        test = "path/TEST-s88-message-queue.db"
        r = DBFilePathHandler.message_queue(is_test=True, folder_path='path', semester_name='s88' )
        self.assertEqual(r, test, "Returns test path")
