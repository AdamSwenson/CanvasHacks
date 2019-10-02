"""
Created by adam on 10/1/19
"""
from CanvasHacks.Repositories.IRepositories import IRepo

__author__ = 'adam'

from CanvasHacks.RequestTools import send_multi_page_get_request
from CanvasHacks.UrlTools import make_url


class StudentRepository( IRepo ):

    def __init__( self, course_ids ):
        self.data = { }
        self.course_ids = course_ids
        for cid in course_ids:
            self.download( cid )

        print( "Loaded {} students".format( len( self.data.keys() ) ) )

    def _make_url( self, course_id ):
        """Makes the url for getting all students for course
        GET /api/v1/courses/:course_id/search_users """
        return make_url( course_id, 'search_users' )

    def download( self, course_id ):
        """Makes request to the server for all students enrolled in the
         course
        """
        data = { 'enrollment_type': 'student' }
        url = self._make_url( course_id )
        results = send_multi_page_get_request( url, data )
        self.store_results( results, course_id )

    def store_results( self, results_list, course_id ):
        """Stores student records in self.data with canvas id as keys"""
        for r in results_list:
            # Add the course id to the student result
            r[ 'course_id' ] = course_id
            # store it in data
            self.data[ r[ 'id' ] ] = r

    def get_student( self, canvas_id ):
        return self.data[ canvas_id ]

    def get_student_name( self, canvas_id ):
        try:
            s = self.get_student( canvas_id )
            return s['name']
        except KeyError:
            return ''


if __name__ == '__main__':
    pass
