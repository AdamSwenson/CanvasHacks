"""
Created by adam on 12/24/19
"""
__author__ = 'adam'

from faker import Faker

fake = Faker()

import random

import pandas as pd


from CanvasHacks.Models.Student import Student


def student_factory():
    return Student(fake.isbn10(), name=fake.name())



if __name__ == '__main__':
    pass
