"""
Created by adam on 3/16/20
"""
__author__ = 'adam'

from CanvasHacks.Definitions.activity import Activity
from CanvasHacks.GradingAnalyzers.nonempty import NonEmpty
from CanvasHacks.GradingMethods.review import ReviewBased
from CanvasHacks.Models.model import Model
from CanvasHacks.Text.stats import WordCount

if __name__ == '__main__':
    pass

class ActivityPoints(Model):

    def __init__(self, activity: Activity, total_points):
        self.activity = activity
        self.total_points = total_points

        self.composition = [
            (NonEmpty, 0.25),
            (WordCount, 0.50),
            (ReviewBased, 0.25)

        ]