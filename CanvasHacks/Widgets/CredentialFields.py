"""
Created by adam on 2/5/19
"""
__author__ = 'adam'

from IPython.display import display
from ipywidgets import widgets

from CanvasHacks.Widgets.InputFields import make_course_ids_input, make_canvas_token_input

TOKEN_INSTRUCTIONS = """
    <div>
        <div>
            <p>You'll need to generate a token for the Canvas API. The token replaces your username/password when making requests to Canvas.</p> 
            <p>Please record the token in a secure place. This program will not save it; you will have to re-enter it every time you use this tool.</p>

            <p>First log into Canvas. Then: </p>
            <blockquote>
                <p>Click the "profile" link in the top right menu bar, or navigate to /profile</p>

                <p>Under the "Approved Integrations" section, click the button to generate a new access token.</p>

            <p>Once the token is generated, you cannot view it again, and you'll have to generate a new token if you forget
                it.
                Remember that access tokens are password equivalent, so keep it secret (ed: keep it safe!).</p>

                <p><a href="https://canvas.instructure.com/doc/api/file.oauth.html#manual-token-generation">https://canvas.instructure.com/doc/api/file.oauth.html#manual-token-generation</a>
                </p>
            </blockquote>
        </div>
        <div>
            <h5> Paste your token into the box below. You don't have to click anything, its value will be read when
                needed</h5>
        </div>
    </div>
    """

SECTION_INSTRUCTIONS = """
    <div>
        <p>You will also need the id number(s) of the courses you wish to grade. You can find them by logging into canvas
            and going to the course page. The number you are looking for will be in the url, immediately after
            '/courses/'. For example:</p>
        <blockquote>https://canvas.csun.edu/courses/<b>12345</b></blockquote>
        <p>Write this number down somewhere secure so that you can re-enter it next time you use the
            program.</p>

        <h5>Add the course ids one-at-a-time using the box and buttons below</h5>
    </div>
    """


def token_instructions_and_input():
    instruct = widgets.HTML( value=TOKEN_INSTRUCTIONS )
    display( instruct )
    make_canvas_token_input()


def section_instructions_and_input():
    display( widgets.HTML( SECTION_INSTRUCTIONS ) )
    make_course_ids_input()


def make_credentials_input():
    token_instructions_and_input()
    section_instructions_and_input()


if __name__ == '__main__':
    pass
