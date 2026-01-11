import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gemini_client import stream_gemini
from prompt_builder import planner_prompt

SYSTEM = """You are a Planning Agent. Your role is to:
1. Analyze tasks and break them into clear steps
2. Identify dependencies and sequencing
3. Consider edge cases and potential issues
4. Create actionable execution plans"""

def plan(task, model, context=""):
    return stream_gemini(planner_prompt(task, context), SYSTEM, model)
