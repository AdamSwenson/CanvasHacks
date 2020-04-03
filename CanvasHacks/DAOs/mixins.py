"""
Created by adam on 3/13/20
"""
__author__ = 'adam'
import CanvasHacks.environment as env
from CanvasHacks.DAOs.sqlite_dao import SqliteDAO
import CanvasHacks.testglobals

if __name__ == '__main__':
    pass


class DaoMixin:
    """
    Provides database access initialization.
    Requires that self.unit be set
    """

    def _initialize_db( self ):
        try:
            unit_number = self.unit.unit_number
        except AttributeError:
            unit_number = self.activity.unit_number

        try:
            t = 'TEST-' if env.CONFIG.is_test else ""
            self.db_filepath = "{}/{}{}-Unit-{}-review-assigns.db".format( env.LOG_FOLDER, t, env.CONFIG.semester_name, unit_number )
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
