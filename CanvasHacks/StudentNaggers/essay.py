"""
Created by adam on 3/14/20
"""
__author__ = 'adam'

if __name__ == '__main__':
    pass


from CanvasHacks.Messaging.nagging import EssayNonSubmittersMessaging


class EssayNagger:

    def __init__( self, overview_repo, send=True ):
        """

        :param overview_repo:
        :param send:
        """
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
                 self.overview_repo.no_essay.reviewed_by_id.tolist() ]

    def run( self ):
        # Initialize these here since may not have values when class instantiated
        self.unit = self.overview_repo.unit
        self.messenger = EssayNonSubmittersMessaging( self.unit, send=self.send )

        print( "Going to nag {} students to turn in essay".format( len( self.recipients ) ) )

        for cid, name in self.recipients:
            self.messenger.send_message_to_student( cid, name )
