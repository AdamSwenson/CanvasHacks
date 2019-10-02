"""
Created by adam on 10/1/19
"""
__author__ = 'adam'


class IRepo(object):

    def download(self, course_id):
        raise NotImplementedError

    def store_results( self, results_list ):
        raise NotImplementedError


if __name__ == '__main__':
    pass