"""
Created by adam on 2/23/20
"""
from CanvasHacks.DAOs.sqlite_dao import SqliteDAO
from CanvasHacks.PeerReviewed.Notifications import StudentWorkForPeerReviewMessenger
from CanvasHacks.QuizReportFileTools import make_quiz_repo
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
        # self.course = env.CONFIG.course if course is None else course
        # self.unit = env.CONFIG.unit if unit is None else unit
        # self.is_test = env.CONFIG.is_test if is_test is None else is_test
        # self.send = send
        #
        # self.studentRepo = StudentRepository(self.course)
        # self.studentRepo.download()
        #
        # self.db_filepath = "{}/{}-Unit-{}-review-assigns.db".format( env.LOG_FOLDER, env.CONFIG.semester_name, self.unit.unit_number)
        #
        # self._initialize_db()
        # self.associationRepo = AssociationRepository(self.dao, self.unit.review)
    #
    # def _initialize_db( self ):
    #     if env.CONFIG.is_test:
    #         # testing: in memory db
    #         self.dao = SqliteDAO()
    #         print("Connected to testing db")
    #     else:
    #         # real: file db
    #         self.dao = SqliteDAO(self.db_filepath)
    #         self.dao.initialize_db_file()
    #         print("Connected to REAL db. {}".format(self.db_filepath))

    def run(self):
        self.work_repo = make_quiz_repo( self.course, self.unit.initial_work )

        # Check if new submitters, bail if not
        # todo

        # Assign reviewers to each submitter and store in db
        self.associationRepo.assign_reviewers( self.work_repo.submitter_ids )

        if not self.is_test:
            make_review_audit_file(self.associationRepo, self.unit )

        msgr = StudentWorkForPeerReviewMessenger( self.unit.review, self.studentRepo, self.work_repo )
        msgr.notify(self.associationRepo.data, self.send)


if __name__ == '__main__':
    pass