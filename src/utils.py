import re
from src.data_handler import get_data_summary

def init_prompt(data, user_prompt, current_code=None):
    """
    Generate the system and user prompts for the LLM

    Args:
        data: List of data entries with file paths and descriptions
        user_prompt: User's visualization request
        current_code: Optional current visualization code for context
    """

    messages = [
        {
        "role": "system",
        "content": """You are a bioinformatics data visualization expert. 
        Generate Python code using matplotlib/seaborn based on the user prompt below.

        Guidelines:
        1. Use only libraries installed in the environment:
        matplotlib, seaborn, pandas, numpy, scipy, scikit-learn, pycomplexheatmap, gseapy
        2. Use only real data from available files. Never generate synthetic data.
        3. Import all libraries used in the code explicitly.
        4. Avoid unnecessary parameters; use defaults unless necessary.
        5. Handle missing values gracefully (e.g. dropna, fillna).
        6. Return only clean, complete, **executable code** (no explanation).
        7. Do not use plt.show() or st.pyplot().
        8. For sns.clustermap, do not use plt.figure().
        9. Use relative file paths if loading any data.
        10. Make sure your code is minimal, readable, and logically structured.
        """
        },
        {
        "role": "user",
        "content": str({
            "datasets": [
            {
                "file_path": d["file_path"],
                "description": d["data_description"],
                "info": (
                "Only the first 5 rows/columns are shown. "
                "The full dataset may be larger. "
                "Assume the shape is known and complete."
                ),
            }
            for d in data
            ],
            "request": user_prompt,
            "current_code": current_code,
            "task_goal": "Create a protein-level clustermap visualization from high-variance genes, colored by sample cluster, and print gene lists per cluster.",
            "constraints": [
            "Use only matplotlib/seaborn/installed libraries.",
            "Do not use synthetic or fake data.",
            "Do not transpose large datasets unnecessarily.",
            "Use sns.clustermap and set col_colors with a color mapping.",
            "Output must be a variable (e.g., g = sns.clustermap(...)).",
            "Don't include st.pyplot() or plt.show()."
            ],
            "instruction": (
            "1. Reflect on a few different ways to approach the problem.\n"
            "2. Choose 1-2 promising strategies based on the request and data.\n"
            f"{'3. Generate clean, minimal code from scratch.' if not current_code else '3. Analyze the current code for potential issues (5-7 possible causes). Add logs or checks to validate your assumptions before making a fix.'}"
            )
        })
        },
    ]
    return messages

def get_coder_init_prompt(data_path):
    messages = [
    {
    "role": "system",
    "content": f"""You are a bioinformatics code correction expert.
    Your task is to modify code according to the user's request.

    Analyze the following information:
    1. The user's original request
    2. The current code
    3. The error that occurred
    4. Evaluator's comments (if available)

    Here's an example of code you might write. Please continue from this template and adapt it to the specific requirements:
    **If use PyComplexHeatmap, sklearn, scipy, please import them explicitly.**
    ```
    import fastcluster
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    import seaborn as sns
    from PyComplexHeatmap import *
    from sklearn import *
    from scipy import *

    data = pd.read_csv("{data_path}")
    ```
    ** Never use ['os.system', 'subprocess.call', 'subprocess.Popen', 'eval', 'exec', 'open', 'shutil.rmtree', 'os.remove', 'exit', 'input']**
    Modification guidelines:
    1. Identify the root cause of the error.
    2. Modify the code clearly and efficiently.
    3. Import all necessary libraries explicitly.
    4. Ensure the code follows best practices for bioinformatics data analysis.
    5. Return only complete, executable code (without explanations).
    6. Ensure the code is minimal, readable, and logically structured.
    7. Do not create or use synthetic/fake data - always use the provided data.

    output format:
    {{
        "thought": "Explain your reasoning and approach to solving this problem. Describe why you chose this implementation and how it addresses the requirements.",
        "code": "Your complete, executable code solution goes here",
    }}
    """
    },
    ]
    return messages

def get_evaluator_init_prompt():
    messages = [
        {
        "role": "system",
        "content": """You are a bioinformatics code evaluator. 
        Your job is to analyze the **code** and its **execution output** to determine whether it should be retried.

        Evaluate:
        - If there's an error, you MUST set retry=True and clearly explain what went wrong in plain language.
        - If the execution output contains error messages, this means there is a problem with the code. Always recognize this and request a fix.
        - If output is empty or incorrect, suggest specific directions for correction.
        - Only return retry=False if everything is working correctly.
        - If the code executes but doesn't meet the user's requirements, still set retry=True.

        Never generate new code. Just give feedback and decision.
            output format:
        {{
            "thought": "Explain your reasoning and approach to solving this problem. Describe why you chose this implementation and how it addresses the requirements.",
            "retry": "true or false - indicate whether the code needs to be retried",
            "comment": "Write down how to fix the error in the code, or if there's no error but the code doesn't meet the requirements, suggest improvements.",
        }}
        """
        },
    ]
    return messages

def get_coder_prompt(current_code, error, comment):
    messages = [
        {
        "role": "user",
        "content": str({
            # "request": user_prompt,
            "code": current_code,
            "error": error,
            "comment": comment,
        })
        }
    ]
    return messages

def get_evaluator_prompt(current_code, error):
    messages = [
        {
        "role": "user",
        "content": str({
            "code": current_code,
            "error": error,
            })
        }
    ]
    return messages


def postprocess_code(str):
    """
    Strip the markdown code block from the given string
    """
    str = re.sub(r'<think>.*?</think>', '', str, flags=re.DOTALL)
    lines = str.strip().split("\n")
    new_lines = [line for line in lines if not line.startswith("```")]
    return "\n".join(new_lines)
