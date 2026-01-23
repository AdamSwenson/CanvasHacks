"""
Created by adam on 12/24/19
"""
__author__ = 'adam'

from faker import Faker

from CanvasHacks.Models.message_queue import MessageQueueItem
import datetime

fake = Faker()

import random

import pandas as pd

from CanvasHacks.Models.student import Student


def student_factory():
    name = "{}, {}".format(fake.last_name(), fake.first_name())
    s = Student(student_id=random.randint(11111, 999999), name=name)
    s.sortable_name = name
    return s


def make_students(number):
    """
    Creates a list of student object
    :param number: How many to create
    :return:
    """
    return [student_factory() for _ in range(0, number)]


def message_queue_item_factory(activity_id=None, student_id=None, id=None, created_at=None):
    activity_id = fake.random_int() if activity_id is None else activity_id
    student_id = fake.random_int() if student_id is None else student_id
    id = fake.random_int() if id is None else id
    status_repos = [{'type': 'FeedbackStatusRepository',
                     'activity_id': activity_id,
                     'review_pairings_activity_id': fake.random_int()
                     },
                    {'type': 'InvitationStatusRepository', 'activity_id': activity_id}]
    created_at = fake.date_time() if created_at is None else created_at

    return MessageQueueItem(id=id, activity_id=activity_id, student_id=student_id, subject=fake.text(),
                            body=fake.text(), status_repos=status_repos, created_at=created_at)


if __name__ == '__main__':
    pass
