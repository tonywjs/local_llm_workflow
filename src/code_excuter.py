import io
from contextlib import redirect_stderr, redirect_stdout
from typing import List
import traceback
import matplotlib.pyplot as plt

# 인터랙티브 모드 활성화 (그래프가 즉시 표시되도록 함)
plt.ion()

def execute_code(code_string: str) -> bool:
    """
    Safely executes visualization code and displays the result in Streamlit.

    Args:
        code_string: The Python code to execute
        data: the session state data loaded by streamlit
        status: Streamlit status element to update status messages

    Returns:
        bool: True if execution was successful, False otherwise
    """

    # Add debug logging
    # st.write("Code being executed:")
    # st.code(code_string)

    # Create a new figure before execution
    
    # 실행 전에 모든 그림 닫기
    plt.close('all')
    
    # Create a safe globals environment with necessary imports
    globals_dict = {
        "plt": __import__('matplotlib.pyplot'),
        "np": __import__('numpy'),
        "pd": __import__('pandas'),
        "scipy": __import__('scipy'),
        "sklearn": __import__('sklearn'),
        "sns": __import__('seaborn')
    }
    
    # 추가 모듈 임포트
    # try:
    #     # scipy.cluster.hierarchy 모듈 임포트
    #     scipy_cluster = __import__('scipy.cluster.hierarchy', fromlist=['linkage', 'dendrogram'])
    #     globals_dict['linkage'] = scipy_cluster.linkage
    #     globals_dict['dendrogram'] = scipy_cluster.dendrogram
    # except ImportError:
    #     pass

    # Capture stdout and stderr
    stdout = io.StringIO()
    stderr = io.StringIO()

    # Execute the code with output capturing and warning filtering
    import warnings

    with warnings.catch_warnings():
        with redirect_stdout(stdout), redirect_stderr(stderr):
            try:
                exec(code_string, globals_dict, locals())
            except Exception as e:
                print(f"{traceback.format_exc()}", file=stderr)
                current_figures = []
                return False, stderr.getvalue(), current_figures

    current_figures = [plt.figure(i) for i in plt.get_fignums()]
    return True, stdout, current_figures


def display_figures(stdout, current_figures):
    # 모든 열린 그림 가져오기
    
    
    # 그림이 없으면 경고 표시
    if not current_figures:
        print("코드가 실행되었지만 그래프가 생성되지 않았습니다.")
        return False
    
    # 모든 그림 표시하기
    for fig in current_figures:
        # 터미널에서 실행 시 그래프를 표시하기 위해 non-blocking 모드로 설정
        plt.figure(fig.number)
        plt.show(block=False)
        plt.pause(0.1)  # 그래프가 화면에 표시될 시간을 주기 위한 짧은 일시 정지
        plt.close(fig)

    # Display any print statements
    if isinstance(stdout, io.StringIO):
        output = stdout.getvalue()
        if output:
            print(output)
    else:
        print(stdout)

    return True
