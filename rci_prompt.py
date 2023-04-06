import openai

# Derived from https://arxiv.org/pdf/2303.17491.pdf

openai.api_key = open("openai_key.txt", "r").read().strip("\n")  # get api key from text file

def rci_enhance(prompt):
    #prompt should be a two item list, where the first item is a query, and the second item is a rough draft answer.
    completion = openai.ChatCompletion.create(
    model="gpt-4",
    temperature=0.5,
    messages=[
        {"role": "system", "content": "You analyze a user's question, and a possible answer to that question.\
         You make insightful criticisms about the provided answer and suggest ways that the answer can be improved.\
         The question and answer will be supplied as a list in the following format: '[\"USER QUESTION\", \"ANSWER GIVEN\"]'\
         Do not respond with the improved answer. Only respond with a list of criticisms and suggestions of how the answer can be improved."},
        {"role": "user", "content": prompt},
    ],
    )
    criticism = completion.choices[0].message.content
    completion = openai.ChatCompletion.create(
    model="gpt-4",
    temperature=0.5,
    messages=[
        {"role": "system", "content": "You analyze a query and answer to a query along with a list of criticisms and improvements\
         that can make that answer better. Rewrite the provided answer in a way that addresses the provided critiques\
         and implemnts the suggested improvements."},
        {"role": "user", "content": prompt + " " + criticism},
    ],
    )
    improved_answer = completion.choices[0].message.content
    return improved_answer