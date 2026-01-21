import base64
import sys
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import smtplib

from CanvasHacks.Errors.oauth import ExpiredTokenError
# from email.MIMEMultipart import MIMEMultipart
# from email.MIMEBase import MIMEBase
# from email import Encoders
# from email.MIMEText import MIMEText
from CanvasHacks.Logging.messages import MessageLogger
from CanvasHacks.Messaging.oauth import OauthHandler
from CanvasHacks import environment


class EmailerBase( object ):

    def __init__( self, password, test=False, text_subtype='html', show_debug=False):
        """
        :param password
        :param test
        :param text_subtype Typical values for text_subtype are plain, html, xml
        """
        self.show_debug = show_debug
        self.PASSWORD = password

        self.isTest = True if test else False

        # typical values for text_subtype are plain, html, xml
        self.text_subtype = text_subtype

        self.logger = MessageLogger()

        if self.isTest:
            print( "TESTING MODE" )
        else:
            print( "LIVE MODE" )

    def _connect( self ):
        """This will work for stmp servers using basic username and password
        authentication. This method should be overridden in child classes where
        a different system is needed"""
        try:
            self.conn = smtplib.SMTP( self.URL, self.PORT )
            self.conn.set_debuglevel( self.show_debug )
            self.conn.starttls()
            self.conn.login(self.USER, self.PASSWORD)
        except Exception as exc:
            sys.exit( "connection failed; %s" % str( exc ) )  # give a error message

    def sendMail( self, destination, message_content, subject, print_status=False ):
        """
        @param destination: should be an email address
        @type destination: C{str}
        """
        raise NotImplementedError

    def send_w_attachment( self, destination, message_content, subject, attachment ):
        """
        Sends an email with the specified attachment
        """
        raise NotImplementedError



class ExchangeEmailer( EmailerBase ):
    """
    Base class for sending email via exchange
    """

    def __init__( self, password=None, test=False, text_subtype='html', show_debug=False):
        self.sender = 'adam.swenson@csun.edu'
        self.bcc_address = 'adamswenson@gmail.com'

        self.SMTPserver = 'smtp.office365.com'
        self.USERNAME = "ars62917"
        self.URL = "smtp.office365.com"
        self.PORT = 587
        self.USER = "adam.swenson@csun.edu"

        super().__init__( password, test, text_subtype, show_debug )

        self.token_handler = OauthHandler(environment.CONFIG)

        # Get the access token upon instantiation.
        # If the class persists for too long a period, the token
        # will expire. This will be handled in sendMail
        self.token_handler.request_access_token()

    def _make_auth_bytes(self, fromAddr, access_token):
        auth_string = f"user={fromAddr}\x01auth=Bearer {access_token}\x01\x01"
        return base64.b64encode(auth_string.encode()).decode()

    def _connect( self ):
        """Overwrites the base connection process to use oauth
        Raises ExpiredTokenError if the access token has expired"""

        auth_bytes = self._make_auth_bytes(self.USER, self.token_handler.access_token)

        self.conn = smtplib.SMTP(self.SMTPserver, self.PORT)
        self.conn.set_debuglevel(self.show_debug)
        self.conn.ehlo()
        self.conn.starttls()
        self.conn.ehlo()

        code, resp = self.conn.docmd("AUTH", "XOAUTH2 " + auth_bytes)
        if code > 400:
            raise ExpiredTokenError( code, resp )



    def sendMail( self, destination, message_content: str, subject: str, print_status=False ):
        """
        :param destination: an email address
        :type destination: C{string}
        :param print_status: Whether to print status messages
        :param subject: The subject line
        :param message_content: The body of the message
        """

        self.destination = destination
        self.content = message_content
        self.subject = subject
        try:
            msg = MIMEText( self.content, self.text_subtype )
            msg[ 'To' ] = self.destination
            msg[ 'Subject' ] = self.subject
            msg[ 'From' ] = self.sender  # some SMTP servers will do this automatically, not all

            try:
                self._connect()
            except ExpiredTokenError:
                print("Getting new access token...")
                # If the token has expired, get a new one and try again
                self.token_handler.request_access_token()
                self._connect()

            try:
                self.conn.sendmail( self.sender, self.destination, msg.as_string() )
                # This was the problem that caused CAN-77
                # self.conn.sendmail( self.sender, self.bcc_address, msg.as_string() )
                if print_status:
                    print( "Sent to: %s \n %s" % (self.destination, msg.as_string()) )
            finally:
                self.conn.close()
        except Exception as exc:
            self.logger.write("mail failed; %s" % str( exc ), is_error=True)
            sys.exit( "mail failed; %s" % str( exc ) )  # give a error message

    def send_w_attachment( self, destination, message_content, subject, attachment ):
        """
        Sends an email with the specified attachment
        Unclear whether this works yet
        """
        self.destination = destination
        self.content = message_content
        self.subject = subject
        try:
            msg = MIMEMultipart()
            msg[ 'Subject' ] = self.subject
            msg[ 'From' ] = self.sender
            msg[ 'To' ] = self.destination
            # msg['To'] = ', '.join(self.destination)
            part = MIMEBase( 'application', "octet-stream" )
            part.set_payload( open( attachment, "rb" ).read() )
            Encoders.encode_base64( part )
            part.add_header( 'Content-Disposition', 'attachment; filename="%s"' % attachment )
            msg.attach( part )

            try:
                self._connect()
            except ExpiredTokenError:
                print("Getting new access token...")
                # If the token has expired, get a new one and try again
                self.token_handler.request_access_token()
                self._connect()

            try:
                self.conn.sendmail( self.sender, self.destination, msg.as_string() )
            finally:
                self.conn.close()
        except Exception as exc:
            sys.exit( "mail failed; %s" % str( exc ) )  # give a error message


