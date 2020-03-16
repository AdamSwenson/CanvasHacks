"""
Tools for downloading data from assignments that do not
use quiz reports
Created by adam on 2/26/20
"""
from CanvasHacks.Loaders.interfaces import ILoader
from CanvasHacks.Files.QuizReportFileTools import save_downloaded_report

__author__ = 'adam'

from CanvasHacks.Repositories.submissions import AssignmentSubmissionRepository

if __name__ == '__main__':
    pass


class AssignmentDownloadLoader( ILoader ):
    """Loads all records for quiz"""

    @staticmethod
    def load( activity, course, save=True, **kwargs ):
        """
        Handles loading data for a non-quiz unit
        :param activity:
        :param course:
        :param kwargs:
        :return: DataFrame
        """
        # We need the canvas.api.unit object
        assignment = AssignmentDownloadLoader.get_assignment( course, activity )
        subRepo = AssignmentSubmissionRepository( assignment )

        # parse out already graded submissions
        # subRepo.data =[j for j in subRepo.data if j[0].grade != 'complete']
        if save:
            # Want to have all the reports be formatted the same
            # regardless of whether we manually or programmatically
            # downloaded them. Thus we save before doing anything to them.
            save_downloaded_report( activity, subRepo.frame )

        return subRepo.frame
