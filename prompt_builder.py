def analyze_project_prompt(project_path, task=""):
    """Prompt for analyzing an existing project."""
    return f"""
Analyze the project at: {project_path}

Task: {task if task else "Generate summary and documentation"}

Analyze the project structure, codebase, and create comprehensive documentation.
Identify:
1. What the project does
2. Main components and architecture
3. Technologies used
4. How to set it up and run
5. Key features

Provide a detailed analysis and documentation.
"""

def supervisor_prompt(task):
    return f"""
Analyze the following task and create a detailed execution plan. DO NOT ask for clarification - make reasonable assumptions and proceed.

TASK: {task}

INSTRUCTIONS:
1. Break the task down into numbered, sequential sub-tasks.
2. Make reasonable assumptions for any missing details:
   - For GUI/web tasks: Use HTML/CSS/JavaScript
   - For desktop apps: Use Python with Tkinter or appropriate framework
   - For games: Make it playable and functional
   - For code projects: Create complete, runnable code
3. For each sub-task, indicate:
   - What needs to be done
   - Expected output/deliverable
   - Dependencies on other sub-tasks
4. Identify potential edge cases and challenges.
5. Estimate complexity (simple/complex) for each sub-task.

IMPORTANT: Always start with "EXECUTION PLAN:" followed by numbered steps. Never ask for clarification - just proceed with best practices and reasonable defaults.

Task: {task}
"""

def planner_prompt(task, context=""):
    return f"""
You are a Planning Agent. Analyze the task and create a detailed step-by-step plan.

TASK: {task}
{f'CONTEXT: {context}' if context else ''}

Create a clear, actionable plan with:
1. Sequential steps
2. Expected outcomes for each step
3. Dependencies between steps
4. Potential risks or edge cases

If the task is unclear, ask specific clarifying questions.
"""

def executor_prompt(step, previous_results=""):
    previous_section = f'PREVIOUS RESULTS:\n{previous_results}' if previous_results else ''
    return f"""
You are an Execution Agent. Execute the following step precisely and thoroughly.

STEP TO EXECUTE:
{step}

{previous_section}

INSTRUCTIONS:
1. Execute the step completely
2. Provide detailed output/results
3. If this involves code, provide complete, runnable code in markdown code blocks
4. For code files, use this format: ```language:filename.ext
   code here
   ```
5. For multiple files, provide each in a separate code block with filename
6. If you encounter errors, explain them and suggest fixes
7. Be thorough and accurate

IMPORTANT: When creating code files, always use the format:
```javascript:game.js
// code here
```

Or for HTML files:
```html:index.html
<!DOCTYPE html>
...
```

Execute now:
"""

def reviewer_prompt(task, output):
    return f"""
You are a Review Agent. Review the output against the original task and correct any mistakes.

ORIGINAL TASK:
{task}

OUTPUT TO REVIEW:
{output}

INSTRUCTIONS:
1. Check if the output fully addresses the task
2. Identify any errors, bugs, or issues
3. Verify correctness and completeness
4. Provide a corrected/improved version
5. Highlight what was fixed

Review and provide the corrected output:
"""

def code_reviewer_prompt(task, code_output):
    return f"""
You are a Code Reviewer Agent. Review the following code output for errors, best practices, and improvements.

ORIGINAL TASK:
{task}

CODE TO REVIEW:
{code_output}

INSTRUCTIONS:
1. Check for syntax errors, bugs, and logical issues
2. Review code quality, style, and best practices
3. Check for security vulnerabilities
4. Verify the code solves the task correctly
5. Provide corrected code with explanations
6. Suggest optimizations if applicable

Review and provide corrected code:
"""

def summarizer_prompt(task, execution_log, final_output):
    return f"""
You are a Summarizer Agent. Create a comprehensive summary of the task execution.

ORIGINAL TASK:
{task}

EXECUTION LOG:
{execution_log}

FINAL OUTPUT:
{final_output}

INSTRUCTIONS:
Create a summary that includes:
1. Task overview
2. Steps taken
3. Key deliverables/achievements
4. Issues encountered and resolutions
5. Final status (Success/Partial/Failed)
6. Recommendations or next steps

Provide a clear, structured summary:
"""