class GmailEmailer( EmailerBase ):
    """
    Base class for sending email via gmail
    """

    def __init__( self, password, test=False, text_subtype='html', show_debug=False ):
        self.sender = "gradeomatic@gmail.com"
        self.bcc_address = 'adamswenson@gmail.com'

        if test:
            self.SMTPserver = 'mailtrap.io'
            self.URL = 'sandbox.smtp.mailtrap.io'
            self.PORT = 2525
            self.USERNAME = '64b2254587cb48'
            self.PASSWORD = password
            self.USER = self.USERNAME

        else:
            self.SMTPserver = "smtp.gmail.com"
            self.USERNAME = self.sender
            self.URL = self.SMTPserver
            self.PORT = 587
            self.USER = self.USERNAME

        super().__init__( password, test, text_subtype, show_debug )

    def sendMail( self, destination, message_content: str, subject: str, print_status=False ):
        """
        :param destination: an email address
        :type destination: C{string}
        :param print_status: Whether to print status messages
        :param subject: The subject line
        :param message_content: The body of the message
        """

        self.destination = destination
        self.content = message_content
        self.subject = subject
        try:
            msg = MIMEText( self.content, self.text_subtype )
            msg[ 'To' ] = self.destination
            msg[ 'Subject' ] = self.subject
            msg[ 'From' ] = self.sender  # some SMTP servers will do this automatically, not all

            # msg['CC'] = self.sender

            self._connect()
            try:
                self.conn.sendmail( self.sender, self.destination, msg.as_string() )
                # This was the problem that caused CAN-77
                # self.conn.sendmail( self.sender, self.bcc_address, msg.as_string() )
                if print_status:
                    print( "Sent to: %s \n %s" % (self.destination, msg.as_string()) )
            finally:
                self.conn.close()
        except Exception as exc:
            self.logger.write("mail failed; %s" % str( exc ), is_error=True)
            sys.exit( "mail failed; %s" % str( exc ) )  # give a error message

    def send_w_attachment( self, destination, message_content, subject, attachment ):
        """
        Sends an email with the specified attachment
        Unclear whether this works yet
        """
        self.destination = destination
        self.content = message_content
        self.subject = subject
        # try:
        #     msg = MIMEMultipart()
        #     msg[ 'Subject' ] = self.subject
        #     msg[ 'From' ] = self.sender
        #     msg[ 'To' ] = self.destination
        #     # msg['To'] = ', '.join(self.destination)
        #     part = MIMEBase( 'application', "octet-stream" )
        #     part.set_payload( open( attachment, "rb" ).read() )
        #     Encoders.encode_base64( part )
        #     part.add_header( 'Content-Disposition', 'attachment; filename="%s"' % attachment )
        #     msg.attach( part )
        #     conn = self.connect()
        #     try:
        #         conn.sendmail( self.sender, self.destination, msg.as_string() )
        #     finally:
        #         conn.close()
        # except Exception as exc:
        #     sys.exit( "mail failed; %s" % str( exc ) )  # give a error message


# class Emailer( EmailerBase ):
#     """
#     This is the base class for any emailing function
#     """
#
#     def __init__( self, test=False ):
#         EmailerBase.__init__( self, test )
#
#     def sendMail( self, destination, message_content, subject, print_status=False ):
#         """
#         @param destination: should be a list of email addresses
#         @type destination: C{list}
#         """
#         # this invokes the secure SMTP protocol (port 465, uses SSL)
#         # from smtplib import SMTP                  # use this for standard SMTP protocol   (port 25, no encryption)
#
#         self.destination = destination
#         self.content = message_content
#         self.subject = subject
#         try:
#             msg = MIMEText( self.content, self.text_subtype )
#             msg[ 'To' ] = self.destination
#             msg[ 'Subject' ] = self.subject
#             msg[ 'From' ] = self.sender  # some SMTP servers will do this automatically, not all
#             # msg['CC'] = self.sender
#
#             conn = smtplib.SMTP( self.SMTPserver, self.PORT )
#             conn.set_debuglevel( False )
#             conn.starttls()
#             conn.login( self.USERNAME, self.PASSWORD )
#             try:
#                 conn.sendmail( self.sender, self.destination, msg.as_string() )
#                 if (print_status):
#                     print( "Sent to: %s \n %s" % (self.destination, msg.as_string()) )
#             finally:
#                 conn.close()
#         except Exception as exc:
#             sys.exit( "mail failed; %s" % str( exc ) )  # give a error message
#
#     def send_w_attachment( self, destination, message_content, subject, attachment ):
#         """
#         Sends an email with the specified attachment
#         """
#         self.destination = destination
#         self.content = message_content
#         self.subject = subject
#         try:
#             msg = MIMEMultipart()
#             msg[ 'Subject' ] = self.subject
#             msg[ 'From' ] = self.sender
#             msg[ 'To' ] = self.destination
#             # msg['To'] = ', '.join(self.destination)
#             part = MIMEBase( 'application', "octet-stream" )
#             part.set_payload( open( attachment, "rb" ).read() )
#             Encoders.encode_base64( part )
#             part.add_header( 'Content-Disposition', 'attachment; filename="%s"' % attachment )
#             msg.attach( part )
#             conn = self.connect()
#             try:
#                 conn.sendmail( self.sender, self.destination, msg.as_string() )
#             finally:
#                 conn.close()
#         except Exception as exc:
#             sys.exit( "mail failed; %s" % str( exc ) )  # give a error message
