"""
Created by adam on 3/16/20
"""
__author__ = 'adam'

if __name__ == '__main__':
    pass


class IAnalyzer:
    @staticmethod
    def analyze( content, **kwargs):
        raise NotImplementedError


class NonEmpty(IAnalyzer):

    @staticmethod
    def analyze( content,  **kwargs ):

        if content is not None:
            if isinstance( content, (int, float) ):
                return True

            if len( content ) > 0:
                return True

        return False
