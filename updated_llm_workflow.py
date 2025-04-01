import os
import traceback
import pandas as pd
from src.data_handler import get_data_summary
from src.utils import init_prompt, get_coder_prompt, postprocess_code, get_evaluator_prompt, get_coder_init_prompt, get_evaluator_init_prompt
# from src.ollama_llms import get_coder_response, get_evaluator_response
from src.openai_llm import get_coder_response, get_evaluator_response
from src.code_excuter import execute_code, display_figures

import json
import sys

model_name = sys.argv[1]
print(f"===================model_name: {model_name}====================")
user_input = """열: 유전자  
행: 샘플

clustermap의 계층적 클러스터링을 사용하여 클러스터 정의

각 클러스터별 상위 100개의 표준 편차가 가장 높은 유전자 선택

변동성이 큰 유전자 상위 목록의 clustermap 표시; 샘플 클러스터를 col_colors 인수로 표시, 딕셔너리를 전달할 수 있음

ticklabels 자동으로 표시

각 클러스터에 고유한 유전자마다 클러스터와 동일한 색깔로 행에 표시 

행/열 둘다 색갈 표시되는지 확인

각 클러스터에 해당하는 유전자 print"""
qmd_content = f"""---
title: "생성된 시각화 코드"
format:
html:
code-fold: false
self-contained: true
execute:
  echo: true
  error: true
jupyter: python3
---

## user prompt
```
{user_input}
```
"""


coder_messages = get_coder_init_prompt(data_entry[0]["file_path"])
evaluator_messages = get_evaluator_init_prompt()

prompt = init_prompt(data_entry, user_input)

coder_messages.append({"role": "user", "content": prompt[0]["content"] + prompt[1]["content"]})
evaluator_messages.append({"role": "user", "content": prompt[0]["content"] + prompt[1]["content"]})

try:
    coder_response, coder_messages = get_coder_response(model_name=model_name, message=coder_messages, history=True, temperature=coder_temperature)
except:
    coder_response, coder_messages = {"code": "llm error"}, coder_messages

code = postprocess_code(coder_response["code"])
print("===================code====================")
print(code)
print("===========================================")
success = False
retry = False
max_retries = 20
n = 0


while True:
    scope = {}
    # 코드에 위험한 함수가 있는지 확인
    dangerous_functions = ['os.system', 'subprocess.call', 'subprocess.Popen', 'eval', 'exec', 'shutil.rmtree', 'os.remove', 'exit', 'input']
    
    # 코드에서 위험한 함수 검사
    has_dangerous_function = []
    for func in dangerous_functions:
        if func in code:
            has_dangerous_function.append(func)
    
    if has_dangerous_function != []:
        stdout = stdout = f"Warning: Code contains dangerous function: '{has_dangerous_function}'! ** Never use ['os.system', 'subprocess.call', 'subprocess.Popen', 'eval', 'exec', 'open', 'shutil.rmtree', 'os.remove', 'exit', 'input']**"
        success = False
    else:
        try:
            stdout = exec(code,scope)
            success = True
        except Exception as e:
            stdout = traceback.format_exc()
            success = False
    print(retry, n < max_retries, not success)
    if not success:
        print("===================error====================")
        print(stdout)
    else:
        print("===================success====================")
        stdout = "No error"
        print(stdout)
    # get evaluator prompt
    evaluator_messages += get_evaluator_prompt(code, stdout)
    # get evaluator response
    try:
        evaluator_response, evaluator_messages = get_evaluator_response(model_name=model_name, message=evaluator_messages, history=True, temperature=evaluator_temperature)
        retry = evaluator_response["retry"]
    except:
        evaluator_response, evaluator_messages = {"retry": False, "comment": "llm error"}, evaluator_messages
    if (not success) and (n < max_retries and not success):
        n += 1
        # get coder prompt
        coder_messages += get_coder_prompt(code, stdout, evaluator_response["comment"])
        # get coder response
        try:
            coder_response, coder_messages = get_coder_response(model_name=model_name, message=coder_messages, history=True, temperature=coder_temperature)
            code = postprocess_code(coder_response["code"])
            print("===================code====================")
            print(code)
            print("===========================================")
        except:
            coder_response, coder_messages = {"code": "llm error"}, coder_messages
    else:
        break