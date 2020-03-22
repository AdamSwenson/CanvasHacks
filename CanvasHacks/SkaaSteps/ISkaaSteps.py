"""
Created by adam on 2/23/20
"""
from CanvasHacks.DAOs.sqlite_dao import SqliteDAO
from CanvasHacks.Logging.display import DisplayManager
from CanvasHacks.Repositories.reviewer_associations import AssociationRepository
from CanvasHacks.Repositories.students import StudentRepository

__author__ = 'adam'

from CanvasHacks import environment as env
import CanvasHacks.testglobals
if __name__ == '__main__':
    pass


class IStep:
    """Parent of all steps in a Skaa"""

    def __init__( self, course=None, unit=None, is_test=None, send=True ):
        """
        :param course:
        :param unit:
        :param is_test:
        :param send: Whether to actually send the messages
        """
        self.course = env.CONFIG.course if course is None else course
        self.unit = env.CONFIG.unit if unit is None else unit
        self.is_test = env.CONFIG.is_test if is_test is None else is_test
        self.send = send



    def _initialize( self ):
        """Creates and populates all relevant repositories and db access points"""
        self.studentRepo = StudentRepository( self.course )
        self.studentRepo.download()
        self._initialize_db()
        self.associationRepo = AssociationRepository( self.dao, self.activity_for_review_pairings)

        self.display_manager = DisplayManager(self.activity)

        # Moved to child classes while working on CAN-53
        # if isinstance(self.activity, MetaReview) and isinstance(self.activity_notifying_about, MetaReview):
        #     # If both of these are the metareview, then we are on the final
        #     # step (sending the metareview results to the reviewer). Thus
        #     # we need a special status repository since the notified field
        #     # for the metareview will have already been populated in the previous step
        #     self.statusRepos = FeedbackStatusRepository( self.dao, self.activity_notifying_about )
        # elif isinstance(self.activity, DiscussionReview) and isinstance(self.activity_notifying_about, DiscussionReview):
        #     # If both of these are the discussion review, then we are on the final
        #     # step (sending the review results to the poster). Thus
        #     # we need a special status repository since the notified field
        #     # for the review will have already been populated in the previous step
        #     self.statusRepos = FeedbackStatusRepository( self.dao, self.activity_notifying_about )
        # else:
        #     self.statusRepos = StatusRepository( self.dao, self.activity_notifying_about )

    def _initialize_db( self ):
        try:
            t = 'TEST-' if env.CONFIG.is_test else ""
            self.db_filepath = "{}/{}{}-Unit-{}-review-assigns.db".format( env.LOG_FOLDER, t, env.CONFIG.semester_name, self.unit.unit_number )
        except AttributeError as e:
            # This is likely to happen during testing
            print(e)

        if env.CONFIG.is_test:
            try:
                if CanvasHacks.testglobals.TEST_WITH_FILE_DB:
                    # testing: file db
                    self._initialize_file_db()
                    print( "Connected to TEST db file. {}".format( self.db_filepath ) )
                else:
                    # testing: in memory db
                    self._initialize_memory_db()
            except (NameError, AttributeError) as e:
                print(e)
                # The variable might not be defined under in any
                # number of circumstances. So default to the in-memory db
                self._initialize_memory_db()

        else:
            # real: file db
            self._initialize_file_db()
            print( "Connected to REAL db. {}".format( self.db_filepath ) )

    def _initialize_file_db( self ):
        self.dao = SqliteDAO( self.db_filepath )
        self.dao.initialize_db_file()

    def _initialize_memory_db( self ):
        self.dao = SqliteDAO()
        print( "Connected to in-memory testing db" )

    def run( self ):
        raise NotImplementedError
