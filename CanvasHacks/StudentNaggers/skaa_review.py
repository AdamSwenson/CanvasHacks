"""
Created by adam on 3/14/20
"""
__author__ = 'adam'

if __name__ == '__main__':
    pass

from CanvasHacks.Messaging.nagging import ReviewNonSubmittersMessaging


class SkaaReviewNagger:
    def __init__( self, overview_repo, send=True ):
        self.send = send
        self.overview_repo = overview_repo
        self.studentRepo = self.overview_repo.studentRepo


    @property
    def recipients( self ):
        """
        Returns list of (canvas id, name)
        :return:
        """
        return [ (cid, self.studentRepo.get_student_first_name( cid )) for cid in
                 self.overview_repo.non_reviewed.reviewed_by_id.tolist() ]

    def run( self ):
        self.unit = self.overview_repo.unit

        self.messenger = ReviewNonSubmittersMessaging( self.unit, send=self.send )

        print( "Going to nag {} students to turn in SKAA review".format( len( self.recipients ) ) )

        for cid, name in self.recipients:
            self.messenger.send_message_to_student( cid, name )
