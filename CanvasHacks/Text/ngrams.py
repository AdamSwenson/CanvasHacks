"""
Created by adam on 4/11/20
"""
__author__ = 'adam'

"""
Previously in TextProcessingTools
Created by adam on 11/11/15
"""
__author__ = 'adam'

import nltk

# This idiom is necessary. See https://github.com/nltk/nltk/issues/1516
from nltk.metrics import association



class NgramError(BaseException):
    def __init__(self, processing_step):
        """
        Arguments:
            :param processing_step: String description of where error arose
        :return:
        """
        super().__init__()
        self.kind = 'NgramProcessing'
        self.identifier_type = 'String content'
        self.step = processing_step
#         ProcessingError.__init__(self, processing_step)

class NgramGetter(object):
    """
    Abstract parent class for extracting ngrams.

    Attributes:
        collocation_finder: One of the nltk's collocation finder tools (e.g., BigramCollocationFinder)
        top_likelihood_ratio:
        measurement_tool: One of nltk's measurement tools (e.g., nltk.collocations.BigramAssocMeasures)
        modifiers: IModifier instantiating tool for modifying the text before calculating ngrams
        ngrams: List of ngrams
        raw_freq: Frequency distribution of ngrams
        sorted_ngrams: List of tuples sorted by self.scored_ngrams
        top_pmi: Variable number of n-grams with the highest Pointwise Mutual Information (i.e., which occur together
        more often than would be expected)
        word_bag: List of text to run
    """

    def __init__(self):
        self.modifiers = []
        self.ngram_filters = []
        self.word_bag = []
        self.ngrams = []
        if not self.measurement_tool:
            raise NotImplementedError

    def add_modifier(self, iModifier):
        # assert(isinstance(iModifier, IModifier))
        self.modifiers.append(iModifier)

    def _run_modifiers(self):
        """
        Calls the modifiers in sequence and stores the results back in word_bag
        """
        for modifier in self.modifiers:
            self.word_bag = [modifier.process(w) for w in self.word_bag]

    def add_filter(self, iNgramFilter):
        """
        Adds a filter to be run after the ngrams are created
        :param iNgramFilter:
        :return:
        """
        self.ngram_filters.append(iNgramFilter)

    def apply_filters(self):
        for ftr in self.ngram_filters:
            self.collocation_finder.apply_ngram_filter(ftr)

    def process(self, word_bag, min_freq=3, get_top=10, **kwargs):
        """
        Runs any modifiers (stemmers, lemmatizers, etc) on the list of terms and
        then extracts the ngrams

        Args:
            get_top: The cut off for ngrams to get stats for
            min_freq: Integer of minimum number of appearances of ngram to extract
            word_bag: List of strings to extract ngrams from. Should already be filtered.
        """
        raise NotImplementedError

    def _calculate_statistics(self, get_top=10, **kwargs):
        """
                A number of measures are available to score collocations or other associations.
        The arguments to measure functions are marginals of a contingency table,
        in the bigram case (n_ii, (n_ix, n_xi), n_xx):
                w1    ~w1
             ------ ------
         w2 | n_ii | n_oi | = n_xi
             ------ ------
        ~w2 | n_io | n_oo |
             ------ ------
             = n_ix        TOTAL = n_xx
        We test their calculation using some known values presented
        in Manning and Schutze's text and other papers.
        Student's t: examples from Manning and Schutze 5.3.2
        Arguments:
            get_top: The cut off for ngrams to get stats for
        """
        self.topPMI = self.collocation_finder.nbest(self.measurement_tool.pmi, get_top)
        self.raw_freq = self.collocation_finder.score_ngrams(self.measurement_tool.raw_freq)
        self.sorted_ngrams = [ngram for ngram, score in self.raw_freq]
        self.top_likelihood_ratio = self.collocation_finder.nbest(self.measurement_tool.likelihood_ratio, get_top)


class BigramGetter(NgramGetter):
    """
    Extracts 2-grams from a word bag and calculates statistics
    Attributes:
        top_pmi: Variable number of n-grams with the highest Pointwise Mutual Information (i.e., which occur together more often than would be expected)
        top_likelihood_ratio:
        raw_freq: Frequency distribution of ngrams
        sorted_ngrams: List of tuples sorted by self.scored_ngrams
    """

    def __init__(self):
        self.measurement_tool = association.BigramAssocMeasures()
        NgramGetter.__init__(self)

    def process(self, word_bag, min_freq=3, get_top=10, **kwargs):
        """
        Arguments:
            word_bag: List of strings
        """
        assert(isinstance(word_bag, list))
        self.collocation_finder = nltk.collocations.BigramCollocationFinder.from_words(word_bag)
        self.collocation_finder.apply_freq_filter(min_freq)
        self._calculate_statistics(get_top)

class TrigramGetter(NgramGetter):
    """
        Extracts 3-grams from a word bag and calculates statistics
    """

    def __init__(self):
        self.measurement_tool = association.TrigramAssocMeasures()
        NgramGetter.__init__(self)

    def process(self, word_bag, min_freq=3, get_top=10, **kwargs):
        """
        Arguments:
            word_bag: List of strings
        """
        assert(isinstance(word_bag, list))
        #         try:
        self._run_modifiers()
        self.collocation_finder = nltk.collocations.TrigramCollocationFinder.from_words(word_bag)
        self.collocation_finder.apply_freq_filter(min_freq)
        self._calculate_statistics(get_top)

if __name__ == '__main__':
    pass