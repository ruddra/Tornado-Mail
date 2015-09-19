###SMTP Configuration 
SMTP_USERNAME = 'ME'
SMTP_PASSWORD = 'MYPASSWORD'
SMTP_HOST = 'SMTP.HOST'
SMTP_SENDER = 'SENDER@HOST'

###IMAP Configuration
IMAP_USERNAME = 'ME'
IMAP_PASSWORD = 'MYPASSWORD'
IMAP_SSL = 'SMTP.SSL'
IMAP_RECEIVER = 'RECEIVER@HOST'


import tornado.web
import imaplib
import email
import json
import smtplib
from email.mime.text import MIMEText
from tornado.ioloop import IOLoop


class IMAPRequestHandler(tornado.web.RequestHandler):
    def get(self):
        msg_dict = self.get_messages()
        self.write(json.dumps(msg_dict))

    def _get_text(self, email_message_instance):
        maintype = email_message_instance.get_content_maintype()
        if maintype == 'multipart':
            for part in email_message_instance.get_payload():
                if part.get_content_maintype() == 'text':
                    return part.get_payload()
        elif maintype == 'text':
            return email_message_instance.get_payload()

    def _parse_header_from_list(self, content):
        try:
            _content = email.header.decode_header(content)
            return _content[0][0]
        except IndexError:
            return 'None'

        except Exception as e:
            print(e)
            return 'None'

    def get_messages(self):
        all_unread_msg = dict()
        try:
            server = imaplib.IMAP4_SSL(IMAP_SSL, 993)
            server.login(IMAP_USERNAME, IMAP_PASSWORD)
            server.select("INBOX")
            typ, data = server.search(None, '(UNSEEN)')

            msg_dict = dict()
            for num in data[0].split():
                single_msg = dict()
                typ, data = server.fetch(num, '(RFC822)')
                msg = email.message_from_bytes(data[0][1])
                if 'subject' in msg:
                    single_msg['subject'] = self._parse_header_from_list(msg['subject'])
                if 'from' in msg:
                    single_msg['from'] = self._parse_header_from_list(msg['from'])
                if 'to' in msg:
                    single_msg['to'] = self._parse_header_from_list(msg['to'])

                single_msg['body'] = self._get_text(msg)

                msg_dict[msg['message-id']] = single_msg
            all_unread_msg['message'] = 'Successfully retrieved messages {0} messages'.format(len(msg_dict))
            all_unread_msg['emails'] = msg_dict
            all_unread_msg['status'] = 200

            server.close()
            server.logout()
        except Exception as e:
            # raise e
            all_unread_msg['message'] = "Error occurred: {0}".format(e)
            all_unread_msg['status'] = 400

        return all_unread_msg


class SMTPRequestHandler(tornado.web.RequestHandler):
    def post(self):
        msg = self.get_argument('body')
        subject = self.get_argument('subject')
        recipients = self.get_argument('to')

        self.send_email(msg, subject, recipients)

    def send_email(self, msg, subject, recipients):
        smtp = smtplib.SMTP()
        smtp.connect(SMTP_HOST, 25)
        smtp.login(SMTP_USERNAME, SMTP_PASSWORD)
        msg = MIMEText(msg)
        sender = SMTP_SENDER
        try:
            msg['Subject'] = subject
            msg['From'] = sender
            msg['To'] = recipients
            smtp.sendmail(sender, recipients, msg.as_string())
            msg = dict()
            msg['message'] = "success"
            msg['status'] = 200
            self.write(json.dumps(msg))
        except Exception as e:
            msg = dict()
            msg['message'] = "Error: {0}".format(e)
            msg['status'] = 400
            self.write(json.dumps(msg))


application = tornado.web.Application([
    (r"/getmail", IMAPRequestHandler),
    (r"/sendmail", SMTPRequestHandler)
])

application.listen(7777)
IOLoop.instance().start()
