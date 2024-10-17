"""
Created by adam on 4/23/20
"""
__author__ = 'adam'
import json
from CanvasHacks.Assessment.files import JournalFiles, EssayFiles
from CanvasHacks.Text.process import WordbagMaker


def process_journal_entries( journal_entries, existing=[ ] ):
    """
    Tokenizes and lightly filters a list of journal entries
    before saving to json
    """
    filename_maker = JournalFiles()
    fp = filename_maker.make_bag_filepath( **journal_entries )
    # fp = make_bag_filepath( **journal_entries )
    print( fp )

    if fp not in existing:
        bagmaker = WordbagMaker( keep_stopwords=True )

        if len( journal_entries[ 'content' ] ) > 0:
            for entry in journal_entries[ 'content' ]:
                #                 print(entry)
                if len( entry[ 'body' ] ) > 0:
                    entry[ 'bag' ] = bagmaker.process( entry[ 'body' ] )

        with open( fp, 'w' ) as f:
            json.dump( journal_entries, f )

    return journal_entries


def process_essay_entries( essay_entries, existing=[ ] ):
    """
    Tokenizes and lightly filters a list of journal entries
    before saving to json
    """
    filename_maker = EssayFiles()
    fp = filename_maker.make_bag_filepath( **essay_entries )
    # fp = make_bag_filepath( **journal_entries )
    print( fp )

    if fp not in existing:
        bagmaker = WordbagMaker( keep_stopwords=True )

        if len( essay_entries[ 'content' ] ) > 0:
            for entry in essay_entries[ 'content' ]:
                #                 print(entry)
                if len( entry[ 'body' ] ) > 0:
                    entry[ 'bag' ] = bagmaker.process( entry[ 'body' ] )

        with open( fp, 'w' ) as f:
            json.dump( essay_entries, f )

    return essay_entries
if __name__ == '__main__':
    pass