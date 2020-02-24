"""
Created by adam on 2/23/20
"""
from CanvasHacks.DAOs.sqlite_dao import SqliteDAO

__author__ = 'adam'

if __name__ == '__main__':
    pass


class StatusRepository:

    def __init__( self, dao: SqliteDAO, content_assignment_id):
        """
        Create a repository to handle review assignments for a
        particular activity
        """
        self.content_assignment_id = content_assignment_id
        self.session = dao.session
