"""
Defines types of activity with respect to features of
the text we'd expect
Created by adam on 2/25/20
"""
__author__ = 'adam'

class ITextType:
    """
    Parent
    """
    pass


class AuthorActivity(ITextType):
    """
    An activity where they are to discuss an author
    or authors
    """

    def __init__(self, authors):
        authors = authors if isinstance(authors, list) else [authors]
        self.authors = authors
        self.expected += self.authors





if __name__ == '__main__':
    pass