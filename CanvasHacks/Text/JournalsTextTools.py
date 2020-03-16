"""
Created by adam on 10/26/18
"""
__author__ = 'adam'

from CanvasHacks.Files.JournalsFileTools import load_words_to_ignore


def filter_out_terms(bag, exclude=[]):
    """ Applies exclude list and other filters to the wordbag"""
    if len(exclude) == 0:
        exclude = load_words_to_ignore()

    exclude += [ "%s" % i for i in range(0,1000)]
    exclude += ['none']
    #     print(exclude)
    return [w for w in bag if w not in exclude]


# test
# t = ['none', 'a']
# assert(filter_out_terms(t, ['a']) == [])

if __name__ == '__main__':
    pass