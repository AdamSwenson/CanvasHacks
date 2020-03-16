"""
Created by adam on 10/1/19
"""
import CanvasHacks.environment as env
from CanvasHacks.Models.student import Student
from CanvasHacks.Repositories.interfaces import IRepo

__author__ = 'adam'

from CanvasHacks.Api.RequestTools import send_multi_page_get_request
from CanvasHacks.Api.UrlTools import make_url


class StudentRepository( IRepo ):
    """Manages information about students downloaded
    using canavasapi
    """

    def __init__( self, course_objects=[] ):
        """
        :param course_objects: List of canvasapi.Course objects or single object
        """
        if not isinstance(course_objects, list):
            course_objects = [course_objects]
        # List of canvas api objects
        self.course_objects = course_objects
        self.data = { }

    def download( self ):
        """Makes request to the server for all students enrolled in the
         course
        Stores student records in self.data with canvas id as keys
        """
        if len(self.course_objects) > 0:
            for course in self.course_objects:
                for u in course.get_users():
                    # Filter out teachers et al
                    if u.id not in env.CONFIG.excluded_users:
                        self.data[u.id] = u
        print( "Loaded {} students".format( len( self.data.keys() ) ) )

    # @property
    # def student_ids( self ):
    #     return list(set([k for k in self.data.keys()]))

    def get_student( self, canvas_id ):
        return self.data.get(canvas_id)
        # return Student(**s)
        # return Student(student_id=canvas_id, name=self.data[ canvas_id ])

    def get_student_name( self, canvas_id ):
        try:
            s = self.get_student( canvas_id )
            return s.name
            # return s['name']
        except KeyError:
            print('No student found for id: {}'.format(canvas_id))
            return ''
        except AttributeError:
            print('No student found for id: {}'.format(canvas_id))
            return ''

    def get_student_first_name( self, canvas_id ):
        full_name = self.get_student_name(canvas_id)

        if ',' in full_name:
            return full_name.split(',')[1]
        else:
            return full_name.split(' ')[0]

class StudentRepositoryOld( IRepo ):

    def __init__( self, course_ids=[] ):
        self.data = { }
        self.course_ids = course_ids
        # List of canvas api objects
        self.courses = []
        if len(course_ids) > 0:
            # option to use blank so can just load
            # test data from file manually
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
        # s = self.data.get(canvas_id)
        # return Student(**s)
        return Student(student_id=canvas_id, name=self.data[ canvas_id ])

    def get_student_name( self, canvas_id ):
        try:
            s = self.get_student( canvas_id )
            # return s.name
            return s['name']
        except KeyError:
            return ''


if __name__ == '__main__':
    pass
