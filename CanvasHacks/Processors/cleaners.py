"""
Created by adam on 3/11/20
"""
__author__ = 'adam'

from bs4 import BeautifulSoup

from CanvasHacks.Models.model import StoreMixin
import re

if __name__ == '__main__':
    pass


class ICleaner:
    @staticmethod
    def clean( content ):
        raise NotImplementedError


class UtfCleaner( ICleaner ):

    @staticmethod
    def clean( content ):
        single_char_to_remove = [
            '°',
            'ç',
            'ï',
            '¬', '†',
            "Ä", "ô"  # , "s"
        ]
        multi_char_to_remove = [
            "\xa0"
        ]
        chars = single_char_to_remove + multi_char_to_remove
        rx = r'{}'.format("|".join(chars))
        content = re.sub( rx, '', content )

        # Dealing with single first to reduce time for next step
        # content = "".join( [ c for c in content if c not in single_char_to_remove ] )
        # return str( content )  # .encode('utf-8').decode()
        #
        # for c in multi_char_to_remove:
        #     content = re.sub(c, '', content)
        return content


class HtmlCleaner( ICleaner ):

    @staticmethod
    def clean( content ):
        soup = BeautifulSoup( content, features="lxml" )
        return soup.text


class TextCleaner( StoreMixin ):
    cleaners = [
        UtfCleaner,
        HtmlCleaner
    ]

    def __init__( self, **kwargs ):
        self.handle_kwargs( **kwargs )

    def clean( self, content ):
        if not isinstance(content, str):
            # This is a text cleaner. If we haven't received
            # text, we just send it back
            return content

        try:
            for cleaner in self.cleaners:
                content = cleaner.clean( content )
            return content
        except Exception as e:
            print( 'Text Cleaner Error', e, content )
