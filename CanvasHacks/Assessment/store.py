"""
Created by adam on 4/23/20
"""
__author__ = 'adam'

from collections import namedtuple

from afinn import Afinn

# A journal assignment which was done by one class on one week in one term
# Thus on one week in one term there may be multiple CourseJournals
from CanvasHacks.Assessment.files import EssayFiles, JournalFiles
from CanvasHacks.Text.process import TokenFiltrationMixin

afinn = Afinn()
import json


def load_stored_bags( file_handler ):
    """
    Loads all stored wordbags for the type of assignment
    as determined by the type of file_handler passed in.
    Returns a tuple:
        store: Holds the actual data
        terms: List of terms (e.g., 'F18')
        divs: List of week numbers (if journals) or unit numbers (if essays)
    :param file_handler:
    :return:
    """

    fiter = file_handler.make_bag_file_iterator()
    data = [ ]

    if isinstance( file_handler, EssayFiles ):
        AssignmentObj = EssayAssignment
        ComboObj = TermUnitStore
    elif isinstance( file_handler, JournalFiles ):
        AssignmentObj = JournalAssignment
        ComboObj = TermWeekStore

    try:
        while True:
            with open( next( fiter ), 'r' ) as f:
                print( f.name )
                d = json.load( f )
                o = AssignmentObj( **d )
                data.append( o )

    except StopIteration:
        print( "Loaded {} files".format( len( data ) ) )

    terms = list( set( [ e.term for e in data ] ) )

    try:
        divs = list( set( [ e.unit_number for e in data ] ) )
    except (NameError, AttributeError):
        # If operating on journals will end up here
        divs = list( set( [ e.week_num for e in data ] ) )

    stores = [ ]
    for t in terms:
        for w in divs:
            stores.append( ComboObj( t, w, data ) )

    return stores, terms, divs


CourseJournal = namedtuple( 'Week', [ 'term',
                                      # The canvas course id for the journal
                                      # 'course_id',

                                      # The canvas assignment id
                                      'id',

                                      'week_num',

                                      # A list of dictionaries containing student
                                      # journal entries.
                                      # Each dictionary has the keys:
                                      #    sid
                                      #    body: The sanitized text of the journal
                                      #    bag: List of word tokens, including stopwords
                                      'content' ] )


class SingleAssignmentStore( TokenFiltrationMixin ):
    """
    An assignment which was done by one class on one week in one term
    Thus on one week in one term there may be multiple CourseJournals
    This holds the data and handles most calculations via properties

    Attributes
        content: List of dictionaries with keys sid, body, bag
        term: String, e.g., 'S20'
        course_id: Integer
        id: The particular assignment's id
        unit_number: Integer

    """

    # id: int
    # term: str
    # content: list
    # unit_number: int
    # course_id: int

    def __init__( self, **kwargs ):
        try:
            for k, v in kwargs.items():
                setattr( self, k, v )
        except AttributeError as e:
            print( e, f"\n {k} => {v}" )
        self._fix_errors()

    #         self.token_filter = TokenFiltrationMixin()

    @property
    def bags( self ):
        """Returns a list of all the student wordbags"""
        return [ s[ 'bag' ] for s in self.content ]

    @property
    def combo_bag( self ):
        """A wordbag comprising every word submitted by students

        Removes punctuation which didn't get filtered when bag created
        """
        b = [ ]
        [ b.extend( l ) for l in self.bags ]
        # remove None type since things will be expecting a list of strings
        b = [ w for w in b if w is not None ]
        return b

    @property
    def no_stops_bag( self ):
        """A wordbag comprising every word submitted by students sans stopwords"""
        return [ self.clean_punctuation( w ) for w in self.combo_bag if
                 self.keep( w, keep_stopwords=False ) ]  # not in self.to_remove]

    @property
    def total_sentiment( self ):
        return self.calc_sentiment( self.combo_bag )

    @property
    def average_sentiment( self ):
        return self.total_sentiment / self.word_count

    @property
    def word_count( self ):
        return len( self.combo_bag )

    @property
    def num_empty( self ):
        return len( [ b for b in self.bags if len( b ) == 0 ] )

    @property
    def num_students( self ):
        return len( self.content )

    @property
    def student_sentiments( self ):
        return [ self.calc_sentiment( bag ) for bag in self.bags ]

    @property
    def student_avg_sentiments( self ):
        return [ self.calc_sentiment( bag ) / len( bag ) for bag in self.bags if len( bag ) > 0 ]

    def calc_sentiment( self, bag ):
        """
        Calculates a total sentiment score of items in the bag
        If the bag is None it will return 0 to avoid
        having to do type checking elsewhere. This should be fine since we
        only care about sentiment score sums
        """
        try:
            txt = ' '.join( bag )
            return afinn.score( txt )
        except TypeError as e:
            print( e )
            return 0

    def _fix_errors( self ):
        try:
            for c in self.content:
                # Not sure why but one entry from f19 has no bag.
                # maybe was the instructor or test student
                if 'bag' not in c.keys():
                    c[ 'bag' ] = [ ]
        except AttributeError as e:
            # sometimes we want to load an empty object
            # which will not have a content attribute
            print( e )


