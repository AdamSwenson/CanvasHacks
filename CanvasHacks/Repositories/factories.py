"""
Created by adam on 2/26/20
"""
__author__ = 'adam'

from CanvasHacks.Definitions.groups import ReviewType
from CanvasHacks.Errors.data_ingestion import NoStudentWorkDataLoaded, NoNewSubmissions
from CanvasHacks.Definitions.skaa import Review
from CanvasHacks.Repositories.assignments import AssignmentRepository
from CanvasHacks.Repositories.discussions import DiscussionRepository
from CanvasHacks.Repositories.quizzes import ReviewRepository, QuizRepository, DiscussionReviewRepository
from CanvasHacks.Repositories.submissions import QuizSubmissionRepository
from CanvasHacks.Loaders.factories import LoaderFactory

if __name__ == '__main__':
    pass


class WorkRepositoryFactory:
    """Decides what kind of repository is needed
    and instantiates it

    Used for ordinary quiz assignments that aren't part of skaa"""

    @staticmethod
    def make( activity, course=None, only_new=False, **kwargs ):
        # Get the object which will handle loading data
        # if only_new:
        #     loader = NewQuizReportFileLoader( activity, course )
        # else:
        #     loader = AllQuizReportFileLoader( activity, course )

        # Get quiz submission objects
        if isinstance( activity, ReviewType ):
            repo = ReviewRepository( activity, course )
        else:
            repo = QuizRepository( activity, course )
        return repo


class WorkRepositoryLoaderFactory:
    """Decides what kind of repository is needed
    and instantiates it after loading data into it

    Replaces make_quiz_repo
    """

    @classmethod
    def make( cls, activity, course=None, only_new=False, **kwargs ):
        """
        Returns a IContentRepository of the appropriate sort with all the
        relevant data loaded, processed, and stored as a dataframe on data
        kwags may contain
            download=True

        :param activity:
        :param course:
        :param only_new:
        :param kwargs:
        :return: IContentRepository
        """
        # Get the object which handles loading student data
        # The params will determine whether this is from file or download
        loader = LoaderFactory.make( is_quiz=activity.is_quiz_type,
                                     is_discussion=activity.is_discussion_type,
                                     combo=True,
                                     **kwargs)

        if activity.is_discussion_type:
            return cls._for_discussion_type_activity(activity, course, loader, **kwargs)

        if activity.is_quiz_type:
            # If uses a quiz report, downloads report and populates the
            # appropriate repository (QuizRepository or ReviewRepository)
            return cls._for_quiz_type_activity(activity, course, loader, **kwargs)

        return cls._for_assignment_type_activity(activity, course, loader, **kwargs)

    @classmethod
    def _for_quiz_type_activity(cls, activity, course, loader, **kwargs):
        """
        Handles the loading if the activity_inviting_to_complete uses a quiz report
        :param activity:
        :param course:
        :param loader:
        :param kwargs:
        :return:
        """
        # Get quiz submission objects
        if isinstance( activity, Review ):
            repo = ReviewRepository( activity, course )
        else:
            repo = QuizRepository( activity, course )

        try:
            student_work_frame = loader.load( activity, course,  **kwargs )

        # Doing each separately so can modify if needed
        except NoStudentWorkDataLoaded:
            raise NoStudentWorkDataLoaded

        except NoNewSubmissions:
            raise NoNewSubmissions

        if student_work_frame is None or len(student_work_frame) == 0:
            # This indicates that all attempts to acquire data
            # have failed and no further will be attempted
            raise NoStudentWorkDataLoaded

        # Download submissions
        subRepo = QuizSubmissionRepository( repo.quiz )

        # Doing the combination with submissions after saving to avoid
        # mismatches of new and old data
        repo.process( student_work_frame, subRepo.frame )

        return repo

    @classmethod
    def _for_assignment_type_activity(cls, activity, course, loader, **kwargs):
        """
        Handles the loading if the activity_inviting_to_complete uses an unit (with no report)
        :param activity:
        :param course:
        :param loader:
        :param kwargs:
        :return:
        """
        repo = AssignmentRepository( activity, course )

        student_work_frame = loader.load( activity, course, **kwargs )

        if student_work_frame is None or len(student_work_frame) == 0:
            raise NoStudentWorkDataLoaded

        repo.process( student_work_frame )

        return repo

    @classmethod
    def _for_discussion_type_activity( cls, activity, course, loader=None, **kwargs ):
        """
        Handles Discussion and DiscussionReview activities
        NB, we don't use loader since will need to make a special one for the review
        but have left the param for now for consistency

        :param activity: Discussion|DiscussionReview
        :param course:
        :param loader:
        :param kwargs:
        :return:
        """

        if isinstance( activity, ReviewType ):
            repo = cls._for_discussion_review( activity=activity, course=course, **kwargs)

        else:
            repo = cls._for_discussion_forum( activity=activity, course=course, **kwargs)

        return repo

    @classmethod
    def _for_discussion_forum( cls, activity, course, **kwargs ):
        repo = DiscussionRepository( activity=activity, course=course, **kwargs )
        # todo refactor the downloading stuff out of the repository and into the loader
        repo.download()
        #
        # student_work_frame = loader.load( activity, course, **kwargs )
        #
        if len( repo.data ) == 0:
            raise NoStudentWorkDataLoaded
        #
        # repo.process( student_work_frame )
        return repo

    @classmethod
    def _for_discussion_review( cls, activity, course, **kwargs ):

        repo = DiscussionReviewRepository( activity=activity, course=course )

        # The params will determine whether this is from file or download
        # Need to create this special for the review since it is a quiz
        loader = LoaderFactory.make( is_quiz=True,
                                     is_discussion=False,
                                     combo=True,
                                     **kwargs )
        try:
            student_work_frame = loader.load( activity, course, **kwargs )

        # Doing each separately so can modify if needed
        except NoStudentWorkDataLoaded:
            raise NoStudentWorkDataLoaded

        except NoNewSubmissions:
            raise NoNewSubmissions

        if student_work_frame is None or len( student_work_frame ) == 0:
            # This indicates that all attempts to acquire data
            # have failed and no further will be attempted
            raise NoStudentWorkDataLoaded

        # Download submissions
        subRepo = QuizSubmissionRepository( repo.quiz )

        # Doing the combination with submissions after saving to avoid
        # mismatches of new and old data
        repo.process( student_work_frame, subRepo.frame )
        return repo
