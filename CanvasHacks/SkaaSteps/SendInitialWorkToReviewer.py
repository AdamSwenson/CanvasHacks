"""
Created by adam on 2/23/20
"""
from CanvasHacks.DAOs.sqlite_dao import SqliteDAO
from CanvasHacks.Errors.data_ingestion import NoNewSubmissions
from CanvasHacks.PeerReviewed.Notifications import StudentWorkForPeerReviewMessenger
from CanvasHacks.QuizReportFileTools import make_quiz_repo
from CanvasHacks.Repositories.quizzes import WorkRepositoryLoaderFactory
from CanvasHacks.Repositories.reviewer_associations import AssociationRepository, make_review_audit_file
from CanvasHacks.Repositories.students import StudentRepository
from CanvasHacks.SkaaSteps.ISkaaSteps import IStep

__author__ = 'adam'

import CanvasHacks.environment as env


class SendInitialWorkToReviewer(IStep):

    def __init__(self, course=None, unit=None, is_test=None, send=True, **kwargs):
        """
        :param course:
        :param unit:
        :param is_test:
        :param send: Whether to actually send the messages
        """
        super().__init__(**kwargs)
        self._initialize()


    def run(self, only_new=True):

        try:
            self.work_repo = WorkRepositoryLoaderFactory.make(self.unit.initial_work, self.course, only_new)
            # self.work_repo = make_quiz_repo( self.course, self.unit.initial_work )

            # Assign reviewers to each submitter and store in db
            self.associationRepo.assign_reviewers( self.work_repo.submitter_ids )

            if not self.is_test:
                make_review_audit_file(self.associationRepo, self.unit )

            # Send the work to the reviewers
            msgr = StudentWorkForPeerReviewMessenger( self.unit.review, self.studentRepo, self.work_repo )
            msgr.notify(self.associationRepo.data, self.send)

        except NoNewSubmissions:
            # Check if new submitters, bail if not
            print("No new submissions")
            # todo Log run failure



if __name__ == '__main__':
    pass