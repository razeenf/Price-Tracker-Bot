import httplib2
import os
import oauth2client
from oauth2client import client, tools, file
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from apiclient import errors, discovery

SCOPES = 'https://www.googleapis.com/auth/gmail.send'
CLIENT_SECRET_FILE = 'client_secret.json'

def get_credentials():
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir, 'gmail-python-email-send.json')
    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        credentials = tools.run_flow(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def create_message(recipient, username, title, sale_price, original_price, discount, asin):
    msg = MIMEMultipart()
    msg['Subject']  = "An item you're tracking is on sale!"
    msg['To'] = recipient
    msg['From'] = 'Price Tracker Bot <amzn.tracker.bot@gmail.com>'
    html = open('template.html', 'r').read().format(**locals())
    msg.attach(MIMEText(html, 'html'))
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    email = {'raw': raw}
    send_message(email)

def send_message(email):
    http = get_credentials().authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http)
    try:
        message = (service.users().messages().send(userId="me", body=email).execute())
        print('Message Id: %s' % message['id'])
        return message
    except errors.HttpError as error:
        print('An error occurred: %s' % error)