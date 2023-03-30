import os
from twilio.rest import Client

twilio_keys = []
twilio_keys += open("twilio_keys.txt", "r").read().split("\n")

account_sid = twilio_keys[0]
auth_token = twilio_keys[1]
twilio_number = twilio_keys[2]
client = Client(account_sid, auth_token)

message = client.messages \
                .create(
                     body="Join Earth's mightiest heroes. Like Kevin Bacon.",
                     from_=twilio_number,
                     to=''
                 )

print(message.sid)