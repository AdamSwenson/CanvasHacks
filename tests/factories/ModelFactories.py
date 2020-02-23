"""
Created by adam on 12/24/19
"""
__author__ = 'adam'

from faker import Faker

fake = Faker()

import random

import pandas as pd


from CanvasHacks.Models.student import Student


def student_factory():
    name = "{}, {}".format(fake.last_name(), fake.first_name())
    s = Student(student_id=random.randint( 11111, 999999 ), name=name)
    s.sortable_name=name
    return s



if __name__ == '__main__':
    pass
