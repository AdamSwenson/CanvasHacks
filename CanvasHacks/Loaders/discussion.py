"""
Created by adam on 3/2/20
"""
__author__ = 'adam'



from CanvasHacks.Loaders.interfaces import ILoader

__author__ = 'adam'

from CanvasHacks.Repositories.discussions import DiscussionRepository


class DiscussionDownloadLoader( ILoader ):
    """Loads all records for quiz"""

    @classmethod
    def load( cls, activity, course, save=True, **kwargs ):
        """
        Handles loading data for a non-quiz unit
        :param activity:
        :param course:
        :param kwargs:
        :return: DataFrame
        """
        print( "Downloading posts for {}", activity.name )
        discussionRepo = DiscussionRepository( activity, course )
        discussionRepo.download()

        return discussionRepo

        #todo re-enable saving

        # We need the canvas.api.unit object
        # assignment = DiscussionDownloadLoader.get_assignment( course, activity )
        # subRepo = AssignmentSubmissionRepository( assignment )
        #
        # # parse out already graded submissions
        # # subRepo.data =[j for j in subRepo.data if j[0].grade != 'complete']
        # if save:
        #     # Want to have all the reports be formatted the same
        #     # regardless of whether we manually or programmatically
        #     # downloaded them. Thus we save before doing anything to them.
        #     save_downloaded_report( activity, subRepo.frame )

        # return subRepo.frame



class DiscussionFileLoader( ILoader ):
    """Loads all records for discussion from file"""

    @classmethod
    def load( cls, activity, course, save=True, **kwargs ):
        """
        Handles loading data for a non-quiz unit
        :param activity:
        :param course:
        :param kwargs:
        :return: DataFrame
        """
        # todo

        # print( "Downloading posts for {}", activity.name )
        # discussionRepo = DiscussionRepository( course, activity.topic_id )
        # discussionRepo.download()

        #todo re-enable saving

        # We need the canvas.api.unit object
        # assignment = DiscussionDownloadLoader.get_assignment( course, activity )
        # subRepo = AssignmentSubmissionRepository( assignment )
        #
        # # parse out already graded submissions
        # # subRepo.data =[j for j in subRepo.data if j[0].grade != 'complete']
        # if save:
        #     # Want to have all the reports be formatted the same
        #     # regardless of whether we manually or programmatically
        #     # downloaded them. Thus we save before doing anything to them.
        #     save_downloaded_report( activity, subRepo.frame )

        # return subRepo.frame







if __name__ == '__main__':
    pass