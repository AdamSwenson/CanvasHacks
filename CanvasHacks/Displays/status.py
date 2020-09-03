"""
Created by adam on 5/10/20
"""
__author__ = 'adam'

from IPython.display import HTML, Latex
from IPython.display import display
from ipywidgets import widgets

import pandas as pd

import CanvasHacks.environment as env

if __name__ == '__main__':
    pass

TIME_TEMPLATE = "%b %m  %H.%M"

def run_status( run_stopped, rest_min, time_templ=TIME_TEMPLATE, return_widget=True ):
    """
    Creates a html widget displaying when the last run finished and when
    the next run begins.
    :param run_stopped:
    :param rest_min:
    :param time_templ:
    :param return_widget: If false, calls IPython.display.display; if true, returns widget
    :return:
    """
    templ = """<p><strong>Completed at:</strong> {run_stopped} | <strong>Next at:</strong> {next_at}</p>"""
    next_run = run_stopped + pd.Timedelta( minutes=rest_min )
    run_stopped = run_stopped.strftime( time_templ )
    next_at = next_run.strftime( time_templ )

    html = templ.format( run_stopped=run_stopped, next_at=next_at )

    w = widgets.HTML(
        value="html",
        # placeholder='Some HTML',
        # description='Some HTML',
    )
    if return_widget:
        return w

    display(w)
