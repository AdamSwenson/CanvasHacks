"""
Created by adam on 3/12/20
"""
__author__ = 'adam'

from CanvasHacks.SkaaSteps.SendInitialWorkToReviewer import SendInitialWorkToReviewer
from CanvasHacks.SkaaSteps.SendMetareviewToReviewer import SendMetareviewToReviewer
from CanvasHacks.SkaaSteps.SendReviewToReviewee import SendReviewToReviewee

if __name__ == '__main__':
    pass

from ipywidgets import widgets
from IPython.display import display
from CanvasHacks import environment

def run_all_steps( SEND=True, download=True ):
    print( "====================== STEP 1 ======================" )
    step1 = SendInitialWorkToReviewer( course=environment.CONFIG.course, unit=environment.CONFIG.unit, send=SEND )
    step1.run( rest_timeout=5 )

    print( "====================== STEP 2 ======================" )
    step2 = SendReviewToReviewee( environment.CONFIG.course, environment.CONFIG.unit, send=SEND )
    step2.run( rest_timeout=5, download=download )

    print( "====================== STEP 3 ======================" )
    step3 = SendMetareviewToReviewer( environment.CONFIG.course, environment.CONFIG.unit, send=SEND )
    step3.run( rest_timeout=5, download=download )



def skaa_run_button():
    RUNNING = False

    def get_style( is_running=False ):
        return 'warning' if is_running else 'danger'

    def get_name( is_running=False ):
        return 'RUNNING' if is_running else 'RUN SKAA'

        # Create the button

    #     layout = widgets.Layout( width=width )
    b = widgets.Button( description=get_name( RUNNING ), button_style=get_style( RUNNING ) )

    def callback( change ):
        RUNNING = True
        b.description = get_name( RUNNING )
        b.button_style = get_style( RUNNING )
        #         print('beep')
        #         time.sleep(3)
        #         print('boop')

        run_all_steps( SEND=True, download=True )

        RUNNING = False

        b.description = get_name( RUNNING )
        b.button_style = get_style( RUNNING )

    b.on_click( callback )
    display( b )
    return b
