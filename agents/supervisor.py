import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gemini_client import call_gemini
from prompt_builder import supervisor_prompt

SYSTEM = """You are a Supervisor Agent. Your role is to:
1. Analyze incoming tasks
2. Break them into clear, actionable sub-tasks
3. Determine which agent should handle each sub-task
4. Make reasonable assumptions and proceed - NEVER ask for clarification
5. Create a structured execution plan

Always proceed with execution. Make reasonable assumptions:
- GUI/web = HTML/CSS/JavaScript
- Desktop = Python with appropriate framework
- Games = Make them playable and fun
- Code = Complete, runnable, production-ready

Return your response starting with "EXECUTION PLAN:" followed by numbered steps."""

def supervise(task, model):
    """Supervise and split task into manageable sub-tasks."""
    prompt = supervisor_prompt(task)
    return call_gemini(prompt, SYSTEM, model)
