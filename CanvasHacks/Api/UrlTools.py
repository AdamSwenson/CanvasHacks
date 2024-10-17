"""
Created by adam on 9/20/18
"""
__author__ = 'adam'

from CanvasHacks import environment


# import configparser

# # Load api token and section numbers
# print("Reading credentials from %s" % environment.CREDENTIALS_FILE)
# config = configparser.ConfigParser()
# config.read( environment.CREDENTIALS_FILE)
#
# URL_BASE = config['url'].get('BASE')

def make_url_no_api_version(section_id, verb):
    """Returns the canvas request url
    Canvasapi was updated to throw an error if /api/v1/ is included
    in the base url.
    This function returns the url base as set in config (i.e., no /api/v1/)/section_id/verb"""
    return "%s/%s/%s" % (environment.CONFIG.canvas_url_base, section_id, verb)


def make_url(section_id, verb):
    """Returns the canvas request url
    Canvasapi was updated to throw an error if /api/v1/ is included
    in the base url. This function adds those back in when building the url for non-canvasapi using
    requests
    """
    return f"{environment.CONFIG.canvas_url_base}/api/v1/courses/{section_id}/{verb}"

    #return "%s/%s/%s" % (environment.CONFIG.canvas_url_base, section_id, verb)


if __name__ == '__main__':
    pass