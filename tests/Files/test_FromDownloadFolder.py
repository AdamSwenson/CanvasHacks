import unittest
import datetime

from CanvasHacks.Files.FromDownloadFolder import get_unit_number, is_csv, is_report, get_activity_type,\
    report_file_iterator, DOWNLOAD_FOLDER, file_reports
from CanvasHacks.PeerReviewed.Definitions import TopicalAssignment, Review, MetaReview, DiscussionReview


class TestUtilities( unittest.TestCase ):
    def test_is_csv( self ):
        cases = [ ('Unit 3_ Peer review Survey Student Analysis Report(2).csv', True),
                  ('Unit 3_ Warm up Quiz Student Analysis Report.csv', True),
                  ('Unit 3 stuff in pdf.pdf', False)
                  ]
        for case, expect in cases:
            self.assertEqual( expect, is_csv( case ) )

    def test_is_report( self ):
        cases = [
            ('Unit 3_ Discussion review Survey Student Analysis Report(1).csv', True),
            ('2020-03-15-Unit 3 Metareview-student-work.csv', True),
            ('Unit 34_ Peer review Survey Student Analysis Report(2).csv', True),
            ('Unit 3_ Warm up Quiz Student Analysis Report.csv', True),
            ('Taco truck report 3.csv', False),
            ('TacoUnit 23 report.pdf', False)
        ]
        for case, expect in cases:
            self.assertEqual( expect, is_report( case ), case )

    def test_get_unit_number( self ):
        cases = [
            ('Unit 3_ Discussion review Survey Student Analysis Report(1).csv', 3),
            ('2020-03-15-Unit 13 Metareview-student-work.csv', 13),
            ('Unit 34_ Peer review Survey Student Analysis Report(2).csv', 34),
            ('Unit 1_ Warm up Quiz Student Analysis Report.csv', 1),
            ('UNIT 1_ Warm up Quiz Student Analysis Report.csv', 1),
        ]
        for case, expect in cases:
            self.assertEqual( expect, get_unit_number( case ), case )

    def test_get_activity_type( self ):
        cases = [
            ('Unit 3_ Discussion review Survey Student Analysis Report(1).csv', DiscussionReview),
            ('2020-03-15-Unit 13 Metareview-student-work.csv', MetaReview),
            ('Unit 34_ Peer review Survey Student Analysis Report(2).csv', Review),
            ('Unit 1_ Warm up Quiz Student Analysis Report.csv', TopicalAssignment),
            ('UNIT 1_ Warm up Quiz Student Analysis Report.csv', TopicalAssignment),
        ]
        for case, expect in cases:
            self.assertEqual( expect, get_activity_type( case ), case )

    def test_report_file_iterator( self ):
        fiter = report_file_iterator(DOWNLOAD_FOLDER)
        # NB will not work if no files in actual download folder
        try:
            while True:
                f = next(fiter)
                # check correct keys
                self.assertIn('file_name', f.keys())
                self.assertIn('path', f.keys())
                self.assertIn('activity', f.keys())
        except StopIteration:
            pass

    def test_file_reports( self ):
        self.skipTest("Will actually run the program")
        # reports = file_reports(DOWNLOAD_FOLDER)
        # print(reports)
        # self.assertTrue(len(reports) > 0)


if __name__ == '__main__':
    unittest.main()
