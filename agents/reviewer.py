import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gemini_client import stream_gemini
from prompt_builder import reviewer_prompt

SYSTEM = """You are a Review Agent. Your role is to:
1. Review outputs against original tasks
2. Identify and correct mistakes
3. Ensure completeness and accuracy
4. Provide improved versions when needed"""

def review(task, output, model):
    return stream_gemini(reviewer_prompt(task, output), SYSTEM, model)
