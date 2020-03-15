"""
Tools for selecting whether running on live data or test data
Created by adam on 2/15/20
"""
from IPython.display import display
from ipywidgets import widgets
from CanvasHacks import environment

__author__ = 'adam'


def make_test_selector(return_button=False):
    """
    Displays or returns the button for selecting
    whether we are running on test or live data
    :return:
    """
    def get_description():
        return 'TEST' if environment.CONFIG.is_test else 'LIVE'

    def get_icons():
        return ['check', ''] if environment.CONFIG.is_test else ['', 'check']

    def get_style():
        return 'success' if environment.CONFIG.is_test else 'warning'

    def get_value():
        return environment.CONFIG.is_test

    def get_tooltip():
        return "Click to set to {}".format("TEST" if not environment.CONFIG.is_test else 'LIVE')

    b = widgets.ToggleButton(
        value=get_value(),
        description=get_description(),
        button_style=get_style(),
        tooltip=get_tooltip()
    )
    if return_button is True:
        # If putting inside a box or something else which will
        # call display
        return b
    else:
        display( b )


    def callback(j):
        if not j.new:
            environment.CONFIG.set_live()

        if j.new:
            environment.CONFIG.set_test()

        b.icons = get_icons()
        b.button_style = get_style()
        b.value = get_value()
        b.description = get_description()
        b.tooltip = get_tooltip()

    b.observe(callback, names='value')


if __name__ == '__main__':
    pass