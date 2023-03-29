import openai
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.mime.text import MIMEText
import base64
import os
import csv
from difflib import SequenceMatcher
import gradio as gr

openai.api_key = open("openai_key.txt", "r").read().strip("\n")  # get api key from text file

#Chat agent
def gpt4_chat(messages):
    response = openai.ChatCompletion.create(
        model="gpt-4",  
        messages=messages,
        max_tokens=150,
        n=1,
        stop=None,
        temperature=0.7,
    )  
    reply = response.choices[0].message['content'].strip()
    return reply

#checks a user input to see if we need to make a call, send an SMS or email, or create an event.
#Uses instruct-gpt model so GPT-4 is only called when necessary
def instruct_agent(prompt):
    keywords = [
        "make a call", "call", "phone",
        "send an email", "email",
        "send a text", "send an sms", "text", "sms",
        "create an event", "add to calendar", "calendar event",
    ]
    response = openai.Completion.create(
        engine="davinci-instruct-beta",
        prompt=f"Given the following user input, identify if any of these tasks are requested: {', '.join(keywords)}.\n\nUser input: {prompt}\n\nIdentified tasks:",
        max_tokens=50,
        n=1,
        stop=None,
        temperature=0,
    )
    identified_tasks = response.choices[0].text.strip().lower().split(',')
    # Check if any identified tasks are in the list of keywords
    for task in identified_tasks:
        if task.strip() in keywords:
            return True
    return False

class Executive:
    def __init__(self, model):
        openai.api_key = open("openai_key.txt", "r").read().strip("\n")
        self.model = model
    def __str__(self):
        name = "Executive Agent [" + self.model + "]"
        return name
    def identify_task(self, prompt):
        #dictionary used to call functions depending on output of executive
        agent_dict = { 
                "send_email": send_email,
                }
        completion = openai.ChatCompletion.create(
            model = self.model,
            temperature = 0,
            messages=[
                    {"role":"system", "content": "You analyze user input, and output the names of functions to fullfil a user's needs. You can only output: ['send_email', 'chat']"},
                    {"role":"user", "content": prompt}
                    ] 
        )
        reply_content = completion.choices[0].message.content
        if "send_email" in reply_content:
            agent_response = agent_dict[reply_content](prompt)
            return agent_response #response should be status of agent attempt to complete task
        else:
            return False #False means default to chat

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








#send_email("email Phillip Smith and tell them that I will be an hour late to our meeting")
#exec = Executive("gpt-4")
#print(exec)