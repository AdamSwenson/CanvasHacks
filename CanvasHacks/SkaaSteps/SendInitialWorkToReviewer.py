"""
Created by adam on 2/23/20
"""
from CanvasHacks.Errors.data_ingestion import NoNewSubmissions
from CanvasHacks.Messaging.Messengers import StudentWorkForPeerReviewMessenger
from CanvasHacks.Repositories.quizzes import WorkRepositoryLoaderFactory
from CanvasHacks.Repositories.reviewer_associations import make_review_audit_file
from CanvasHacks.SkaaSteps.ISkaaSteps import IStep

__author__ = 'adam'


class SendInitialWorkToReviewer( IStep ):

    def __init__( self, course=None, unit=None, is_test=None, send=True, **kwargs ):
        """
        :param course:
        :param unit:
        :param is_test:
        :param send: Whether to actually send the messages
        """
        super().__init__( course, unit, is_test, send, **kwargs )
        self._initialize()

    def run( self, only_new=True ):
        """
        Loads content assignments, assigns reviewers, and sends formatted
        work to reviewer
        :param only_new:
        :return:
        """
        try:
            self.work_repo = WorkRepositoryLoaderFactory.make( self.unit.initial_work, self.course, only_new )
            # self.work_repo = make_quiz_repo( self.course, self.unit.initial_work )

            # Assign reviewers to each submitter and store in db
            self.associationRepo.assign_reviewers( self.work_repo.submitter_ids )

            if not self.is_test:
                make_review_audit_file( self.associationRepo, self.unit )

            # Send the work to the reviewers
            self.messenger = StudentWorkForPeerReviewMessenger( self.unit.review, self.studentRepo, self.work_repo, self.statusRepo )
            self.messenger.notify( self.associationRepo.data, self.send )


        except NoNewSubmissions:
            # Check if new submitters, bail if not
            print( "No new submissions" )
            # todo Log run failure


if __name__ == '__main__':
    pass
