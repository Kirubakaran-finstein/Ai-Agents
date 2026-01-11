import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gemini_client import call_gemini
from prompt_builder import summarizer_prompt

SYSTEM = """You are a Summarizer Agent. Your role is to:
1. Create comprehensive summaries of completed work
2. Highlight key achievements and deliverables
3. Note any issues encountered and how they were resolved
4. Provide a clear final status report

Be concise but thorough."""

def summarize(task, execution_log, final_output, model):
    """Generate a comprehensive summary of the task execution."""
    prompt = summarizer_prompt(task, execution_log, final_output)
    return call_gemini(prompt, SYSTEM, model)
