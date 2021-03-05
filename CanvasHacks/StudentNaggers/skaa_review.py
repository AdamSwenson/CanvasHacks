"""
Created by adam on 3/14/20
"""
__author__ = 'adam'

from CanvasHacks.Logging.nagging import log_nag_messages
from CanvasHacks.SkaaSteps.ISkaaSteps import IStep

if __name__ == '__main__':
    pass

from CanvasHacks.Messaging.nagging import ReviewNonSubmittersMessaging


class SkaaReviewNagger(IStep):
    def __init__( self, overview_repo, is_test=None, send=True, **kwargs ):
            """
            :param course:
            :param unit:
            :param is_test:
            :param send: Whether to actually send the messages
            """
            self.send = send
            self.overview_repo = overview_repo
            # This will be the student repo and preempt loading of a new one in the
            # call to _initialize_db under _initialize()
            self.studentRepo = self.overview_repo.studentRepo

            self.unit = self.overview_repo.unit

            # ----- CAN-75 -----
            # All of the following is added in CAN-75 so can refer to the invitation date
            # in the message
            # ------------------
            super().__init__(  is_test=is_test, send=send, **kwargs )
            # The activity whose results we are going to be doing something with
            self.activity = self.unit.review

            # In sending the review results to the author we are
            # telling the about the feedback on the original assignment
            self.activity_feedback_on = self.unit.initial_work

            # The activity whose id is used to store review pairings for the whole SKAA
            self.activity_for_review_pairings = self.unit.initial_work

            # won't need other repos so just get the main review
            # assignments db loaded through dao
            self._initialize()


    @property
    def recipients( self ):
        """
        Returns list of (canvas id, name)
        :return:
        """
        return [ (cid, self.studentRepo.get_student_first_name( cid )) for cid in
                 self.overview_repo.non_reviewed.reviewed_by_id.tolist() ]

    def run( self ):

        self.messenger = ReviewNonSubmittersMessaging( unit=self.unit, send=self.send, dao=self.dao )

        print( "Going to nag {} students to turn in SKAA review".format( len( self.recipients ) ) )

        for cid, name in self.recipients:
            self.messenger.send_message_to_student( cid, name )

        log_nag_messages(activity=self.activity, list_of_sent_messages=self.messenger.sent, is_dry_run=self.is_test)
