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


def make_url(section_id, verb):
    """Returns the canvas request url"""
    return "%s/%s/%s" % (environment.URL_BASE, section_id, verb)


if __name__ == '__main__':
    pass