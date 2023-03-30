import os
from twilio.rest import Client

twilio_keys = []
twilio_keys += open("twilio_keys.txt", "r").read().split("\n")

account_sid = twilio_keys[0]
auth_token = twilio_keys[1]
twilio_number = twilio_keys[2]

def send_sms(to, body):    
    client = Client(account_sid, auth_token)
    message = client.messages \
                    .create(
                        body=body,
                        from_=twilio_number,
                        to=to
                    )