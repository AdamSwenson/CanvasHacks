"""
Created by adam on 12/24/19
"""
__author__ = 'adam'

from faker import Faker

from CanvasHacks.Models.message_queue import MessageQueueItem

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


def message_queue_item_factory(activity_id=None, student_id=None):
    activity_id = fake.random_int() if activity_id is None else activity_id
    student_id = fake.random_int() if student_id is None else student_id

    return MessageQueueItem(activity_id=activity_id, student_id=student_id, subject=fake.text(),
                            body=fake.text())


if __name__ == '__main__':
    pass
