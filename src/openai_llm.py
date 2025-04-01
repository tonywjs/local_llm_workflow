import json
from pydantic import BaseModel
from openai import OpenAI
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

def get_coder_response(model_name: str, message: str, history: bool = False, temperature: float = 0.0):
    print("====================coder response====================")
    client = OpenAI(base_url=OLLAMA_URL + "/v1", api_key='ollama')
    with client.beta.chat.completions.stream(
        model=model_name,
        messages=message,
        response_format=CODER_OUTPUT_FORMAT,
        temperature=temperature,
        max_tokens=4000,
    ) as stream:
        for event in stream:
            # print(event.content)
            if event.type == "content.delta":
                if event.parsed is not None:
                    # Print the parsed data as JSON
                    print(event.delta, end='', flush=True)
            elif event.type == "content.done":
                print("DONE")
            elif event.type == "error":
                print("Error in stream:", event.error)
        final_completion = stream.get_final_completion().choices[0].message.content
        final_completion = json.loads(final_completion)
        if history:
            message.append({"role": "assistant", "content": final_completion["code"]})
        return final_completion, message


def get_evaluator_response(model_name: str, message: str, history: bool = False, temperature: float = 0.0):
    print("====================evaluator response====================")
    client = OpenAI(base_url=OLLAMA_URL + "/v1", api_key='ollama')
    with client.beta.chat.completions.stream(
        model=model_name,
        messages=message,
        response_format=EVALUATOR_OUTPUT_FORMAT,
        temperature=temperature,
        max_tokens=4000,
    ) as stream:
        for event in stream:
            # print(event.content)
            if event.type == "content.delta":
                if event.parsed is not None:
                    # Print the parsed data as JSON
                    print(event.delta, end='', flush=True)
            elif event.type == "content.done":
                print("DONE")
            elif event.type == "error":
                print("Error in stream:", event.error)
        final_completion = stream.get_final_completion().choices[0].message.content
        final_completion = json.loads(final_completion)
        if history:
            message.append({"role": "assistant", "content": final_completion["comment"]})
        return final_completion, message
