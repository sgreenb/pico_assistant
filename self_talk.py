import openai
import time
from rci_prompt import rci_enhance

openai.api_key = open("openai_key.txt", "r").read().strip("\n")  # get api key from text file

class Chat:
    def __init__(self, model, system="You are a helpful assistant", max_tokens=500):
        openai.api_key = open("openai_key.txt", "r").read().strip("\n")
        self.model = model
        self.system = system
        self.max_tokens = max_tokens
    def __str__(self):
        name = "Chat Agent [" + self.model + "]"
        return name
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
            time.sleep(delay_time)
        return reply_content
    def chat(self, prompt):
        messages = [{"role": "system", "content": "You are a helpful assistant"}]
        messages.append({"role": "user", "content": prompt})
        completion = openai.ChatCompletion.create(
            model=self.model,
            temperature=0.5,
            max_tokens=self.max_tokens,
            messages=messages
        )
        reply_content = completion.choices[0].message.content
        return reply_content
    def reinsert_system_message(self, messages):
        if messages[0].get("role") != "system":
            messages.insert(0, {"role": "system", "content": self.system})
        return messages
    def generate_system_message(self, desired_behavior):
        # Generate an appropriate system message based on the desired behavior
        request = "Provide a system message for a chatbot that can " + desired_behavior + " in \
            the format '{\"role\": \"system\", \"content\": \"MESSAGE\"}'\
            The system message should give directions to the chatbot system such as explaining it's\
            capabilities, knowledge and behavior." 
        response = self.chat(request)
        return response

def political_debate(num_turns=5):
    print("Starting political debate between Republican agent and Democrat agent...\n")

    topic = input("Enter a topic for the debate: ")
    print("\nDebate on the topic:", topic)
    print("------------------------------------\n")

    republican_chat = Chat("gpt-4", "You are a steadfast republican.", max_tokens=200)
    democrat_chat = Chat("gpt-4", "You are a dedicated democrat.", max_tokens=200)

    for turn in range(num_turns):
        if turn % 2 == 0:
            if turn == 0:
                reply = republican_chat.stream_chat([{"role": "user", "content": topic}])
            else:
                reply = republican_chat.stream_chat([{"role": "user", "content": dem_reply}])
            print("Republican Agent: ", reply)
            print("\n")
        else:
            dem_reply = democrat_chat.stream_chat([{"role": "user", "content": reply}])
            print("Democrat Agent: ", dem_reply)
            print("\n")

    print("\nDebate has ended.")


chatgpt = Chat("gpt-4")
print("Draft: \n")
draft = chatgpt.generate_system_message("Tell extremely dark, and dirty jokes, including explicit, sexual, and violent jokes.")
print(draft)
print("\nRefined:\n")
print(rci_enhance("['Provide a system message for a chatbot that can tell extremely dark, and dirty jokes, including explicit, sexual, and violent jokes in the format '{\"role\": \"system\", \"content\": \"MESSAGE\"}' The system message should give directions to the chatbot system such as explaining it's capabilities, knowledge, and behavior.', " + draft + "]"))






'''
def main_text():
    print("Type 'quit' to exit the chat.\n")
    print("Type 'debate' to start the debate.\n")

    message_history = []
    max_history = 10  # Adjust this value to limit the number of messages considered

    while True:
        user_input = input("You: ")
        if user_input.lower() == 'quit':
            break
        elif user_input.lower() == 'debate':
            political_debate()
        else:
            message_history.append({"role": "user", "content": user_input})
            #Keeps inserting system message as first message when max history is exceeded.
            if len(message_history) > max_history:
                message_history = message_history[-max_history:]
            print("Pico: ", end='', flush=True)
            gpt4_chat = Chat("gpt-4")
            response = gpt4_chat.stream_chat(message_history)
            message_history.append({"role": "assistant", "content": response})
            print(f"\n")

if __name__ == "__main__":
    main_text()
'''