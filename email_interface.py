import openai
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.mime.text import MIMEText
import base64
import csv
from difflib import SequenceMatcher

openai.api_key = open("openai_key.txt", "r").read().strip("\n")  # get api key from text file

def load_contacts(filename):
    contacts = {}
    with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            contacts[row['Name']] = row['E-mail 1 - Value']
    return contacts

def find_best_matching_contact(name, contacts):
    best_match = None
    best_similarity = 0.0
    for contact_name in contacts:
        similarity = SequenceMatcher(None, name.lower(), contact_name.lower()).ratio()
        if similarity > best_similarity:
            best_similarity = similarity
            best_match = contact_name
    return best_match if best_similarity > 0.5 else None

def send_email(prompt):
    SCOPES = ['https://www.googleapis.com/auth/gmail.send']
    completion = openai.ChatCompletion.create(
    model = "gpt-4",
            temperature = 0,
            messages=[
                    {"role":"system", "content": "You identify the recipient, title, and body of an email to be sent based on a user request. The output must be in the format: 'recipient | email title | email body'"},
                    {"role":"user", "content": prompt},
                    ] 
        )
    reply_content = completion.choices[0].message.content
    email_data = reply_content.strip().split('|')
    to, subject, body = email_data
    to = to.strip()
    subject = subject.strip()
    body = body.strip()

    #If an email address is not explicitly specified, search name in contacts and retrieve email
    if '@' not in to:
        contacts = load_contacts("contacts.csv")
        best_match = find_best_matching_contact(to, contacts)
        if best_match is not None:
            to = contacts[best_match]
        else:
            print(f"No matching contact found for {to}")

    try:
        creds = None
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        service = build('gmail', 'v1', credentials=creds)
        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject
        create_message = {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}
        send_message = (service.users().messages().send(userId="me", body=create_message).execute())
        status = "Email has been sent."
    except HttpError as error:
        print(F'An error occurred: {error}')
        status = "An error occured, message not sent."
        send_message = None
    return status