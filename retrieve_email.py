from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import os
import pickle
import base64
from bs4 import BeautifulSoup
import re 


# If modifying these SCOPES, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_gmail_service():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)
    return service

def list_messages(service, user_id='me'):
    # Call the Gmail API to fetch INBOX
    results = service.users().messages().list(userId=user_id, labelIds=['INBOX', 'UNREAD']).execute()
    messages = results.get('messages', [])

    if not messages:
        print("No messages found.")
    else:
        print("Message snippets:")
        for message in messages[:5]:  # Get the first 5 messages
            msg = service.users().messages().get(userId=user_id, id=message['id'], format='full').execute()

            # Extracting the Subject from headers
            headers = msg['payload']['headers']
            subject = next(header['value'] for header in headers if header['name'] == 'Subject')

            # Extracting the message body
            get_decoded_email_body(msg)
            
def get_decoded_email_body(msg):
    # Function to find the email body part
    def find_body_part(parts):
        for part in parts:
            if part['mimeType'] == 'text/plain' or part['mimeType'] == 'text/html':
                if 'data' in part['body']:
                    return part['body']['data']
            if 'parts' in part:
                return find_body_part(part['parts'])
        return None

    # Extracting the Subject from headers
    headers = msg['payload']['headers']
    subject = next(header['value'] for header in headers if header['name'] == 'Subject')

    # Extracting the message body
    if 'parts' in msg['payload']:
        part_data = find_body_part(msg['payload']['parts'])
    else:
        part_data = msg['payload']['body']['data'] if 'body' in msg['payload'] and 'data' in msg['payload']['body'] else None

    decoded_string = ""
    if part_data:
        # Decode the base64 URL encoded string
        decoded_bytes = base64.urlsafe_b64decode(part_data + "==")  # Padding might be required
        # Convert the byte content to string
        decoded_string = decoded_bytes.decode('utf-8')

    clean_subject = clean_html(subject)
    clean_body = clean_html(decoded_string)
    
    print(f"Subject: {clean_subject} \n")
    print(f"Body: {clean_body}\n")
    print("\n")

def clean_html(html_content):
    # Function to remove the HTML tags from the email body
    soup = BeautifulSoup(html_content, 'html.parser')
    text = soup.get_text()
    text = re.sub(r'\s+', ' ', text)  # Remove extra whitespace
    return text.strip()


if __name__ == '__main__':
    service = get_gmail_service()
    list_messages(service)