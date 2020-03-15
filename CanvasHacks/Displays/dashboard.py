"""
Created by adam on 3/13/20
"""
__author__ = 'adam'

from CanvasHacks.Repositories.overview import SkaaOverviewRepository

if __name__ == '__main__':
    pass

SKAA_ORDER = [ 'student', 'reviewing', 'reviewed_by', 'invited_to_review',
               'received_feedback_on_essay', 'invited_to_metareview',
               'received_feedback_on_review', 'canvas_id', 'csun_id', 'reviewing_id', 'reviewed_by_id' ]

DISCUSSION_ORDER = [ 'student', 'reviewing', 'reviewed_by', 'invited_to_discussion_review',
                     'received_discussion_feedback', 'canvas_id', 'csun_id', 'reviewing_id', 'reviewed_by_id' ]


class SkaaDashboard:
    """
    This is in charge of displaying information from the
    skaa overview repo
    """

    def __init__( self, overview_repo: SkaaOverviewRepository ):
        self.repo = overview_repo

    @property
    def data( self ):
        return self.repo.data[ SKAA_ORDER ]

    @property
    def essay( self ):
        """
        Return students who have done initial work and been assigned a reviewer

        :return: DataFrame
        """
        return self.repo.essay

    @property
    def no_essay( self ):
        """
        Students who have not submitted the initial work
        :return: DataFrame
        """
        return self.repo.no_essay

    @property
    def reviewed( self ):
        """
        Returns the subset of students who have turned in the initial work
        whose reviewer has turned in the review

        :return: DataFrame
        """
        return self.repo.reviewed

    @property
    def non_reviewed( self ):
        """
        Returns the subset of students who have turned in the initial work
        whose reviewer has NOT turned in the review

        Drops the 'reviewing' column in results since that can be
        confusing in this context
        :return: DataFrame
        """
        return self.repo.non_reviewed.drop( [ 'reviewing' ], axis=1 )

    @property
    def metareviewed( self ):
        """
        Returns the subset of students who have turned in the initial work
        whose author has turned in the metareview

        Drops the 'reviewed_by' column in results since that can be
        confusing in this context

        :return: DataFrame
        """
        return self.repo.metareviewed.drop( [ 'reviewed_by' ], axis=1 )

    @property
    def non_metareviewed( self ):
        """
        Returns the subset of students who have turned in the initial work
        whose author has turned in the metareview

        Drops the 'reviewed_by' column in results since that can be
        confusing in this context

        :return: DataFrame
        """
        return self.repo.non_metareviewed.drop( [ 'reviewed_by' ], axis=1 )

    def print_counts( self ):
        print( "\n~~~~~~~~~~~~~~~~~~~~~ SKAA ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~" )
        print( "===================== initial work =====================" )
        print( "{} students have turned in essay and been paired up".format( len( self.essay ) ) )
        print( "{} students haven't turned in essay".format( len( self.no_essay ) ) )

        print( "\n===================== review =====================" )
        print( "{} students' reviewers has turned in the review".format( len( self.reviewed ) ) )
        print( "{} students have a reviewer who hasn't turned in the review".format( len( self.non_reviewed ) ) )

        print( "\n===================== metareview =====================" )
        print( "{} students' authors have turned in the metareview".format( len( self.metareviewed ) ) )
        print( "{} students' authors haven't turned in the metareview".format( len( self.non_metareviewed ) ) )
        print( "\n" )


class DiscussionDashboard:
    """
    This is in charge of displaying information from the
    discussion overview repository

    """

    def __init__( self, overview_repo ):
        self.repo = overview_repo

    @property
    def data( self ):
        return self.repo.data[ DISCUSSION_ORDER ]

    @property
    def posters( self ):
        """
        Students who have posted and been assigned reviewers
        :return: DataFrame
        """
        return self.repo.posters

    @property
    def non_posters( self ):
        """
        Students who have not posted and thus not been assigned a reviewer
        :return: DataFrame
        """
        return self.repo.non_posters

    @property
    def reviewed( self ):
        return self.repo.reviewed

    @property
    def non_reviewed( self ):
        """
        Returns students whose reviewer hasn't turned in the review.

        Drops the reviewing column to avoid confusion
        :return:
        """
        return self.repo.non_reviewed.drop( [ 'reviewing' ], axis=1 )

    def print_counts( self ):
        print( "\n~~~~~~~~~~~~~~~~~~~ DISCUSSION ~~~~~~~~~~~~~~~~~~~~~~~~~" )
        print( "===================== Discussion posts =====================" )
        print( "{} students have turned in posts and been paired up".format( len( self.posters ) ) )
        print( "{} students have not posted".format( len( self.non_posters ) ) )

        print( "\n===================== review =====================" )
        print( "{} students' reviewers has turned in the review".format( len( self.reviewed ) ) )
        print( "{} students have a reviewer who hasn't turned in the review".format( len( self.non_reviewed ) ) )
        print( "\n" )
