import time
import os
from model_router import choose_model
from agents.supervisor import supervise
from agents.planner import plan
from agents.executor import execute
from agents.reviewer import review
from agents.code_reviewer import review_code
from agents.summarizer import summarize
from memory.memory import save_task, fetch_memory
from file_manager import setup_project, run_project
from project_analyzer import ProjectAnalyzer
from documentation_generator import generate_project_documentation, create_summary_md

class TaskOrchestrator:
    def __init__(self):
        self.execution_log = []
        self.max_retries = 3
        # Always use the best Pro model for all tasks
        self.complex_model = choose_model("complex")
        self.simple_model = choose_model("complex")  # Use best model for execution too
        self.project_created = False  # Track if project was actually created
    
    def log(self, message, level="INFO", verbose=False):
        """Log execution events - simplified output."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        self.execution_log.append(log_entry)
        
        # Only print important messages, skip verbose ones
        if verbose:
            return
        
        # Simplify messages
        simple_messages = {
            "START": "🚀 Starting...",
            "SUPERVISE": "🔍 Analyzing task...",
            "PLAN": "📋 Planning...",
            "EXECUTE": "⚙️  Executing...",
            "REVIEW": "🔍 Reviewing...",
            "CODE_REVIEW": "💻 Code review...",
            "SUMMARY": "📝 Summarizing...",
            "PROJECT": "📁 Creating project...",
            "RUN": "🚀 Running...",
            "MEMORY": "💾 Saving...",
            "SUCCESS": "✅ Complete",
            "ANALYZE": "📊 Analyzing...",
            "DOCS": "📝 Generating docs...",
        }
        
        # Use simple message or original
        display_msg = simple_messages.get(level, message)
        if level in ["INFO", "WARNING", "ERROR"]:
            # Only show important warnings/errors
            if level == "ERROR":
                print(f"❌ Error: {message}")
            elif level == "WARNING" and "quota" not in message.lower():
                return  # Skip quota warnings
        else:
            print(display_msg)
    
    def check_clarification_needed(self, response):
        """Check if agent is asking for clarification."""
        response_lower = response.lower()
        clarification_keywords = ["clarification needed", "unclear", "need more", "please specify", 
                                "what do you mean", "could you clarify", "?"]
        return any(keyword in response_lower for keyword in clarification_keywords)
    
    def is_project_analysis_task(self, task):
        """Check if task is about analyzing an existing project."""
        analysis_keywords = ["analyze", "summary", "documentation", "document", "explain", "describe", "review"]
        path_indicators = ["folder", "directory", "project", "codebase", "files in"]
        task_lower = task.lower()
        return any(keyword in task_lower for keyword in analysis_keywords) and \
               any(indicator in task_lower for indicator in path_indicators)
    
    def extract_project_path(self, task):
        """Extract project path from task description."""
        import re
        # Look for paths in the task
        path_patterns = [
            r'projects?[/\\][^\s]+',
            r'[^\s]+[/\\]projects?[/\\][^\s]+',
            r'["\']([^"\']+projects?[^"\']+)["\']',
        ]
        
        for pattern in path_patterns:
            matches = re.findall(pattern, task, re.IGNORECASE)
            if matches:
                path = matches[0].strip('"\'')
                if os.path.exists(path) or os.path.exists(os.path.join("projects", path)):
                    return path if os.path.exists(path) else os.path.join("projects", path)
        
        # Check if task mentions a project name
        projects_dir = "projects"
        if os.path.exists(projects_dir):
            for item in os.listdir(projects_dir):
                if item.lower() in task.lower():
                    full_path = os.path.join(projects_dir, item)
                    if os.path.isdir(full_path):
                        return full_path
        
        return None
    
    def _handle_project_analysis(self, task):
        """Handle project analysis and documentation generation."""
        try:
            project_path = self.extract_project_path(task)
            
            if not project_path:
                # Try to find the most recent project
                projects_dir = "projects"
                if os.path.exists(projects_dir):
                    projects = [os.path.join(projects_dir, d) for d in os.listdir(projects_dir) 
                               if os.path.isdir(os.path.join(projects_dir, d))]
                    if projects:
                        project_path = max(projects, key=os.path.getmtime)
                        self.log(f"Using most recent project: {project_path}", "INFO")
                    else:
                        return {
                            "status": "error",
                            "message": "No project found to analyze. Please specify a project path.",
                            "execution_log": self.execution_log
                        }
                else:
                    return {
                        "status": "error",
                        "message": "No projects directory found. Please specify a project path.",
                        "execution_log": self.execution_log
                    }
            
            if not os.path.exists(project_path):
                return {
                    "status": "error",
                    "message": f"Project path does not exist: {project_path}",
                    "execution_log": self.execution_log
                }
            
            self.log(f"Analyzing project", "ANALYZE")
            print(f"📂 {os.path.basename(project_path)}")
            
            # Analyze project
            analyzer = ProjectAnalyzer(project_path)
            analysis = analyzer.analyze()
            summary = analyzer.generate_summary()
            
            self.log("Analysis complete", "ANALYZE", verbose=True)
            
            # Generate documentation
            self.log("Generating documentation", "DOCS")
            try:
                doc_path, documentation = generate_project_documentation(project_path, "PROJECT_DOCUMENTATION.md")
                print(f"📄 Documentation: {os.path.basename(doc_path)}")
            except Exception as e:
                # Create summary instead
                doc_path = create_summary_md(project_path, task)
                documentation = f"Summary created"
            
            # Create quick summary
            summary_path = create_summary_md(project_path, task)
            
            self.log("Analysis complete", "SUCCESS")
            
            return {
                "status": "success",
                "final_output": f"Project Analysis Complete\n\n{summary}\n\nDocumentation: {doc_path}\nSummary: {summary_path}",
                "summary": f"Analyzed project at {project_path}\n- Files: {analysis['complexity']['total_files']}\n- Lines: {analysis['complexity']['total_lines']}\n- Languages: {', '.join(analysis['languages'].keys())}",
                "execution_log": self.execution_log,
                "project_path": project_path,
                "analysis": analysis
            }
            
        except Exception as e:
            self.log(f"Project analysis error: {str(e)}", "ERROR")
            return {
                "status": "error",
                "message": str(e),
                "execution_log": self.execution_log
            }
    
    def extract_steps(self, plan_text):
        """Extract numbered steps from plan text."""
        steps = []
        lines = plan_text.split('\n')
        for line in lines:
            line = line.strip()
            # Look for numbered steps (1., 2., Step 1, etc.)
            if (line and (line[0].isdigit() or line.lower().startswith('step'))):
                # Remove numbering and clean
                cleaned = line.split('.', 1)[-1].strip()
                if cleaned and len(cleaned) > 5:  # Filter out very short lines
                    steps.append(cleaned)
        return steps if steps else [plan_text]  # Fallback to full text if no steps found
    
    def run_task(self, task):
        """Main orchestrator function with full workflow."""
        try:
            self.execution_log = []
            self.log(f"Starting task: {task}", "START")
            
            # Check if this is a project analysis task
            if self.is_project_analysis_task(task):
                return self._handle_project_analysis(task)
            
            # Step 1: Supervision - Split and analyze task
            self.log("Supervising task", "SUPERVISE")
            try:
                supervision_result = supervise(task, self.complex_model)
                self.log("Supervision complete", "SUPERVISE", verbose=True)
                
                # Ignore clarification requests - proceed anyway
                if self.check_clarification_needed(supervision_result):
                    # Extract execution plan if it exists, otherwise use the whole result
                    if "EXECUTION PLAN:" in supervision_result:
                        supervision_result = supervision_result.split("EXECUTION PLAN:")[-1]
                    # Continue execution - don't return early
            except Exception as e:
                self.log(f"Supervision error: {str(e)}", "ERROR")
                # Continue with basic planning if supervision fails
            
            # Step 2: Planning - Create detailed plan
            self.log("Planning execution", "PLAN")
            plan_output = ""
            try:
                # Get previous context from memory
                memory_context = fetch_memory()
                context = f"Previous tasks: {str(memory_context[-3:]) if len(memory_context) > 0 else 'None'}"
                
                for chunk in plan(task, self.complex_model, context):
                    print(chunk, end="", flush=True)
                    plan_output += chunk
                print()  # New line after streaming
                
                # Ignore clarification requests - proceed anyway
                if self.check_clarification_needed(plan_output):
                    self.log("Note: Planning suggested clarification, but proceeding with execution anyway", "INFO")
                    # Extract execution plan if it exists
                    if "EXECUTION PLAN:" in plan_output:
                        plan_output = plan_output.split("EXECUTION PLAN:")[-1]
                    # Continue execution - don't return early
            except Exception as e:
                self.log(f"Planning error: {str(e)}", "ERROR")
                plan_output = f"Execute task: {task}"
            
            # Step 3: Extract and execute steps
            steps = self.extract_steps(plan_output)
            self.log(f"Executing {len(steps)} step(s)", "EXECUTE", verbose=True)
            
            execution_results = []
            previous_results = ""
            
            for i, step in enumerate(steps, 1):
                if len(steps) > 1:
                    print(f"Step {i}/{len(steps)}...")
                self.log(f"Executing step {i}", "EXECUTE", verbose=True)
                
                step_output = ""
                retry_count = 0
                success = False
                
                while retry_count < self.max_retries and not success:
                    try:
                        # Use complex model for execution to ensure high-quality outputs with proper code blocks
                        for chunk in execute(step, self.complex_model, previous_results):
                            print(chunk, end="", flush=True)
                            step_output += chunk
                        print()  # New line after streaming
                        success = True
                    except Exception as e:
                        error_msg = str(e)
                        # Check if it's a quota error - the client should handle fallback automatically
                        # but we log it for visibility
                        if "quota" in error_msg.lower() or "429" in error_msg:
                            self.log(f"Quota limit reached, system will auto-switch to free tier models", "INFO")
                        retry_count += 1
                        self.log(f"Execution error (attempt {retry_count}/{self.max_retries}): {str(e)[:100]}...", "WARNING")
                        if retry_count >= self.max_retries:
                            step_output = f"[Error executing step: {str(e)}]"
                            success = True  # Continue despite error
                
                execution_results.append({
                    "step": step,
                    "output": step_output
                })
                previous_results += f"\nStep {i} Output:\n{step_output}\n"
            
            # Combine all execution results
            combined_output = "\n\n".join([f"Step {i+1}: {r['output']}" for i, r in enumerate(execution_results)])
            
            # Step 4: Review output
            self.log("Reviewing output", "REVIEW")
            reviewed_output = ""
            try:
                for chunk in review(task, combined_output, self.complex_model):
                    print(chunk, end="", flush=True)
                    reviewed_output += chunk
                print()  # New line after streaming
            except Exception as e:
                error_msg = str(e)
                if "quota" in error_msg.lower() or "429" in error_msg:
                    self.log(f"Quota limit reached during review, system will auto-switch to free tier", "INFO")
                self.log(f"Review error: {str(e)[:100]}...", "WARNING")
                reviewed_output = combined_output
            
            # Step 5: Code Review (if code is detected)
            final_output = reviewed_output
            if any(keyword in reviewed_output.lower() for keyword in ["def ", "class ", "import ", "function", "code"]):
                self.log("Reviewing code", "CODE_REVIEW")
                try:
                    code_reviewed = review_code(task, reviewed_output, self.complex_model)
                    final_output = code_reviewed
                    self.log("Code review complete", "CODE_REVIEW")
                except Exception as e:
                    error_msg = str(e)
                    if "quota" in error_msg.lower() or "429" in error_msg:
                        self.log(f"Quota limit reached during code review, system will auto-switch to free tier", "INFO")
                    self.log(f"Code review error: {str(e)[:100]}...", "WARNING")
            
            # Step 6: Final Summary
            self.log("Generating summary", "SUMMARY")
            try:
                summary = summarize(task, "\n".join(self.execution_log), final_output, self.complex_model)
                self.log("Summary generated", "SUMMARY")
            except Exception as e:
                error_msg = str(e)
                if "quota" in error_msg.lower() or "429" in error_msg:
                    self.log(f"Quota limit reached during summary, system will auto-switch to free tier", "INFO")
                self.log(f"Summary error: {str(e)[:100]}...", "WARNING")
                summary = f"Task completed. Final output: {final_output[:200]}..."
            
            # Step 7: Create project folder and save files
            project_path = None
            saved_files = []
            self.project_created = False
            try:
                # Check if output contains code (likely a project)
                if any(keyword in final_output.lower() for keyword in 
                       ["```", "<!doctype", "<html", "def ", "function", "class ", "import ", "const ", "let "]):
                    self.log("Creating project", "PROJECT")
                    project_path, saved_files = setup_project(task, final_output, summary)
                    
                    # Verify project was created and has files
                    if project_path and saved_files and len(saved_files) > 0:
                        self.project_created = True
                        print(f"📁 Project: {os.path.basename(project_path)}")
                        print(f"📄 Files saved: {', '.join(saved_files)}")
                        
                        # Try to run the project
                        self.log("Running project", "RUN", verbose=True)
                        try:
                            run_success = run_project(project_path)
                        except Exception as run_error:
                            self.log(f"Project run warning: {str(run_error)[:100]}", "WARNING", verbose=True)
                    else:
                        self.log(f"Project creation resulted in no files. Output may not contain valid code.", "WARNING")
                        self.log(f"Saved files: {saved_files}, Path: {project_path}", "INFO", verbose=True)
                else:
                    self.log("Output does not appear to contain code (no project created)", "INFO")
            except Exception as e:
                self.log(f"Project creation error: {str(e)}", "WARNING", verbose=True)
            
            # Step 8: Save to memory
            try:
                save_task(task, final_output)
                self.log("Saved to memory", "MEMORY", verbose=True)
            except Exception as e:
                pass  # Silent fail for memory
            
            # Final verification - log actual completion status
            if not self.project_created and any(keyword in final_output.lower() for keyword in ["```", "def ", "function", "class "]):
                self.log("⚠️  Code was generated but project creation failed - review output above", "WARNING")
            
            self.log("Task completed", "SUCCESS")
            
            return {
                "status": "success",
                "final_output": final_output,
                "summary": summary,
                "project_created": self.project_created,
                "execution_log": self.execution_log,
                "steps_executed": len(steps),
                "project_path": project_path,
                "saved_files": saved_files
            }
            
        except Exception as e:
            self.log(f"Critical error: {str(e)}", "ERROR")
            return {
                "status": "error",
                "message": str(e),
                "execution_log": self.execution_log
            }

def run_task(task):
    """Main entry point for running a task."""
    orchestrator = TaskOrchestrator()
    return orchestrator.run_task(task)
