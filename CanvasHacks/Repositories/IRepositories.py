"""
Created by adam on 10/1/19
"""
__author__ = 'adam'


class IRepo(object):

    def download(self):
        raise NotImplementedError

    @property
    def student_ids( self ):
        if isinstance(self.data, dict):
            uids = list(set([k for k in self.data.keys()]))
        if isinstance(self.data, list):
            uids = list( set( [ k['student_id'] for k in self.data ] ) )
        uids.sort()
        return uids



    # def store_results( self, results_list ):
    #     raise NotImplementedError


if __name__ == '__main__':
    pass