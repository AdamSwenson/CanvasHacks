"""
Created by adam on 1/29/19
"""
__author__ = 'adam'


def determine_credit(submissions):
    """Adds submissions of zero length to the no-credit list.
    Adds others to the credit list.
    Returns a dictionary with keys credit and nocredit, with the lists as values
    """
    credit = []
    nocredit = []

    for s in submissions:
        if 'body' in s.keys() and s['body'] is not None and len(s['body']) > 2:
            credit.append(s['student_id'])
        else:
            nocredit.append(s['student_id'])

    return {'credit': credit, 'nocredit': nocredit}


if __name__ == '__main__':
    pass