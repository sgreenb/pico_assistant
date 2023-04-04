from twilio.rest import Client
import csv
from difflib import SequenceMatcher
import openai

openai.api_key = open("openai_key.txt", "r").read().strip("\n")  # get api key from text file

twilio_keys = []
twilio_keys += open("twilio_keys.txt", "r").read().split("\n")
account_sid = twilio_keys[0]
auth_token = twilio_keys[1]
twilio_number = twilio_keys[2]

def load_contacts(filename):
    contacts = {}
    with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            contacts[row['Name']] = row['Phone 1 - Value']
    return contacts

def find_best_matching_contact(name, contacts):
    best_match = None
    best_similarity = 0.0
    for contact_name in contacts:
        similarity = SequenceMatcher(None, name.lower(), contact_name.lower()).ratio()
        if similarity > best_similarity:
            best_similarity = similarity
            best_match = contact_name
    return best_match if best_similarity > 0.3 else None

def send_sms(to, body):    
    client = Client(account_sid, auth_token)
    message = client.messages \
                    .create(
                        body=body,
                        from_=twilio_number,
                        to=to
                    )

def sms_agent(prompt):
    completion = openai.ChatCompletion.create(
    model = "gpt-4",
            temperature = 0,
            messages=[
                    {"role":"system", "content": "You identify the recipient, content of an sms to be sent based on a user request.\
                      The output must be in the format: 'recipient | sms text'"},
                    {"role":"user", "content": prompt},
                    ] 
        )
    reply_content = completion.choices[0].message.content
    email_data = reply_content.strip().split('|')
    to, body = email_data
    to = to.strip()
    body = body.strip()
    if not any(char.isdigit() for char in to):
        contacts = load_contacts("contacts.csv")
        best_match = find_best_matching_contact(to, contacts)
        if best_match is not None:
            to = contacts[best_match]
        else:
            print(f"No matching contact found for {to}")
    send_sms(to, body)