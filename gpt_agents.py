import openai
import time
from email_interface import send_email
from spotify_interface import spotify_agent

openai.api_key = open("openai_key.txt", "r").read().strip("\n")  # get api key from text file

#Chat agent
class Chat:
    def __init__(self, model):
        openai.api_key = open("openai_key.txt", "r").read().strip("\n")
        self.model = model
    def __str__(self):
        name = "Chat Agent [" + self.model + "]"
        return name
    def chat(self, messages):
        completion = openai.ChatCompletion.create(
            model = self.model,
            temperature = 0.7,
            messages = messages
        )
        reply_content = completion.choices[0].message.content
        return reply_content
    def stream_chat(self, messages, delay_time=0.01):
        response = openai.ChatCompletion.create(
            model=self.model,
            temperature=0.7,
            messages=messages,
            stream=True
        )
        reply_content = ''
        for event in response:
            print(reply_content, end='', flush=True)
            event_text = event['choices'][0]['delta']
            reply_content = event_text.get('content', '')
            time.sleep(delay_time)
        return reply_content    

#Checks a user input to see if we need to do some external task.
#Uses instruct-gpt model so GPT-4 is only called when necessary.
#Need to check if this is actually worthwhile.
def instruct_agent(prompt):
    keywords = [
        "play", "spotify", "volume", "next", "next song", "pause", "music", "song",
        "send an email", "email",
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
    #Check if any identified tasks are in the list of keywords
    for task in identified_tasks:
        if task.strip() in keywords:
            return True
    return False

#faster alternative to instruct_agent
def is_exec_needed(prompt):
    keywords = [
            "play", "spotify", "volume", "next", "next song", "pause", "music", "song",
            "send an email", "email",
            "sms", "text", "message"
    ]
    prompt = prompt.lower()
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
                "send_sms": False #add this later
                }
        completion = openai.ChatCompletion.create(
            model = self.model,
            temperature = 0,
            messages=[
                    {"role":"system", "content": "You analyze user input, and output the names of functions to fullfil a user's needs. You can output: ['send_email', 'spotify_agent', 'send_sms'] to fulfill a request, otherwise reply: 'chat'"},
                    {"role":"user", "content": prompt}
                    ] 
        )
        reply_content = completion.choices[0].message.content
        if "send_email" or "spotify_agent" in reply_content:
            agent_response = agent_dict[reply_content](prompt)
            #return agent_response #Response is status recieved from agent attempting to a complete task.
        else:
            return False #False means default to chat

def main():
    print("Welcome to the Pico Assistant interface!")
    print("Type 'quit' to exit the chat.\n")

    message_history = []
    system_message = [{"role": "system", "content": "You are Pico. Pico is an AI assistant. Your name is Pico. You can chat, send emails, and interact with Spotify"}]
    message_history.append(system_message[0])
    max_history = 10  # Adjust this value to limit the number of messages considered

    while True:
        user_input = input("You: ")
        if user_input.lower() == 'quit':
            break
        else:
            message_history.append({"role": "user", "content": user_input})
            #Keeps inserting system message as first message when max history is exceeded.
            if len(message_history) > max_history:
                message_history.insert(-max_history + 1, system_message[0])
            message_history = message_history[-max_history:]
            #Check user input, if executive is needed, call executive on user input and return result.
            if is_exec_needed(message_history[-1].get("content")):
                executive = Executive("gpt-4")
                agent_response = executive.identify_task(message_history[-1].get("content"))
                if agent_response == False:
                    print("Pico: ", end='', flush=True)
                    gpt4_chat = Chat("gpt-4")
                    response = gpt4_chat.stream_chat(message_history)
                    message_history.append({"role": "assistant", "content": response})
                    print(f"\n")
                else:
                    print(agent_response)
            #If executive not needed, respond with chat.
            else:
                print("Pico: ", end='', flush=True)
                gpt4_chat = Chat("gpt-4")
                response = gpt4_chat.stream_chat(message_history)
                message_history.append({"role": "assistant", "content": response})
                print(f"\n")
        
if __name__ == "__main__":
    main()