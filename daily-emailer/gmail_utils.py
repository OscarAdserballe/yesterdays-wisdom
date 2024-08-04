import os.path
import base64
from objects import Page 
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def get_gmail_service():
    """Shows basic usage of the Gmail API."""
    creds = None
    # The file token.json stores the user's access and refresh tokens and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)
    return service

def send_message(service, user_id, message):
    try:
        message = service.users().messages().send(userId=user_id, body=message).execute()
        print('Message Id: %s' % message['id'])
        return message
    except Exception as e:
        print(f'An error occurred: {e}')
        return None

def format_email_content(pages: list[Page]) -> str:
    html_content = """
    <html>
    <body>
    <h1>Pages Report</h1>
    <ul>
    """
    
    for page in pages:
        if isinstance(page, Page):
            try:
                html_content += f"""
                <li>
                    <h2>{page.title}</h2>
                    <p><strong>Type:</strong> {page.type}</p>
                    <p><strong>Class:</strong> {page.in_class}</p>
                    <p><strong>Created Time:</strong> {page.created_time}</p>
                    <p><strong>Last Edited Time:</strong> {page.last_edited_time}</p>
                    <p><strong>Created By:</strong> {page.created_by}</p>
                    <p><strong>URL:</strong> <a href="{page.url}">{page.url}</a></p>
                    <p><strong>Public URL:</strong> <a href="{page.public_url}">{page.public_url}</a></p>
                    <p><strong>Questions:</strong></p>
                    <ul>
                """
                for question, answer in page.questions.items():
                    html_content += f"<li><strong>{question}:</strong> {answer}</li>"
                
                html_content += """
                    </ul>
                </li>
                """
            except Exception as e:
                print(f"Some other error occurred in connection with creating the email, {e}")
        else:
            print(f"{page} is not Page object")
        
    html_content += """
    </ul>
    </body>
    </html>
    """
    
    return html_content

def send_email(pages: list[Page], sender: str, to: str, subject: str):
    service = get_gmail_service()

    email_content = format_email_content(pages)
    
    message = MIMEText(email_content, 'html')
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes())
    raw = raw.decode()
    email_message = {'raw': raw}
    
    send_message(service, 'me', email_message)