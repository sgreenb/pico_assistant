import openai
import ast
from docx import Document
from pico import Chat
import os
import subprocess

def execute_commands(command_string):
    # Convert the string to a list of commands
    command_list = ast.literal_eval(command_string)
    # Execute each command in the list
    for command in command_list:
        try:
            exec(command, globals())
        except:
            proofread_command = proofreader_agent(command)
            exec(proofread_command, globals())

def proofreader_agent(command):
    system = "You proofread individual lines of Python 3 code. You primarily look for errors \
            such as SyntaxError and unescaped quotes. Do not concern yourself with NameError \
            since you are not shown preceding code. You will be given a line of Python 3 code \
            if there are no errors, simply return the code exactly. If there is an error only \
            reply with the modified code with the error fixed. Do not include any explanations \
            or additional comments in your response."
    message_history = []
    message_history.append({"role": "user", "content": command})
    proofreader_agent = Chat("gpt-4", system=system, temp=0)
    response = proofreader_agent.chat(message_history)
    return response

def file_agent(user_request):
    system = "You are 'File Agent', you take a user's request to generate or manipulate a file.\
        You have can use any methods from the Python libraries os and subprocess to acomplish \
        your task. You output a list of valid python commands, with arguments in the order required \
        to acomplish your goal. You only output the list of commands to be executed in the format: \
        '[operation_1, operation_2, operation_3]' Each operation must be a valid argument for the Python \
        exec() function, this means multiline operations must be contained in a single list item, you can\
        use the newline character to seperate the lines. Only reply with the list of commands. If the content \
        written to the file is code, include some comments for readibility. The default location to save and \
        retrive files is ./docs unless otherwise stated. Do not preface the response with natural language. \
        Be very careful to properly escape all quotes when necessary to prevent syntax errors." 
    message_history = []
    message_history.append({"role": "user", "content": user_request})
    file_agent = Chat("gpt-4", system=system, temp=0)
    response = file_agent.chat(message_history)
    return response

