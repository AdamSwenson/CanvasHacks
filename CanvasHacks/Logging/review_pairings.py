"""
Created by adam on 2/25/20
"""
import datetime

import pandas as pd

from CanvasHacks import environment as env
from CanvasHacks.TimeTools import getDateForMakingFileName

__author__ = 'adam'

if __name__ == '__main__':
    pass


def make_review_audit_file(associationRepo, studentRepo, unit):
    """Stores all review assignments to a csv file
    for easier auditing
    """
    d = associationRepo.audit_frame(studentRepo)
    d['timestamp'] = datetime.datetime.now().isoformat()

    fp = "{}/{}-Unit{}-peer review assignments.csv".format(env.LOG_FOLDER, getDateForMakingFileName(), unit.unit_number )
    d.to_csv(fp)
    print("Audit file saved to {}".format(fp))

    #
    # # Make audit file
    # review_audit = []
    # for rev in associationRepo.get_associations(unit.review):
    #     print(rev.assessor_id, rev.assessee_id)
    #     assessor = studentRepo.get_student_record( rev.assessor_id )
    #     assessee = studentRepo.get_student_record( rev.assessee_id )
    #     print(assessor)
    #
    #     review_audit.append({
    #         'activity_inviting_to_complete' : unit.review.name,
    #         'assessor_name' : assessor.short_name,
    #         'assessor_sis_id': assessor.sis_user_id,
    #         'assessor_canvas_id': assessor.id,
    #         'assessee_name' : assessee.short_name,
    #         'assessee_sis_id': assessee.sis_user_id,
    #         'assessee_canvas_id': assessee.id,
    #         'timestamp': datetime.datetime.now().isoformat()
    #     })
    #
    # review_audit = pd.DataFrame(review_audit)

