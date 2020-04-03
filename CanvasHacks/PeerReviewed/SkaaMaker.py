"""
Creates all the assignments in a unit
Created by adam on 3/1/20
"""
__author__ = 'adam'

import pandas as pd

import CanvasHacks.environment as env
from CanvasHacks.Models.model import StoreMixin
from CanvasHacks.Definitions.unit import Unit

LOC = '{}/Box Sync/TEACHING/Phil 305 Business ethics/Phil305 S20'.format(
    env.ROOT )  # placeholder for where the access codes are stored

DETAILS_FP = "{}/Unit details.xlsx".format( LOC )


class UnitDefinitionsLoader( StoreMixin ):

    def __init__( self, **kwargs ):
        self.handle_kwargs( **kwargs )

    def load( self, filepath ):
        with pd.ExcelFile( filepath ) as xls:
            self.unit_details = pd.read_excel( xls, 'details' )
            self.start_dates = pd.read_excel( xls, 'startdates' )
            # start_dates.start = start_dates.apply(lambda x: pd.Timestamp(x.start, tz='US/Pacific'), axis=1)
            self.start_dates.start = self.start_dates.apply( lambda x: pd.Timestamp( x.start ), axis=1 )

            # Clean up the text
            self.unit_details.activity_title = self.unit_details.activity_title.str.strip()

    def run( self, course ):
        for u in self.units:
            for a in u.components:
                maker = CreationHandlerFactory.make( a, course )
                # print( maker.creation_dict )
                maker.create()

    def make_unit( self, unit_number, start ):
        u = Unit( [ ], unit_number )
        for activity_type in u.component_types:
            # Holds the data we'll use to create the activity
            v = {}
            # Represents a date which gets incremented for each step
            d = start

            # Get the dates sorted out
            # Have to do this first, since the penalizer for some activities
            # will require the due date when it initializes
            deets = self.unit_details[ self.unit_details.activity_title == activity_type.title_base ]

            v[ 'unlock_at' ] = d + pd.Timedelta( '1 minutes' )
             # = unlock_at

            d += pd.Timedelta( '{} days'.format( deets.due_days_from_start.values[ 0 ] ) )
            v[ 'due_at' ] = d - pd.Timedelta( '1 minute' )
            # setattr( activity, 'due_at', due_at )
            # v[ 'due_at' ] = due_at

            d += pd.Timedelta( '{} days'.format( deets.lock_after_due.values[ 0 ] ) )
            v[ 'lock_at' ] = d - pd.Timedelta( '1 minute' )


            # Instantiate
            activity = activity_type( unit_number=u.unit_number, due_at=v[ 'due_at' ] )
            #         print(activity.title_base)
            # deets = self.unit_details[ self.unit_details.activity_title == activity.title_base ]
            #         print(deets)

            setattr( activity, 'unit_number', unit_number )

            v['title'] = activity.make_title

            # Set time values

            setattr( activity, 'unlock_at', v[ 'unlock_at' ] )
            setattr( activity, 'lock_at', v['lock_at'] )

            # unlock_at = d + pd.Timedelta( '1 minutes' )
            # v[ 'unlock_at' ] = unlock_at


            # d += pd.Timedelta( '{} days'.format( deets.lock_after_due.values[ 0 ] ) )
            # lock_at = d - pd.Timedelta( '1 minute' )
            # setattr( activity, 'lock_at', lock_at )
            # v[ 'lock_at' ] = lock_at

            # set point values
            points_possible = deets.points.values[ 0 ]
            setattr( activity, 'points_possible', points_possible )
            v[ 'points_possible' ] = points_possible

            # set text
            # description = activity.description
            # setattr( activity, 'description', description )
            v[ 'description' ] = activity.description

            activity.creation_dict = v

            u.components.append( activity )

        return u

    def create_units( self ):
        self.units = [ ]
        for i, row in self.start_dates.iterrows():
            print( row.unit )
            u = self.make_unit( row.unit, row.start )
            #         u.components.append( activity_type( **v) )
            self.units.append( u )

        return self.units


class CreationHandlerFactory:
    @classmethod
    def make( cls, activity, course, **kwargs ):
        if activity.creation_type == 'assignment':
            return AssignmentCreator( activity, course )
            # course.create_assignment( a.creation_dict )
        if activity.creation_type == 'quiz':
            return QuizCreator( activity, course )
            # course.create_quiz( a.creation_dict )
        if activity.creation_type == 'discussion':
            return DiscussionCreator( activity, course )
            # course.create_discussion_topic( a.creation_dict )
        if activity.creation_type == 'survey':
            return SurveyCreator( activity, course )


class IActivityCreator:
    """Parent of everything which creates stuff on canvas
    """

    def create( self ):
        raise NotImplementedError


class AssignmentCreator( IActivityCreator ):

    def __init__( self, activity, course, **kwargs ):
        self.course = course
        self.activity = activity

    @property
    def creation_dict( self ):
        d = self.activity.creation_dict
        # add fields specific to this knd of activity

        return d

    def create( self ):
        return self.course.create_assignment( self.creation_dict )


class QuizCreator( IActivityCreator ):

    def __init__( self, activity, course, **kwargs ):
        self.course = course
        self.activity = activity

    @property
    def creation_dict( self ):
        d = self.activity.creation_dict
        # add fields specific to this knd of activity
        return d

    def create( self ):
        return self.course.create_quiz( self.creation_dict )


class DiscussionCreator( IActivityCreator ):

    def __init__( self, activity, course, **kwargs ):
        self.course = course
        self.activity = activity

    @property
    def creation_dict( self ):
        d = self.activity.creation_dict
        # add fields specific to this knd of activity

        return d

    def create( self ):
        return self.course.create_assignment( self.creation_dict )


class SurveyCreator( IActivityCreator ):

    def __init__( self, activity, course, **kwargs ):
        self.course = course
        self.activity = activity

    @property
    def creation_dict( self ):
        d = self.activity.creation_dict
        # add fields specific to this knd of activity
        return d

    def create( self ):
        return self.course.create_assignment( self.creation_dict )


if __name__ == '__main__':
    pass
