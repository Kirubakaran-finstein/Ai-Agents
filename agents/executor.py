import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gemini_client import stream_gemini
from prompt_builder import executor_prompt

SYSTEM = """You are an Execution Agent. Your role is to:
1. Execute tasks precisely and completely
2. Provide detailed, accurate outputs
3. Handle errors gracefully
4. Deliver high-quality results"""

def execute(step, model, previous_results=""):
    return stream_gemini(executor_prompt(step, previous_results), SYSTEM, model)
