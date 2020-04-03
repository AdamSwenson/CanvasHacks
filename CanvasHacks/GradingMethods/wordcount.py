"""
Created by adam on 3/15/20
"""
__author__ = 'adam'


from CanvasHacks.GradingMethods.base import IGradingMethod
from CanvasHacks.Processors.cleaners import TextCleaner
from CanvasHacks.Text.stats import WordCount

if __name__ == '__main__':
    pass


def make_pct_required_count_thresholds( required_count, step=10 ):
    return [
        { 'min_count': round( required_count * pct * 0.01 ), 'pct_credit': round( pct * 0.01 ) } for pct in
        range( 0, 100, step ) ]


class GradeByWordCount( IGradingMethod):

    def __init__( self, threshold_dicts=[ ], required_count=None, pct_of_score=1, count_stopwords=True ):
        """
        Count dict defines the thresholds via wordcounts
        and percentage of total. Should be a list like:
        [
            { count : int,
            pct_credit : float
            },
            {count : 1000,
            pct_credit: 54.3
            }
        ]
        :param threshold_dicts:
        :param count_stopwords: Whether stopwords should be included in the wordcount
        """

        self.required_count = required_count
        self.threshold_dicts = threshold_dicts
        self.count_stopwords = count_stopwords

        # Will remove html and most encoding artifacts.
        # Whatever we're calling this on, should've already
        # removed that stuff, but just to be safe
        self.cleaner = TextCleaner()

        # The object which will handle the actual processing and computation
        self.analyzer = WordCount( count_stopwords=count_stopwords )

        if self.required_count is not None and len( self.threshold_dicts ) > 0:
            self.make_pct_required_count_thresholds( self.required_count )

        self.prepare_dicts()

    def make_pct_required_count_thresholds( self, required_count, step=10 ):
        self.threshold_dicts = make_pct_required_count_thresholds(required_count, step)
        # [
        #     { 'min_count': round( required_count * pct * 0.01 ), 'pct_credit': round( pct * 0.01 ) } for pct in
        #     range( 0, 100, step ) ]
        self.prepare_dicts()
        return self.threshold_dicts

    def prepare_dicts( self ):
        # Validate and put the dicts we've received into the
        # correct order
        # if len( self.threshold_dicts ) == 0:
        #     raise InvalidGradingValuesError
        self.threshold_dicts.sort( key=lambda x: x[ 'min_count' ], reverse=True )

    def grade( self, content, **kwargs ):
        """
        Returns the pct credit as a float between 0-100
        Assumes that html and encoding artifacts have been
        separately removed

        :param content:
        :param kwargs:
        :return:
        """
        # Remove html and other artifacts
        # content = self.cleaner.clean( content )

        # Tokenize and count
        word_count = self.analyzer.analyze( content )

        # Lookup correct pct total
        for td in self.threshold_dicts:
            if word_count >= td[ 'min_count' ]:
                return td[ 'pct_credit' ]

        # if we've fallen all the way through the dicts, they
        # are below the lowest cutoff
        return 0
