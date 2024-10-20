"""
Created by adam on 4/23/20
"""
__author__ = 'adam'
import json

from CanvasHacks.Api.RequestTools import get_all_course_assignments
from CanvasHacks.Assessment.files import JournalFiles, EssayFiles, ReviewFiles
from CanvasHacks.Definitions.journal import Journal
from CanvasHacks import environment as env
from CanvasHacks.Definitions.skaa import InitialWork, MetaReview, Review
from CanvasHacks.Repositories.submissions import SubmissionRepository, QuizSubmissionRepository
from CanvasHacks.Text.cleaners import TextCleaner

from CanvasHacks.Repositories.factories import WorkRepositoryLoaderFactory


def get_all_journal_assigns_for_class(course_id, term):
    assignments = [ ]
    # Get list of all assignments for the courses
    assignments += get_all_course_assignments( course_id )
    assignments = [ (a[ 'id' ], a[ 'name' ].strip()) for a in assignments ]

    # If we we're passed an activity_inviting_to_complete, filter the assignments
    assignments = [a for a in assignments if Journal.is_activity_type(a[1])]

    assignments = [{ 'term': term,
                     'course_id': course_id,
                     'id': a[0],
                     'week_num' : int(a[1].split(' ')[-1][ : -1])
                     } for a in assignments]
    return assignments


def get_all_essay_assigns_for_class(course_id, term):
    assignments = [ ]
    # Get list of all assignments for the courses
    assignments += get_all_course_assignments( course_id )
    assignments = [ (a[ 'id' ], a[ 'name' ].strip()) for a in assignments ]

    # If we we're passed an activity_inviting_to_complete, filter the assignments
    assignments = [a for a in assignments if InitialWork.is_activity_type(a[1])]

    assignments = [{ 'term': term,
                     'course_id': course_id,
                     'id': a[0],
                     'unit_number' : int(a[1].split(':')[0].split(" ")[1])
                     } for a in assignments]
    return assignments


def get_all_review_assigns_for_class(course_id, term):
    assignments = [ ]
    # Get list of all assignments for the course
    assignments += get_all_course_assignments( course_id )
    assignments = [ (a[ 'id' ], a[ 'name' ].strip()) for a in assignments ]

    # If we we're passed an activity_inviting_to_complete, filter the assignments
    assignments = [a for a in assignments if Review.is_activity_type(a[1]) or MetaReview.is_activity_type(a[1])]

    assignments = [{ 'term': term,
                 'course_id': course_id,
                 'id': a[0],
                 'unit_number' : int(a[1].split(':')[0].split(" ")[1])
                 } for a in assignments]
    return assignments




def store_course_journals(course_id, term, start_week=None):
    """
    Downloads and saves journals
    """
    # may want to run later with True so can look at uses of I/me for depression
    course = env.CONFIG.canvas.get_course(course_id)
    journals = get_all_journal_assigns_for_class(course_id, term)
    filename_maker = JournalFiles()
    cleaner = TextCleaner()
    for j in journals:
        # doing first so won't waste time
        fp = filename_maker.make_content_filepath(**j )
        # make_content_filepath( **j, )
        print(fp)
        if start_week is not None and j['week_num'] < start_week:
            pass

        else:
            # Download submissions
            assignment = course.get_assignment(j['id'])
            print("Downloading {} {}".format(j['term'], j['week_num']))
            subRepo = SubmissionRepository(assignment)
            print("{} journals downloaded".format(len(subRepo.data)))

            j['content'] =[{'sid': d.user_id, 'body': cleaner.clean(d.body)} for d in subRepo.data if d.body is not None]

            with open(fp, 'w') as f:
                json.dump(j, f)



def store_course_essays( course_id, term, start_unit=None ):
    """
    Downloads and saves essays
    """
    course = env.CONFIG.canvas.get_course(course_id)
    essays = get_all_essay_assigns_for_class(course_id, term)
    print(f'downloaded {len(essays)} essays')
    filename_maker = EssayFiles()
    cleaner = TextCleaner()
    for j in essays:
        # doing first so won't waste time
        fp = filename_maker.make_content_filepath(**j )
        # make_content_filepath( **j, )
        print(fp)
        if start_unit is not None and j[ 'unit_number' ] < start_unit:
            pass

        else:
            # Download submissions
            assignment = course.get_assignment(j['id'])
            print("Downloading {} {}".format(j['term'], j['unit_number']))
            subRepo = SubmissionRepository(assignment)
            print("{} essays downloaded".format(len(subRepo.data)))

            j['content'] =[{'sid': d.user_id, 'body': cleaner.clean(d.body)} for d in subRepo.data if d.body is not None]

            #dev HACK!!!! Used to download data for a single course / unit
            # return j

            with open(fp, 'w') as f:
                json.dump(j, f)


def store_course_reviews(course_id, term, start_unit=None):
    course = env.CONFIG.canvas.get_course(course_id)
    reviews = get_all_review_assigns_for_class(course_id, term)
    print(f'downloaded {len(reviews)} reviews')
    filename_maker = ReviewFiles()
    cleaner = TextCleaner()


    for j in reviews:
        # doing first so won't waste time
        fp = filename_maker.make_content_filepath(**j )
        # make_content_filepath( **j, )
        print(fp)
        if start_unit is not None and j[ 'unit_number' ] < start_unit:
            pass
    
        else:
            # Download submissions

            quiz = course.get_assignment(j['id'])

            # Filter previously graded
            # self.subRepo.data = [ s for s in self.subRepo.data if s.workflow_state != 'complete' ]


            # quiz = course.get_quiz(j['id'])
            print("Downloading {} {}".format(j['term'], j['unit_number']))
            repo = WorkRepositoryLoaderFactory.make( course=course,
                                                              activity=quiz,
                                                              rest_timeout=30 )
            # subRepo = QuizSubmissionRepository(quiz)
            print("{} reviews downloaded".format(len(repo.data)))

            # If this is a quiz type assignment, we need to get the quiz submission objects
            # not the regular submission object so we can use them for uploading
            # qsubs = [ s for s in self.quiz.get_submissions() ]

            # return workRepo.data
    
            j['content'] =[{'sid': d.user_id, 'body': cleaner.clean(d.body)} for d in repo.data if d.body is not None]
    
            #dev HACK!!!! Used to download data for a single course / unit
            return j
    
            with open(fp, 'w') as f:
                json.dump(j, f)


if __name__ == '__main__':
    pass