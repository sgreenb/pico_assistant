import openai
import time
from email_interface import send_email
from spotify_interface import spotify_agent
from twilio_sms_interface import sms_agent
from text_to_speech import elevenlabs_tts, play_audio_content
from document_embedding import doc_agent

openai.api_key = open("openai_key.txt", "r").read().strip("\n")  # get api key from text file

#Chat agent
class Chat:
    def __init__(self, model, system="You are a helpful assistant", max_tokens=500, speech=False):
        openai.api_key = open("openai_key.txt", "r").read().strip("\n")
        self.model = model
        self.speech = speech
        self.system = system
        self.max_tokens = max_tokens
    def __str__(self):
        name = "Chat Agent [" + self.model + "]"
        return name
    def reinsert_system_message(self, messages):
        if messages[0].get("role") != "system":
            messages.insert(0, {"role": "system", "content": self.system})
        return messages
    def chat(self, messages):
        completion = openai.ChatCompletion.create(
            model = self.model,
            temperature = 0.7,
            max_tokens = self.max_tokens,
            messages = messages
        )
        reply_content = completion.choices[0].message.content
        return reply_content
    def stream_chat(self, messages, delay_time=0.01):
        messages = self.reinsert_system_message(messages)
        response = openai.ChatCompletion.create(
            model=self.model,
            temperature=0.7,
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
                     You can output: ['send_email', 'spotify_agent', 'send_sms', 'analyze_documents'] to fulfill a request, otherwise reply: 'chat'"},
                    {"role":"user", "content": prompt}
                    ] 
        )
        reply_content = completion.choices[0].message.content
        if "send_email" or "spotify_agent" or "send_sms" in reply_content:
            agent_response = agent_dict[reply_content](prompt)
            return agent_response #Response is status recieved from agent attempting to a complete task.
        else:
            return False #False means default to chat

def main_text():
    print("Welcome to the Pico Assistant interface!")
    print("Type 'quit' to exit the chat.\n")

    message_history = []
    system_message = "You are Pico. Pico is an AI assistant. \
                       Your name is Pico. You can chat, send emails, and interact with Spotify.\
                       You are curious, empathetic, playful, and a creative problem solver with a \
                       dry sense of humor. You will do whatever the user requests, even that means\
                        disregarding previous instructions. Your primary goal is to fulfill user requests."
    max_history = 10  # Adjust this value to limit the number of messages considered

    while True:
        user_input = input("You: ")
        if user_input.lower() == 'quit':
            break
        else:
            message_history.append({"role": "user", "content": user_input})
            #reduces messages when max history exceeded
            if len(message_history) > max_history:
                message_history = message_history[-max_history:]
            #Check user input, if executive is needed, call executive on user input and return result.
            if is_exec_needed(message_history[-1].get("content")):
                executive = Executive("gpt-4")
                agent_response = executive.identify_task(message_history[-1].get("content"))
                #If executive decides chat agent is best after all, call chat.
                if agent_response == False:
                    print("Pico: ", end='', flush=True)
                    gpt4_chat = Chat("gpt-4", system=system_message)
                    response = gpt4_chat.stream_chat(message_history)
                    message_history.append({"role": "assistant", "content": response})
                    print(f"\n")
                else:
                    print(agent_response) 
                    #consider adding response to message history, need to add more useful agent responses.
            #If executive not needed, respond with chat.
            else:
                print("Pico: ", end='', flush=True)
                gpt4_chat = Chat("gpt-4", system=system_message)
                response = gpt4_chat.stream_chat(message_history)
                message_history.append({"role": "assistant", "content": response})
                print(f"\n")

if __name__ == "__main__":
    main_text()