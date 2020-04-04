"""
Created by adam on 3/16/20
"""
__author__ = 'adam'

import re

import canvasapi

from CanvasHacks.Definitions.skaa import InitialWork, Review, MetaReview
from CanvasHacks.Definitions.other import TopicalAssignment, UnitEndSurvey
from CanvasHacks.Definitions.discussion import DiscussionForum, DiscussionReview

if __name__ == '__main__':
    pass


class Unit:
    """The main SKAA. This holds the definitions of all the consituent parts"""
    __name__ = 'Unit'

    def __init__( self, course, unit_number ):
        self.component_types = [ TopicalAssignment,
                                 InitialWork,
                                 Review,
                                 MetaReview,
                                 DiscussionForum,
                                 DiscussionReview,
                                 UnitEndSurvey
                                 ]
        self.components = [ ]

        self.course = course
        self.unit_number = unit_number
        if isinstance( course, canvasapi.course.Course ):
            # This check is here so can run tests without
            # needing a dummy Course object
            self._initialize()

    # def __repr__(self):
    #     """This way can still use unit in format statements """
    #     return self.unit_number

    def _initialize( self ):
        # Get all assignments for the course
        assignments = [ a for a in self.course.get_assignments() ]
        print( "{} assignments in course".format( len( assignments ) ) )
        # Parse out the assignments which have the unit number in their names
        unit_assignments = self.find_for_unit( self.unit_number, assignments )
        print( "{} assignments found for unit # {}".format( len( unit_assignments ), self.unit_number ) )
        self.find_components( unit_assignments )
        for c in self.components:
            # todo access_code_for_next_on probably not needed; created without looking at what already have
            # self._set_access_code_for_next( c )
            # Set the unit number for the assignment
            setattr( c, 'unit_number', self.unit_number )

    def find_components( self, unit_assignments ):
        # Parse components of unit
        for t in self.component_types:
            for a in unit_assignments:
                if t.is_activity_type( a.name ):
                    o = t( **a.attributes )
                    o.access_code = self._set_access_code( o )
                    self.components.append( o )

    def find_for_unit( self, unit_number, assignments ):
        """Given a list of unit names finds the one's
        relevant to this unit
        """
        rx = re.compile( r"\bunit {}\b".format( unit_number ) )
        try:
            return [ a for a in assignments if rx.search( a.name.strip().lower() ) ]
        except AttributeError:
            # Things like discussion forums have a title, not a name
            return [ a for a in assignments if rx.search( a.title.strip().lower() ) ]

    def _set_access_code_for_next( self, obj ):
        """Sets the access code students will need for the subsequent
        unit on the present unit as access_code_for_next.
        NB, this must be run after all the unit.components have been
        discovered and had their access codes set
        """
        # todo access_code_for_next_on probably not needed; created without looking at what already have

        try:
            if obj.access_code_for_next_on is not None:
                next_assign = self.get_by_class( obj.access_code_for_next_on )
                obj.access_code_for_next = next_assign.access_code
        except AttributeError:
            print( "No access code for subsequent unit set for {}".format( obj.name ) )

    def _set_access_code( self, obj ):
        """Some things will have an access code stored
        on them. Others have no access code. Some have
        the access code stored elsewhere.
        This sorts that out and sets the access code if possible.
        NB, this sets the code for the present unit, not the unit
        we will be notifying about
        """
        try:
            # first we try to set from self
            if obj.access_code is not None:
                return obj.access_code
            raise AttributeError
        except AttributeError:
            # check to see if we ahve a quiz id
            try:
                return self.course.get_quiz( obj.quiz_id ).access_code
            except AttributeError:
                print( "No access code for {}".format( obj.name ) )
                return None

    def get_by_class( self, component_class ):
        """
        Returns the unit component given an unistantiated
        class definition object
        :param component_class:
        :return:
        """
        for c in self.components:
            if isinstance( c, component_class ):
                return c

    def get_activity_by_id( self, activity_id ):
        for c in self.components:
            if c.id == activity_id:
                return c

    def get_discussion_by_topic_id( self, topic_id ):
        """
        Discussions are usually identified via the topic id
        thus this is a shortcut to getting the right one, if there
        is more than one associated with the unit
        :param topic_id:
        :return:
        """
        for c in self.components:
            try:
                if c.topic_id == topic_id:
                    return c
            except AttributeError:
                pass

    @property
    def topical_assignment( self ):
        for c in self.components:
            if isinstance( c, TopicalAssignment ):
                return c

    @property
    def initial_work( self ):
        for c in self.components:
            if isinstance( c, InitialWork ):
                return c

    @property
    def metareview( self ):
        for c in self.components:
            if isinstance( c, MetaReview ):
                return c

    @property
    def review( self ):
        for c in self.components:
            if isinstance( c, Review ):
                return c

    @property
    def discussion_forum( self ):
        for c in self.components:
            if isinstance( c, DiscussionForum ):
                return c

    @property
    def discussion_review( self ):
        for c in self.components:
            if isinstance( c, DiscussionReview ):
                return c

    @property
    def unit_end_survey( self ):
        for c in self.components:
            if isinstance( c, UnitEndSurvey ):
                return c