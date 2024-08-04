import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from markupsafe import escape
import functions_framework

import random
from time import sleep
from notion_utils import (
    get_database, extract_pages, fetch_page, generate_questions
)
from objects import Page

@functions_framework.http
def send_email(request):
    recipient = "oscar.adserballe@gmail.com"
    sender_email = 'oscar.adserballe@gmail.com'
    sender_password = 'chay dlux lzbs rbtx'

    subject = "Morning Report"

    # Fetching database and extracting 10 random pages
    database_id = 'beb494e4d3554984a87984e8be8910b8'
    database = get_database(database_id=database_id)
    all_pages = extract_pages(database)
    pages = random.choices(all_pages, k=20)
    
    # For each page generate questions
    for page in pages:
        try:
            page = fetch_page(page)
            page = generate_questions(page)
        except Exception as e:
            try:
                print(page.text)
            except:
                print(f"Page text was not even fetched, see {page.url}")
            print(e)
            continue
        
    # Generate email
    try:
        # Create message container
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient
        msg['Subject'] = subject

        # Attach the message
        message_text = format_email_content(pages)
        msg.attach(MIMEText(message_text, 'html'))

        # Create server object with SSL option
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient, msg.as_string())
        server.quit()

        return f'Email sent to {escape(recipient)}'
    except Exception as e:
        print(e)
        return str(e), 499

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