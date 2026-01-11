import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gemini_client import call_gemini
from prompt_builder import code_reviewer_prompt

SYSTEM = """You are a Code Reviewer Agent. Your role is to:
1. Review code for errors, bugs, and issues
2. Check code quality, best practices, and style
3. Suggest improvements and optimizations
4. Validate code correctness
5. Provide corrected code if needed

Be thorough and provide actionable feedback."""

def review_code(task, code_output, model):
    """Review and correct code output."""
    prompt = code_reviewer_prompt(task, code_output)
    return call_gemini(prompt, SYSTEM, model)
