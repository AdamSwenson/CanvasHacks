"""
Created by adam on 1/29/19
"""
import json
import requests
import docx
import PyPDF2
from assets.RequestTools import make_request_header
from assets.UrlTools import make_url

__author__ = 'adam'


def download_journals( url, destination ):
    """Handles making the request to download journals"""
    # download file
    print( url )
    file_response = requests.get( url, headers=make_request_header() )

    # write to folder
    print( "Writing to %s" % destination )
    open( destination, 'wb' ).write( file_response.content )


def download_submitted_file( url, filepath ):
    response = requests.get( url, headers=make_request_header() )
    # save it to file
    open( filepath, 'wb' ).write( response.content )


def get_submissions( course_id, assignment_id, per_page=42 ):
    """Makes request to the server for all submissions for the given assignment
    Example
        course_id = SECTION_930
        assignment_id = 288480
        response2 = get_submissions(course_id, assignment_id)
    """
    responses = []
    url = make_url( course_id, 'assignments' )
    url = "%s/%s/submissions?per_page=%s" % (url, assignment_id, per_page)
    try:
        while True:
            print( url )
            response = requests.get( url, headers=make_request_header() )
            responses += response.json()
            url = response.links['next']['url']
    except KeyError:
        return responses


def process_response( response_json, journal_folder ):
    """Takes the response and pulls out submissions which used the text box, then downloads
    submitted files and processes out their text content
    """
    submissions = [ ]

    for j in response_json:
        result = { 'submission_id': j[ 'id' ], 'student_id': j[ 'user_id' ] }
        if j[ 'body' ] is not None:
            # The student used the online text box to submit
            result[ 'body' ] = j[ 'body' ]

        else:
            # The student submitted the journal as a separate document
            if 'attachments' in j.keys() and len( j[ 'attachments' ] ) > 0:
                url = j[ 'attachments' ][ 0 ][ 'url' ]
                filename = make_journal_filename( j )

                # download and save submitted file
                fpath = "%s/%s" % (journal_folder, filename)
                download_submitted_file( url, fpath )

                # open the file and extract text
                result[ 'body' ] = getBody( fpath )

            else:
                # NB., if a student never submitted (workflow_state = 'unsubmitted'),
                # then they will have an entry which lacks a body key
                result[ 'body' ] = None
        submissions.append( result )

    return submissions


def save_submission_json( submissions, folder, json_name='all-submissions' ):
    # save submissions
    with open( "%s/%s.json" % (folder, json_name), 'w' ) as fpp:
        json.dump( submissions, fpp )


def get_journal_filename(response):
    """Extracts the name of the file submitted from the response"""
    return response[ 'attachments' ][ 0 ][ 'filename' ]


def make_journal_filename( response ):
    """Creates the standardized filename for saving"""
    return "%s-%s" % (response[ 'user_id' ], get_journal_filename(response)) #response[ 'attachments' ][ 0 ][ 'filename' ])


def getDocxText( filename ):
    doc = docx.Document( filename )
    fullText = [ ]
    for para in doc.paragraphs:
        fullText.append( para.text )

    return '\n'.join( fullText )


def getPdfText( filepath ):
    pdfFileObj = open( filepath, 'rb' )
    pdfReader = PyPDF2.PdfFileReader( pdfFileObj )
    pageObj = pdfReader.getPage( 0 )
    return pageObj.extractText()


def getBody( filepath ):
    """Extracts the text from a saved file"""
    PICTURE_PLACEHOLDER = 'picture-uploaded picture-uploaded picture-uploaded picture-uploaded picture-uploaded'
    filepath = filepath.strip()

    if filepath[ -5: ] == '.docx':
        return getDocxText( filepath )

    if filepath[ -4: ] == '.pdf':
        return getPdfText( filepath )

    elif filepath[ -4: ] == '.jpg':
        return PICTURE_PLACEHOLDER

    elif filepath[ -4: ] == '.png':
        return PICTURE_PLACEHOLDER

    elif filepath[ -4: ] == '.xml':
        return PICTURE_PLACEHOLDER

    elif filepath[ -6: ] == '.pages':
        return PICTURE_PLACEHOLDER

    elif filepath[ -4: ] == '.odt':
        return PICTURE_PLACEHOLDER

    else:
        return PICTURE_PLACEHOLDER


def process_response_without_saving_files( response_json, journal_folder ):
    """Takes the response and pulls out submissions which used the text box, then downloads
    submitted files and processes out their text content
    """
    submissions = [ ]

    for j in response_json:
        result = { 'submission_id': j[ 'id' ], 'student_id': j[ 'user_id' ] }
        if j[ 'body' ] is not None:
            # The student used the online text box to submit
            result[ 'body' ] = j[ 'body' ]

        else:
            # The student submitted the journal as a separate document
            if 'attachments' in j.keys() and len( j[ 'attachments' ] ) > 0:
                url = j[ 'attachments' ][ 0 ][ 'url' ]
                filename = get_journal_filename(j)

                # download the submitted file
                fpath = "%s/%s" % (journal_folder, filename)
                response = requests.get( url, headers=make_request_header() )
                content = response.content

                # download_submitted_file( url, fpath )

                # open the file and extract text
                result[ 'body' ] = getBody( fpath )

            else:
                # NB., if a student never submitted (workflow_state = 'unsubmitted'),
                # then they will have an entry which lacks a body key
                result[ 'body' ] = None
        submissions.append( result )

    return submissions


if __name__ == '__main__':
    pass
