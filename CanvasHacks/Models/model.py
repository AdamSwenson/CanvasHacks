"""
Created by adam on 12/24/19
"""
__author__ = 'adam'


class Model(object):
    """Parent class of all model objects"""

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
    #
    # for k in kwargs.keys():
    #         # print(k, kwargs[k])
    #         setattr(self, k,  kwargs[k])


if __name__ == '__main__':
    pass


class StoreMixin( object ):

    def handle_kwargs( self, kwargs ):
        for key, value in kwargs.items():
            setattr(self, key, value)
