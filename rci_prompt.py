import openai

# Derived from https://arxiv.org/pdf/2303.17491.pdf

openai.api_key = open("openai_key.txt", "r").read().strip("\n")  # get api key from text file

def chat_agent(prompt):
    completion = openai.ChatCompletion.create(
    model = "gpt-4",
            temperature = 0.7,
            messages=[
                    {"role":"system", "content": "You are a helpful assistant"},
                    {"role":"user", "content": prompt},
                    ] 
        )
    reply_content = completion.choices[0].message.content
    return reply_content

def rci_chat_agent(prompt):
    # Step 1: User inputs a question
    user_question = prompt

    # Step 2: Chatbot generates an answer but does not return it
    completion = openai.ChatCompletion.create(
        model="gpt-4",
        temperature=0.7,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_question},
        ],
    )
    generated_answer = completion.choices[0].message.content

    # Step 3: Inject stock user message
    review_message = "Review your previous answer and find problems with your answer."

    # Step 4: Chatbot analyzes its previous answer and generates a reply with the list of problems but does not return it
    completion = openai.ChatCompletion.create(
        model="gpt-4",
        temperature=0.7,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_question},
            {"role": "assistant", "content": generated_answer},
            {"role": "user", "content": review_message},
        ],
    )
    problems_found = completion.choices[0].message.content

    # Step 5: Inject another stock user message
    improve_message = "Based on the problems you found, improve your answer."

    # Step 6: Chatbot generates an improved answer and returns it to the user
    completion = openai.ChatCompletion.create(
        model="gpt-4",
        temperature=0.7,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_question},
            {"role": "assistant", "content": generated_answer},
            {"role": "user", "content": review_message},
            {"role": "assistant", "content": problems_found},
            {"role": "user", "content": improve_message},
        ],
    )
    improved_answer = completion.choices[0].message.content
    return improved_answer