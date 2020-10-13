from CanvasHacks import environment
from CanvasHacks.SkaaSteps.SendInitialWorkToReviewer import SendInitialWorkToReviewer
from CanvasHacks.SkaaSteps.SendMetareviewToReviewer import SendMetareviewToReviewer
from CanvasHacks.SkaaSteps.SendReviewToReviewee import SendReviewToReviewee


def run_all_steps( SEND=True, download=True, **kwargs ):
    """
    Runs all steps for a unit defined in environment
    :param studentRepo: If not defined, each step will instantiate it's own repo
    :param SEND: Whether to send messages (also governs whether records the association between author and reviewer)
    :param download: Whether to try downloading
    :return:
    """
    print( "====================== STEP 1 ======================" )
    step1 = SendInitialWorkToReviewer( course=environment.CONFIG.course,
                                       unit=environment.CONFIG.unit,
                                       send=SEND,
                                       **kwargs)
    step1.run( rest_timeout=5 )

    print( "\n====================== STEP 2 ======================" )
    step2 = SendReviewToReviewee( environment.CONFIG.course,
                                  environment.CONFIG.unit,
                                  send=SEND,
                                  **kwargs)
    step2.run( rest_timeout=5, download=download )

    try:
        print( "\n====================== STEP 3 ======================" )
        step3 = SendMetareviewToReviewer( environment.CONFIG.course,
                                          environment.CONFIG.unit,
                                          send=SEND,
                                          **kwargs)
        step3.run( rest_timeout=5, download=download )
    except AttributeError as e:
        # This may be raised when there is no metareview assignment
        print("Step 3 encountered an error: ",  e)

    except IndexError as e:
        # This may happen when there are no results for the metareview
        print("Problem loading files for Step 3 ", e)

    # Return in case need to check values on them
    return (step1, step2, step3)


if __name__ == '__main__':
    # todo Add stuff here to grab command line arguments and set the unit
    pass

