"""
Created by adam on 3/13/20
"""
__author__ = 'adam'

import datetime
import os

import pandas as pd
from IPython.display import HTML, Latex
from IPython.display import display

import CanvasHacks.environment as env
from CanvasHacks.Repositories.overview import DiscussionOverviewRepository, SkaaOverviewRepository

if __name__ == '__main__':
    pass

SKAA_ORDER = [ 'student', 'reviewing', 'reviewed_by', 'invited_to_review',
               'received_feedback_on_essay', 'invited_to_metareview',
               'received_feedback_on_review', 'canvas_id', 'csun_id', 'reviewing_id', 'reviewed_by_id' ]

DISCUSSION_ORDER = [ 'student', 'reviewing', 'reviewed_by', 'invited_to_discussion_review',
                     'received_discussion_feedback', 'canvas_id', 'csun_id', 'reviewing_id', 'reviewed_by_id' ]


class ControlStore:
    stats_template = """
    <div class='unit-stats'>
        <h2>Unit {unit_number}</h2>
        <div class='skaa'>
        <h3>SKAA</h3>
            <h4>Essay</h4>
            <p><strong>    Submitted essay</strong>: {essay}</p>
            <p><strong>    Did not submit essay</strong>: {no_essay}</p>
            
            <h4>Review</h4>
            <p><strong>    Reviewer submitted</strong>: {skaa_review}</p>
            <p><strong>    Reviewer has not submitted</strong>: {skaa_no_review}</p>
            
            <h4>Metareview (including blocked)</h4>
            <p><strong>    Author submitted</strong>: {skaa_metareview}</p>
            <p><strong>    Author has not submitted</strong>: {skaa_no_metareview}</p>
        </div>
        
        <div class='discussion'>    
        <h3>Discussion</h3>
            <p><strong>    Posted required amount:</strong> {posts}</p>
            <p><strong>    Has not reached post trigger amount:</strong> {no_posts}</p>
            <p><strong>    Reviewer has not submitted:</strong> {discussion_no_review} </p>
        </div>
    </div>
    """

    incomplete_tables_template = """
    <div class='unit-tables-incomplete'>
        <h2>Unit {unit_number}</h2>
        <h3>SKAA</h3>
            <h4>Did not submit essay</h4>
                {no_essay}
            <h4>Reviewer has not submitted</h4>
                {skaa_no_review}
            <h4>Metareview has not submitted (including blocked)</h4>
                {skaa_no_metareview}

        <h3>Discussion</h3>
            <h4>Has not reached post trigger amount</h4>
                {no_posts}
            <h4>Reviewer has not submitted </h4>
                {discussion_no_review}
    </div>
    """

    complete_tables_template = """
    <div class='unit-tables-complete'>
        <h2>Unit {unit_number}</h2>
        <h3>SKAA</h3>
            <h4>Submitted essay</h4>
                {essay}
            <h4>Reviewer has submitted</h4>
                {skaa_review}

        <h3>Discussion</h3>
            <h4>Has reached post trigger amount</h4>
                {posts}
            <h4>Reviewer has submitted </h4>
                {discussion_review}
    </div>
    """

    def __init__( self ):

        self.skaa_dashboards = { }
        self.discussion_dashboards = { }

        self.skaa_repos = { }
        self.discussion_repos = { }

        # Stores all steps which have been run
        self._completed_steps = [ ]

        self.units = { }

    @property
    def completed_steps( self ):
        return self._completed_steps

    @completed_steps.setter
    def completed_steps( self, steps ):
        if isinstance( steps, list ):
            self._completed_steps.extend( steps )
        self._completed_steps.append( steps )

    @property
    def skaa_repo( self ):
        """For backwards compatibility"""
        return self.skaa_overview_repo

    def _initialize_unit_obj( self, unit_number, course=env.CONFIG.course ):
        """Retrieves all assignments etc and creates a Unit
        object. Replaces existing unit object if there was one"""

        # As of CAN-68 we use the method which will check if the object
        # is already stored to save calls to the api
        unit = env.CONFIG.set_unit( unit_number )
        # unit = Unit( course, unit_number )
        self.units[ unit_number ] = unit
        return unit

    def load_unit( self, unit ):
        if isinstance( unit, int ):
            # Load the unit definition if was given a number
            unit = self._initialize_unit_obj( unit )

        # initialize and store overview repos
        skaa_overview_repo = SkaaOverviewRepository()
        skaa_overview_repo.load( unit )
        self.skaa_repos[ unit.unit_number ] = skaa_overview_repo

        disc_overview_repo = DiscussionOverviewRepository()
        disc_overview_repo.load( unit )
        self.discussion_repos[ unit.unit_number ] = disc_overview_repo

        # initialize and store dashboards
        self.skaa_dashboards[ unit.unit_number ] = SkaaDashboard( skaa_overview_repo )
        self.discussion_dashboards[ unit.unit_number ] = DiscussionDashboard( disc_overview_repo )

    @property
    def unit_numbers( self ):
        k = [ uk for uk in self.units.keys() ]
        k.sort()
        return k

    def _display( self, out, latex=False ):
        # Display all of them
        if latex:
            out = Latex( out )
        else:
            out = HTML( out )

        display( out )

    def _get_unit_run_data( self, unit_number ):
        try:
            return {

                    'unit_number': unit_number,

                    'essay': len( self.skaa_dashboards[ unit_number ].essay ),
                    'no_essay': len( self.skaa_dashboards[ unit_number ].no_essay ),

                    'skaa_review': len( self.skaa_dashboards[ unit_number ].reviewed ),
                    'skaa_no_review': len( self.skaa_dashboards[ unit_number ].non_reviewed ),

                    'skaa_metareview': len( self.skaa_dashboards[ unit_number ].metareviewed ),
                    'skaa_no_metareview': len( self.skaa_dashboards[ unit_number ].non_metareviewed ),

                    'posts': len( self.discussion_dashboards[ unit_number ].posters ),
                    'no_posts': len( self.discussion_dashboards[ unit_number ].non_posters ),
                    'discussion_no_review': len( self.discussion_dashboards[ unit_number ].non_reviewed ),
            }
        except (TypeError, AttributeError) as e:
            # we will likely hit this if there is no data yet
            # for the unit requested. Since we don't want to take down the whole
            # operation, we just print the error
            print(e)

    def run_data( self, run_timestamp: datetime.datetime.timestamp = None ):
        """
        Returns a list containing dictionaries of stats for each unit
        :type run_timestamp: Will use current time if None
        :return:
        """
        if run_timestamp is None:
            run_timestamp = datetime.datetime.now()

        d = [ ]
        for u in self.unit_numbers:
            try:
                dt = self._get_unit_run_data( u )
                dt[ 'ran_at' ] = run_timestamp
                d.append( dt )
            except (TypeError, AttributeError):
                pass

        return d

    def save_run_data( self, file_path=env.RUN_DATA_LOG_PATH, run_timestamp: datetime.datetime.timestamp = None ):
        try:
            d = self.run_data( run_timestamp=run_timestamp )
            d = pd.DataFrame( d )
            d.ran_at = pd.to_datetime( d.ran_at )

            try:
                # Instead of appending to the csv file which was causing
                # errors, we read it in and then overwrite it
                # switched to using xlsx instead of csv because of
                # errors with alignment and dates
                existing = pd.read_excel( file_path )
                d = pd.concat( [ d, existing ] )
            except FileNotFoundError:
                pass

            # We check whether the file already exists
            # so that we don't keep writing header rows into the file
            header = not os.path.exists( file_path )

            # Append it to the csv log file
            # d.to_csv(file_path, mode='a', header=header)
            d.to_excel( file_path )
        except (TypeError, AttributeError):
            pass

    def display_stats( self, latex=False ):
        """
        Displays statistics about the assignment using html template
        :param latex:
        :return:`
        """
        assert (latex is False)

        out = [ ]

        for u in self.unit_numbers:
            try:
                if latex:
                    pass
                    # tables.append( self.skaa_dashboards[ u ].non_reviewed.to_latex( caption=label ) )

                else:

                    # default html table
                    d = self._get_unit_run_data( u )
                    # d = {
                    #     'unit_number': u,
                    #     'essay': len(self.skaa_dashboards[ u ].essay),
                    #     'no_essay': len(self.skaa_dashboards[ u ].no_essay),
                    #     'skaa_no_review': len(self.skaa_dashboards[ u ].non_reviewed),
                    #     'posts': len(self.discussion_dashboards[ u ].posters),
                    #     'no_posts': len(self.discussion_dashboards[ u ].non_posters),
                    #     'discussion_no_review': len(self.discussion_dashboards[ u ].non_reviewed),
                    # }
                    if d is not None:
                        out.append( self.stats_template.format( **d ) )
            except (TypeError, AttributeError):
                pass

        out = ' '.join( out )
        self._display( out )

    def display_incomplete_tables( self, latex=False ):
        """
        Displays students where some aspect has not been completed

        :param latex:
        :return:
        """
        tables = [ ]
        for u in self.unit_numbers:
            try:
                label = "Unit {}".format( u )
                if latex:
                    tables.append( self.skaa_dashboards[ u ].non_reviewed.to_latex( caption=label ) )

                else:

                    d = {
                        'unit_number': u
                    }
                    try:
                        d[ 'no_essay' ] = self.skaa_dashboards[ u ].no_essay.to_html(),
                        d[ 'skaa_no_review' ] = self.skaa_dashboards[ u ].non_reviewed.to_html(),
                        d[ 'skaa_no_metareview' ] = self.skaa_dashboards[ u ].non_metareviewed.to_html(),
                    except KeyError:
                        print( 'Bad skaa data' )
                        pass
                    try:
                        d[ 'no_posts' ] = self.discussion_dashboards[ u ].non_posters.to_html(),
                        d[ 'discussion_no_review' ] = self.discussion_dashboards[ u ].non_reviewed.to_html()
                    except KeyError:
                        print( 'Bad discussion data' )
                        pass

                    # Populate the table template and add to the list
                    tables.append( self.incomplete_tables_template.format( **d ) )
            except (TypeError, AttributeError):
                pass

        out = ' '.join( tables )

        self._display( out, latex=latex )

    def display_complete_tables( self, latex=False ):
        """
        Displays students where tasks have been completed.

        :param latex:
        :return:
        """
        tables = [ ]
        for u in self.unit_numbers:
            try:
                if latex:
                    label = "Unit {}".format( u )
                    tables.append( self.skaa_dashboards[ u ].reviewed.to_latex( caption=label ) )

                else:

                    d = {
                        'unit_number': u,
                        'essay': self.skaa_dashboards[ u ].essay.to_html(),
                        'skaa_review': self.skaa_dashboards[ u ].reviewed.to_html(),
                        'posts': self.discussion_dashboards[ u ].posters.to_html(),
                        'discussion_review': self.discussion_dashboards[ u ].reviewed.to_html(),
                    }

                    # Populate the table template and add to the list
                    tables.append( self.complete_tables_template.format( **d ) )
            except (TypeError, AttributeError):
                pass

        out = ' '.join( tables )

        self._display( out, latex=latex )


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
        try:
            return self.repo.non_reviewed.drop( [ 'reviewing' ], axis=1 )
        except (AttributeError, KeyError):
            return self.repo.non_reviewed

    @property
    def metareviewed( self ):
        """
        Returns the subset of students who have turned in the initial work
        whose author has turned in the metareview

        Drops the 'reviewed_by' column in results since that can be
        confusing in this context

        :return: DataFrame
        """
        try:
            return self.repo.metareviewed.drop( [ 'reviewed_by' ], axis=1 )
        except (AttributeError, KeyError):
            # This can happen when the data is empty but we still need to return something
            return self.repo.metareviewed

    @property
    def non_metareviewed( self ):
        """
        Returns the subset of students who have turned in the initial work
        but author has not turned in the metareview

        Drops the 'reviewed_by' column in results since that can be
        confusing in this context

        :return: DataFrame
        """
        try:
            return self.repo.non_metareviewed.drop( [ 'reviewed_by' ], axis=1 )
        except (AttributeError, KeyError):
            # This can happen when the data is empty but we still need to return something
            return self.repo.non_metareviewed

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

    def __init__( self, overview_repo: DiscussionOverviewRepository ):
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
        # try:
        return self.repo.posters
        # except AttributeError:
        #     return pd.DataFrame()

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
        try:
            return self.repo.non_reviewed.drop( [ 'reviewing' ], axis=1 )
        except (AttributeError, KeyError):
            # This can happen when the data is empty but we still need to return something
            return self.repo.non_reviewed

    def print_counts( self ):
        print( "\n~~~~~~~~~~~~~~~~~~~ DISCUSSION ~~~~~~~~~~~~~~~~~~~~~~~~~" )
        print( "===================== Discussion posts =====================" )
        print( "{} students have turned in posts and been paired up".format( len( self.posters ) ) )
        print( "{} students have not posted".format( len( self.non_posters ) ) )

        print( "\n===================== review =====================" )
        print( "{} students' reviewers has turned in the review".format( len( self.reviewed ) ) )
        print( "{} students have a reviewer who hasn't turned in the review".format( len( self.non_reviewed ) ) )
        print( "\n" )
