"""
Created by adam on 10/26/18
"""
__author__ = 'adam'

from CanvasHacks.JournalsFileTools import load_words_to_ignore

def filter_out_terms(combined):
    """Loads the strings to ignore from IGNORE_FILE and returns the filtered wordbag"""
    exclude = load_words_to_ignore()
    #     exclude = ['/p','style=', 'br', '“', 'ethics', '”', 'm','’','p', 'picture-uploaded', 'div', '/div',
    #               '305', 'september', '2018', 'text-align', 'class=', 'span', 'swenson', 'phil', 'philosophy',
    #                '-webkit-standard', 'font', 'face='
    #               ]
    exclude += [ "%s" % i for i in range(0,10)]
    #     print(exclude)

    for k in combined.keys():
        combined[k] = [w for w in combined[k] if w not in exclude]
    return combined


if __name__ == '__main__':
    pass