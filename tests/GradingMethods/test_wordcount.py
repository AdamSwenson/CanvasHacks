"""
Created by adam on 3/15/20
"""
__author__ = 'adam'

from unittest import TestCase

from CanvasHacks.GradingMethods.wordcount import GradeByWordCount, make_pct_required_count_thresholds
from TestingBase import TestingBase
import random
if __name__ == '__main__':
    pass

class TestMakePctRequiredCountThresholds(TestingBase):
    def setUp(self) -> None:
        self.config_for_test()

    def test_by_tens( self ):
        required_cnt = 100
        result = make_pct_required_count_thresholds(required_cnt)

        self.assertEqual(10, len(result))

        min_counts = [p for p in range( 0, 100, 10 )]

        for r in result:
            self.assertIn(r['min_count'], min_counts, "Not an unexpected min count")


class TestGradeByWordCount( TestingBase ):

    def setUp(self) -> None:
        self.config_for_test()
        self.dicts = [{ 'min_count': 100, 'pct_credit': 10},
                              { 'min_count': 200, 'pct_credit': 20},
                              { 'min_count': 300, 'pct_credit': 30},
                              { 'min_count': 400, 'pct_credit': 40}]


    def test_prepare_dicts( self ):

        input_dicts = self.dicts
        random.shuffle(input_dicts)
        # self.assertEqual(dicts[0]['count'], 100)

        obj = GradeByWordCount(input_dicts)
        obj.prepare_dicts()

        self.assertEqual(obj.threshold_dicts[0]['min_count'], 400)

    def test_grade( self ):
        # ( count, credit )
        expect = [ ( 50,  0), (100, 10), (275, 20), (888, 40) ]

        obj = GradeByWordCount(self.dicts)

        for count, credit in expect:
            content = " ".join( [ self.fake.word() for _ in range( 0, count ) ] )

            self.assertEqual(obj.grade(content), credit, "Returns correct pct as 0-100")