class JournalAssignment( SingleAssignmentStore ):
    """
    Journal specific version
    """

    # @property
    # def week_num( self ):
    #     return self.week

    @property
    def week_number( self ):
        return self.week


class EssayAssignment( SingleAssignmentStore ):
    """
    Essay specific
    """

    @property
    def unit_num( self ):
        return self.unit

    # @property
    # def unit_number( self ):
    #     return self.unit


class TermWeekStore( TokenFiltrationMixin ):
    """Represents a particular week in a particular term
    Handles combining multiple classes into one data store
    """

    def __init__( self, term, week, all_assigns ):
        self.term = term
        self.week = week
        self.data = [ d for d in all_assigns if d.term == self.term and d.week_num == self.week ]

    #             print(len(week_journals))
    #         self.token_filter = TokenFiltrationMixin()

    @property
    def bags( self ):
        """Returns a list of all the student wordbags"""
        b = [ ]
        [ b.extend( g.bags ) for g in self.data ]
        return b

    #         return [ b for b in j.bags for j in self.journals]

    @property
    def combo_bag( self ):
        """A wordbag comprising every word submitted by students """
        b = [ ]
        [ b.extend( l ) for l in self.bags ]
        return b

    @property
    def no_stops_bag( self ):
        """A wordbag comprising every word submitted by students sans stopwords"""
        if len( self.combo_bag ) == 0 :
            return [ ]

        return [ self.clean_punctuation( w ) for w in self.combo_bag if
                 self.keep( w, keep_stopwords=False ) ]  # not in self.to_remove]

    @property
    def total_sentiment( self ):
        return self.calc_sentiment( self.combo_bag )

    @property
    def average_sentiment( self ):
        return self.total_sentiment / self.word_count

    @property
    def word_count( self ):
        return len( self.combo_bag )

    @property
    def week_num( self ):
        return self.week


class TermUnitStore( TokenFiltrationMixin ):
    """Represents a particular unit in a particular term
    Handles combining multiple classes into one data store
    """

    def __init__( self, term, unit, all_assigns ):
        self.term = term
        self.unit = unit
        self.data = [ d for d in all_assigns if d.term == self.term and d.unit_number == self.unit ]

    #             print(len(week_journals))
    #         self.token_filter = TokenFiltrationMixin()

    @property
    def bags( self ):
        """Returns a list of all the student wordbags"""
        b = [ ]
        [ b.extend( g.bags ) for g in self.data ]
        return b

    @property
    def combo_bag( self ):
        """A wordbag comprising every word submitted by students """
        b = [ ]
        [ b.extend( l ) for l in self.bags ]
        return b

    @property
    def no_stops_bag( self ):
        """A wordbag comprising every word submitted by students sans stopwords"""
        return [ self.clean_punctuation( w ) for w in self.combo_bag if
                 self.keep( w, keep_stopwords=False ) ]  # not in self.to_remove]

    @property
    def total_sentiment( self ):
        return self.calc_sentiment( self.combo_bag )

    @property
    def average_sentiment( self ):
        return self.total_sentiment / self.word_count

    @property
    def word_count( self ):
        return len( self.combo_bag )

    @property
    def bag_word_counts( self ):
        return [ len( b ) for b in self.bags ]

    @property
    def unit_num( self ):
        return self.unit


if __name__ == '__main__':
    pass
