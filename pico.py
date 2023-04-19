import openai
import os
import time
import json
from datetime import datetime
from email_interface import send_email
from spotify_interface import spotify_agent
from twilio_sms_interface import sms_agent
from text_to_speech import elevenlabs_tts, play_audio_content
from document_embedding import doc_agent
from weather import weather_agent
from google_interface import google_agent

openai.api_key = open("openai_key.txt", "r").read().strip("\n")  # get api key from text file

#Chat agent
class Chat:
    def __init__(self, model, system="You are a helpful assistant", max_tokens=500, speech=False, temp=0.7):
        openai.api_key = open("openai_key.txt", "r").read().strip("\n")
        self.model = model
        self.speech = speech
        self.system = system
        self.max_tokens = max_tokens
        self.temp = temp
    def __str__(self):
        name = "Chat Agent [" + self.model + "]"
        return name
    def reinsert_system_message(self, messages):
        if messages[0].get("role") != "system":
            messages.insert(0, {"role": "system", "content": self.system})
        return messages
    def chat(self, messages):
        messages = self.reinsert_system_message(messages)
        completion = openai.ChatCompletion.create(
            model = self.model,
            temperature = self.temp,
            max_tokens = self.max_tokens,
            messages = messages
        )
        reply_content = completion.choices[0].message.content
        return reply_content
    def stream_chat(self, messages, delay_time=0.01):
        messages = self.reinsert_system_message(messages)
        response = openai.ChatCompletion.create(
            model=self.model,
            temperature=self.temp,
            max_tokens = self.max_tokens,
            messages=messages,
            stream=True
        )
        reply_content = ''
        chunk = ''
        for event in response:
            event_text = event['choices'][0]['delta']
            new_text = event_text.get('content', '')
            print(new_text, end='', flush=True)
            reply_content += new_text
            chunk += new_text
            # Check if the chunk ends with a sentence-ending punctuation
            if chunk and chunk[-1] in {'.', '!', '?'}:
                if self.speech == True:
                    audio_content = elevenlabs_tts(chunk)
                    if audio_content is not None:
                        play_audio_content(audio_content)
                    chunk = ''
            time.sleep(delay_time)
        # Call the ElevenLabs API for the remaining text if any
        if self.speech == True:
            if chunk:
                audio_content = elevenlabs_tts(chunk)
                if audio_content is not None:
                    play_audio_content(audio_content)
            return reply_content
        return reply_content

#Allows saving of message history to file for later retrival
def write_message_history_to_file(full_message_history, directory):
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    filename = f"message_history_{timestamp}.json"
    # Create the directory if it doesn't exist
    if not os.path.exists(directory):
        os.makedirs(directory)
    file_path = os.path.join(directory, filename)
    with open(file_path, 'w') as outfile:
        json.dump(full_message_history, outfile, indent=2)

def is_exec_needed(prompt):
    keywords = [
            "play", "spotify", "volume", "next", "next song", "pause", "resume", "unpause", "playing", "music", "song",
            "send an email", "email",
            "sms", "text", "message",
            "analyze", "summarize", "folder", "directory"
    ]
    prompt = prompt.lower().strip()
    for keyword in keywords:
        if keyword in prompt:
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
        #Dictionary used to call functions depending on output of executive
        agent_dict = { 
                "send_email": send_email,
                "spotify_agent": spotify_agent,
                "send_sms": sms_agent,
                "analyze_documents": doc_agent,
                }
        completion = openai.ChatCompletion.create(
            model = self.model,
            temperature = 0,
            messages=[
                    {"role":"system", "content": "You analyze user input, and output the names of functions to fullfil a user's needs.\
                      The spotify_agent can search for music or artists, play and pause songs, or go to the next song. \
                     If the user just says, 'pause' or 'next song' or 'volume to x' that means the spotify_agent is needed. \
                     You can output: ['send_email', 'spotify_agent', 'send_sms', 'analyze_documents'] to fulfill a request, otherwise reply: 'chat'"},
                    {"role":"user", "content": prompt}
                    ] 
        )
        reply_content = completion.choices[0].message.content
        if any(command in reply_content for command in ["send_email", "spotify_agent", "send_sms", "analyze_documents"]):
            agent_response = agent_dict[reply_content](prompt)
            return agent_response #Response is status recieved from agent attempting to a complete task.
        else:
            return False #False means default to chat

