from pydantic import BaseModel
from ollama import Client
from dotenv import load_dotenv
import os

# load .env
load_dotenv()


OLLAMA_URL = os.getenv("OLLAMA_URL")


class CODER_OUTPUT_FORMAT(BaseModel):
    thought: str
    code: str

class EVALUATOR_OUTPUT_FORMAT(BaseModel):
    thought: str
    retry: bool
    comment: str

def get_coder_response(model_name: str, message: list, history: bool = False):
    print("====================coder response====================")
    client = Client(host=OLLAMA_URL)
    response = client.chat(model=model_name, messages=message, stream=True, format=CODER_OUTPUT_FORMAT.model_json_schema(), options={"stop": ["\n\n\n\n"]})
    full_response = ""

    for part in response:
        content = part['message']['content']
        print(content, end='', flush=True)
        full_response += content

    full_response = full_response.choices[0].message.content
    if history:
        message.append({"role": "assistant", "content": full_response})

    return full_response, history


def get_evaluator_response(model_name: str, message: list, history: bool = False):
    print("====================evaluator response====================")
    client = Client(host=OLLAMA_URL)
    response = client.chat(model=model_name, messages=message, stream=True, format=EVALUATOR_OUTPUT_FORMAT.model_json_schema(), options={"stop": ["\n\n\n\n"]})
    full_response = ""
    for part in response:
        content = part['message']['content']
        print(content, end='', flush=True)
        full_response += content

    full_response = full_response.choices[0].message.content
    if history is not None:
        history.append({"role": "assistant", "content": full_response})

    return full_response, history


