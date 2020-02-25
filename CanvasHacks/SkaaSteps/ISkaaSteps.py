"""
Created by adam on 2/23/20
"""
from CanvasHacks.DAOs.sqlite_dao import SqliteDAO
from CanvasHacks.Repositories.reviewer_associations import AssociationRepository
from CanvasHacks.Repositories.students import StudentRepository

__author__ = 'adam'

from CanvasHacks import environment as env

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

        try:
            self.db_filepath = "{}/{}-Unit-{}-review-assigns.db".format( env.LOG_FOLDER, env.CONFIG.semester_name, self.unit.unit_number )
        except AttributeError as e:
            # This is likely to happen during testing
            print(e)


    def _initialize( self ):
        """Creates and populates all relevant repositories and db access points"""
        self.studentRepo = StudentRepository( self.course )
        self.studentRepo.download()
        self._initialize_db()
        self.associationRepo = AssociationRepository( self.dao, self.unit.review )

    def _initialize_db( self ):
        if env.CONFIG.is_test:
            # testing: in memory db
            self.dao = SqliteDAO()
            print( "Connected to testing db" )
        else:
            # real: file db
            self.dao = SqliteDAO( self.db_filepath )
            self.dao.initialize_db_file()
            print( "Connected to REAL db. {}".format( self.db_filepath ) )

    def run( self ):
        raise NotImplementedError