def gpt3_exec(user_input):
    response = openai.Completion.create(
        engine="text-davinci-003",
        temperature = 0,
        max_tokens=10,
        prompt = "Analyze user input, and output the name of function to fullfil a user's needs.\
          The spotify_agent command can search for music or artists, play and pause songs, or go to the next song.\
          The send_email command will let a user send an email. The send_sms command will let a user send an SMS message.\
          The analyze_documents command will let a user analyze a document or the contents of a folder. \
         If none of these commands are needed, reply only with 'chat'. You are only allowed to output one command.\
          The only commands you are allowed to output are: 'spotify_agent', 'send_email', 'send_sms', \
         'analyze_documents', or 'chat'. Do not reply with any other output. User input: " + user_input
        )
    reply_content = response.choices[0].text.strip()
    if "spotify_agent" in reply_content:
        agent_response = spotify_agent(user_input)
        return agent_response
    elif "send_email" in reply_content:
        agent_response = send_email(user_input)
        return agent_response
    elif "send_sms" in reply_content:
        agent_response = sms_agent(user_input)
        return agent_response
    elif "analyze_documents" in reply_content:
        agent_response = doc_agent(user_input)
        return agent_response
    else:
        return False #False means default to chat

def gpt4_exec(user_input):
    completion = openai.ChatCompletion.create(
        model="gpt-4",
        temperature = 0,
        max_tokens=10,
        messages = [
                    {"role":"system", "content": "Analyze user input, and output the name of function to fullfil a user's needs.\
                    The spotify_agent command can play and pause songs on the user's computer, or go to the next song. \
                    If the user just says, 'pause' or 'next song' or 'volume to x' that means the spotify_agent is needed. \
                    Only call the spotify_agent if the user actually want to play music, not just talk about it. \
                    The send_email command will let a user send an email. The send_sms command will let a user send an SMS message.\
                    The analyze_documents command will let a user analyze a document or the contents of a folder. \
                    The weather_agent can provide information about weather, including sunrise and sunset. \
                    If none of these commands are needed, reply only with 'chat'. If it is unclear, reply with 'chat'\
                    You are only allowed to output one command.\
                    The only commands you are allowed to output are: 'spotify_agent', 'send_email', 'send_sms', \
                    'analyze_documents', 'weather_agent' or 'chat'. Do not reply with any other output."},
                    {"role":"user", "content": user_input}
                    ] 
        )
    reply_content = completion.choices[0].message.content
    if "spotify_agent" in reply_content:
        agent_response = spotify_agent(user_input)
        return agent_response
    elif "send_email" in reply_content:
        agent_response = send_email(user_input)
        return agent_response
    elif "send_sms" in reply_content:
        agent_response = sms_agent(user_input)
        return agent_response
    elif "analyze_documents" in reply_content:
        agent_response = doc_agent(user_input)
        return agent_response
    elif "weather_agent" in reply_content:
        agent_response = weather_agent(user_input)
        return agent_response
    else:
        google_search_result = google_agent(user_input)
        return google_search_result

def main_text():
    try:
        print("Welcome to the Pico Assistant interface!")
        print("Type 'quit' to exit the chat.\n")

        message_history = []
        full_message_history = []
        system_message = "You are Pico. Pico is an AI assistant. Your name is Pico. \
                        You can chat, send emails, get weather information and interact with Spotify. \
                        Above all you enjoy having interesting, intellectually stimulating \
                        conversations."
        max_history = 20  # Adjust this value to limit the number of messages considered

        while True:
            user_input = input("You: ")
            if user_input.lower() == 'quit':
                write_message_history_to_file(full_message_history, "./message_logs")
                break
            else:
                message_history.append({"role": "user", "content": user_input})
                full_message_history.append({"role": "user", "content": user_input})
                #reduces messages when max history exceeded
                if len(message_history) > max_history:
                    message_history = message_history[-max_history:]
                #Check user input, if executive is needed, call executive on user input and return result.
                agent_response = gpt4_exec(message_history[-1].get("content"))
                if agent_response == False:
                    print("\nPico: ", end='', flush=True)
                    gpt4_chat = Chat("gpt-4", system=system_message)
                    response = gpt4_chat.stream_chat(message_history)
                    message_history.append({"role": "assistant", "content": response})
                    full_message_history.append({"role": "assistant", "content": response})
                    print(f"\n")
                else:
                    print("\nPico: ", end='')
                    if isinstance(agent_response, list):  # Handling the case when the agent returns a list of responses
                        for i, response in enumerate(agent_response):
                            message_history.append(response)
                            full_message_history.append(response)
                            # Print only the most recent answer
                            if i == len(agent_response) - 1:
                                print(response["content"])
                    else:  # Handling the case when the agent returns a single response (string)
                        message_history.append({"role": "assistant", "content": agent_response})
                        full_message_history.append({"role": "assistant", "content": agent_response})
                        print(agent_response)

    except KeyboardInterrupt:
        print("\nDetected KeyboardInterrupt. Saving message history and exiting.")
    except Exception as e:
        print(f"\nAn error occurred: {e}. Saving message history and exiting.")
    finally:
        write_message_history_to_file(full_message_history, "./message_logs")
        print("Message history saved.")

if __name__ == "__main__":
    main_text()