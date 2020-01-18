"""
Tools for handling and maintaining who is assigned to review whom

Created by adam on 12/28/19
"""
__author__ = 'adam'
import numpy as np
from sqlalchemy import Column, Integer
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

from CanvasHacks import environment as env
from CanvasHacks.Models.model import Model
from CanvasHacks.Models.student import Student

Base = declarative_base()


def assign_reviewers( student_ids ):
    """
    Takes a list of student ids and creates a dict
    of reviewers by shifting them all one to the right

    >>>test_ids = [1, 2, 3, 4]
    >>>test_ids = [1, 2, 3, 4, 5, 6, 7]
    >>>r = assign_reviewers(test_ids)
    >>>for a, b in r:
    >>>   assert(a != b) # no id assigned to self
    """
    return list( zip( student_ids, np.roll( student_ids, 1 ) ) )


class ReviewAssociation( Base, Model ):
    __tablename__ = env.REVIEW_ASSOCIATIONS_TABLE_NAME
    id = Column( Integer, primary_key=True )
    activity_id = Column( Integer )
    assessor_id = Column( Integer )
    assessee_id = Column( Integer )

    # def __init__(self, activity, assessor, assessee):
    #     self.activity = activity
    #     self.assessor = assessor
    #     self.assessee = assessee
    def __repr__( self ):
        return "<ReviewAssociation(activity_id={}, assessor_id={}, assessee_id={}".format(self.activity_id, self.assessor_id, self.assessee_id)
        # "<User(name='%s', fullname='%s', nickname='%s')>" % (
        # ...                             self.name, self.fullname, self.nickname)

    @property
    def assessee( self ):
        return Student(self.assessee_id)

    @property
    def assessor( self ):
        return Student(self.assessor_id)

from sqlalchemy.orm import sessionmaker


class SqliteDAO( object ):
    """
    Makes a connection to sqlite database.
    [following is from import from twitter tools]
    Note that does not actually populate the database. That
    requires a call to: Base.metadata.create_all(SqliteConnection)
    """

    def __init__( self, db_filepath=None ):
        if db_filepath:
            self._make_file_engine( db_filepath )
        else:
            self._create_memory_engine()

        self._connect()
        # if db_filepath:
        #     # We'ere going to use a file based database
        #      self._make_file_engine(db_filepath)
        # else:
        #     self._create_memory_engine()

    def _connect( self ):
        self.session_factory = sessionmaker( bind=self.engine )
        self.session = self.session_factory()

    def _create_memory_engine( self ):
        """Creates an in-memory sqlite db engine"""
        connection_string = 'sqlite:///:memory:'
        print( "creating connection: %s " % connection_string )
        self.engine = create_engine( connection_string, echo=False )

        Base.metadata.create_all(self.engine)
        # print( "creating connection: %s " % conn )
        # self.engine = create_engine( conn, echo=False )

    def _make_file_engine( self, filepath ):
        connection_string =  'sqlite:{}'.format( filepath )
        print( "creating connection: %s " % connection_string )
        self.engine = create_engine( connection_string, echo=False )

    # self.engine = create_engine( 'sqlite:{}'.format( filepath), echo=False )


class AssociationRepository:

    def __init__( self, dao ):
        """
        :param db_loc: Where to find the sqlite database or 'sqlite:///:memory:'
        """
        self.session = dao.session

    #     self._connect()
    #
    # def _connect( self ):
    #     self.engine = create_engine(self.db_loc)
    #
    #
    # self.connection = sqlite3.connect(self.db_loc)
    # self.cursor = self.connection.cursor()

    # def _handle_result( self, row ):
    #     """Loads a ReviewAssociation object """

    def get_associations( self, activity ):
        return self.session.query( ReviewAssociation )\
            .filter( ReviewAssociation.activity_id == activity.id )\
            .all()
        #
        #
        # query = """FROM {table_name} SELECT assessor, assessee WHERE activity_id = {activity_id}"""
        #
        # data = {'table_name' : self.table_name, 'activity_id' : activity.id }
        #
        # results = []
        #
        # for row in self.cursor.execute(query.format(**data)):
        #     ra = ReviewAssociation( activity, row[0], row[1])
        #     results.append(ra)
        #
        # return results

    def create_association( self, activity, assessor, assessee ):
        ra = ReviewAssociation( activity_id=activity.id, assessor_id=assessor.id, assessee_id=assessee.id )
        self.session.add( ra )
        self.session.commit()

    def get_reviewer( self, activity, submitter: Student ):
        """Returns the student assigned to review the submitter"""
        return self.session.query( ReviewAssociation ) \
            .filter( ReviewAssociation.activity_id == activity.id ) \
            .filter(ReviewAssociation.assessor_id == submitter.id ) \
            .one()

    def get_submitter( self, activity, reviewer: Student ):
        """Returns the student assigned to review the submitter"""
        return self.session.query( ReviewAssociation )\
            .filter( ReviewAssociation.activity_id == activity.id )\
            .filter(ReviewAssociation.assessor_id == reviewer.id )\
            .one()

    def get_for_assignment( self, assignment ):
        """Returns list of all submitter, reviewer tuples"""
        pass


if __name__ == '__main__':
    pass
