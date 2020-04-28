"""
Created by adam on 4/23/20
"""
__author__ = 'adam'

import CanvasHacks.environment as env
from CanvasHacks.Files.FileTools import makeDataFileIterator, makeDataFileList
from CanvasHacks.Models.model import StoreMixin


# def make_content_filepath( term, week_num, course_id=None, folder=env.ASSESSMENT_CONTENT_FOLDER, **kwargs ):
#     return "{}/{}-{}-week{}-content.json".format( folder, term, course_id, week_num )
#
#
# def make_bag_filepath( term, week_num, course_id=None, folder=env.ASSESSMENT_BAG_FOLDER, **kwargs ):
#     return "{}/{}-{}-week{}-bag.json".format( folder, term, course_id, week_num )
#

def make_week_iterator( start=1, stop=16 ):
    for w in range( start, stop + 1 ):
        yield w



class IAssessmentFileHandler( StoreMixin ):


    def __init__(self, **kwargs):
        self.handle_kwargs(**kwargs)

    @property
    def bag_folder_root( self ):
        return "{}/bags".format( self.data_folder )

    @property
    def content_folder_root( self ):
        return "{}/content".format( self.data_folder )


    def make_content_file_iterator( self ):
        """
        Returns an iterator that will yield each
        file in the content_folder_root
        :return:
        """
        return makeDataFileIterator(self.content_folder_root)

    def make_bag_file_iterator( self ):
        """
        Returns an iterator that will yield each
        file in the bag_folder_root
        :return:
        """
        return makeDataFileIterator(self.bag_folder_root)

    @property
    def bag_files( self ):
        """
        Returns a list of all existing bag files
        :return:
        """
        return makeDataFileList( self.bag_folder_root )

    def make_content_filepath( self, **kwargs ):
        raise NotImplementedError

    def make_bag_filepath( self, **kwargs ):
        raise NotImplementedError


class JournalFiles( IAssessmentFileHandler ):
    content_filename_templ = "{}/{}-{}-week{}-content.json"
    bag_filename_templ = "{}/{}-{}-week{}-bag.json"

    def __init__(self, **kwargs):
        """
        data_folder
            can be passed in and it will be set on the object overwriting
            the default
        :param kwargs:
        """
        self.data_folder = env.ASSESSMENT_JOURNALS_FOLDER
        self.handle_kwargs(**kwargs)

    def make_content_filepath( self, term, week_num, course_id=None, **kwargs ):
        """
        Returns a full filepath to the content file for the given term, unit, course
        :param week_num:
        :param term:
        :param course_id:
        :param kwargs:
        :return:
        """
        return self.content_filename_templ.format( self.content_folder_root, term, course_id, week_num )

    def make_bag_filepath( self, term, week_num, course_id=None, **kwargs ):
        """
        Returns a full filepath to the bag file for the given term, unit, course
        :param week_num:
        :param term:
        :param course_id:
        :param kwargs:
        :return:
        """
        return self.bag_filename_templ.format( self.bag_folder_root, term, course_id, week_num )


class EssayFiles( IAssessmentFileHandler ):
    content_filename_templ = "{path}/{term}-{course_id}-unit{unit_number}-content.json"
    bag_filename_templ = "{path}/{term}-{course_id}-unit{unit_number}-bag.json"

    def __init__(self, **kwargs):
        """
        data_folder
            can be passed in and it will be set on the object overwriting
            the default
        :param kwargs:
        """
        self.data_folder = env.ASSESSMENT_ESSAYS_FOLDER
        self.handle_kwargs(**kwargs)

    def make_content_filepath( self, term, unit_number, course_id=None, **kwargs ):
        """
        Returns a full filepath to the content file for the given term, unit, course
        :param term:
        :param unit_number:
        :param course_id:
        :param kwargs:
        :return:
        """
        return self.content_filename_templ.format( path=self.content_folder_root,
                                                   term=term,
                                                   course_id=course_id,
                                                   unit_number=unit_number )

    def make_bag_filepath( self, term, unit_number, course_id=None, **kwargs ):
        """
        Returns a full filepath to the bag file for the given term, unit, course
        :param term:
        :param unit_number:
        :param course_id:
        :param kwargs:
        :return:
        """
        return self.bag_filename_templ.format( path=self.bag_folder_root,
                                               term=term,
                                               course_id=course_id,
                                               unit_number=unit_number )



if __name__ == '__main__':
    pass
