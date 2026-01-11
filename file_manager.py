"""
File Manager - Handles project creation, file extraction, and execution.
"""

import os
import re
import subprocess
import shutil
from datetime import datetime
from pathlib import Path

PROJECTS_DIR = "projects"

def create_project_folder(task_name):
    """Create a project folder with a sanitized name."""
    # Sanitize task name for folder name
    safe_name = re.sub(r'[^\w\s-]', '', task_name)
    safe_name = re.sub(r'[-\s]+', '-', safe_name)
    safe_name = safe_name[:50].strip('-').lower()
    
    # Add timestamp to avoid conflicts
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder_name = f"{safe_name}_{timestamp}"
    
    project_path = os.path.join(PROJECTS_DIR, folder_name)
    os.makedirs(project_path, exist_ok=True)
    
    return project_path, folder_name

def extract_code_blocks(text):
    """Extract code blocks from markdown or plain text with improved detection."""
    files = {}
    extracted_codes = set()  # Track already extracted code to avoid duplicates
    
    # Pattern 1: Markdown code blocks with language and filename
    # ```javascript:filename.js
    # code
    # ```
    pattern1 = r'```(\w+)?:?([^\n`]+)?\n(.*?)```'
    matches1 = re.finditer(pattern1, text, re.DOTALL)
    for match in matches1:
        lang = match.group(1) or 'text'
        filename = match.group(2) or f'code.{lang}'
        code = match.group(3).strip()
        filename = filename.strip().strip('`').strip()
        if filename and code and len(code) > 10:  # Require minimum code length
            files[filename] = code
            extracted_codes.add(code[:100])  # Track first 100 chars
    
    # Pattern 2: Standard markdown code blocks (improved)
    # Better detection that handles more markdown variations
    pattern2 = r'```\s*(\w+)?\s*\n(.*?)```'
    matches2 = re.finditer(pattern2, text, re.DOTALL)
    for match in matches2:
        lang = match.group(1) or 'text'
        code = match.group(2).strip()
        if code and len(code) > 10:  # Require minimum code length
            # Skip if we've already extracted similar code
            if not any(code[:100] in extracted for extracted in extracted_codes):
                # Try to infer filename from language
                ext_map = {
                    'javascript': 'script.js',
                    'js': 'script.js',
                    'html': 'index.html',
                    'css': 'style.css',
                    'python': 'script.py',
                    'py': 'script.py',
                    'java': 'Main.java',
                    'cpp': 'main.cpp',
                    'c': 'main.c',
                    'json': 'data.json',
                    'xml': 'data.xml',
                    'yaml': 'config.yaml',
                    'yml': 'config.yml',
                    'html5': 'index.html',
                    'jsx': 'component.jsx',
                    'tsx': 'component.tsx',
                    'typescript': 'script.ts',
                    'ts': 'script.ts',
                }
                filename = ext_map.get(lang.lower(), f'code.{lang}')
                if filename not in files:
                    files[filename] = code
                    extracted_codes.add(code[:100])
    
    # Pattern 3: Look for file creation patterns in text
    # "Create file X with content:"
    file_pattern = r'(?:create|save|write|file|filename|path)[\s:]+([^\s\n]+\.\w+)[\s\n]+(?:with|content|code|below)[\s:]*\n(.*?)(?=\n\n|\n[A-Z]|\Z)'
    matches3 = re.finditer(file_pattern, text, re.IGNORECASE | re.DOTALL)
    for match in matches3:
        filename = match.group(1).strip()
        content = match.group(2).strip()
        if filename and content and filename not in files:
            files[filename] = content
    
    # Pattern 4: HTML files (often standalone)
    if '<!DOCTYPE html>' in text or '<html' in text:
        html_match = re.search(r'(<!DOCTYPE html>.*?</html>)', text, re.DOTALL | re.IGNORECASE)
        if html_match:
            if 'index.html' not in files:
                files['index.html'] = html_match.group(1).strip()
    
    return files

def save_files_to_project(project_path, code_output):
    """Extract code from output and save to project folder."""
    files = extract_code_blocks(code_output)
    
    saved_files = []
    for filename, content in files.items():
        # Clean filename
        filename = os.path.basename(filename)  # Remove any path
        file_path = os.path.join(project_path, filename)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            saved_files.append(filename)
        except Exception as e:
            print(f"Error saving {filename}: {e}")
    
    return saved_files

def create_readme(project_path, task, summary=""):
    """Create a README.md for the project."""
    readme_content = f"""# Project: {task}

Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Description
This project was automatically generated by the Gemini Multi-Agent CLI System.

## Task
{task}

## Summary
{summary if summary else "No summary available."}

## Files
"""
    readme_path = os.path.join(project_path, "README.md")
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    return readme_path

def run_project(project_path):
    """Attempt to run the project based on file types."""
    files = os.listdir(project_path)
    
    # Check for HTML file
    html_files = [f for f in files if f.endswith('.html')]
    if html_files:
        html_file = html_files[0]
        html_path = os.path.join(project_path, html_file)
        # Silent execution
        try:
            # Try to open in default browser
            if shutil.which('xdg-open'):
                subprocess.Popen(['xdg-open', html_path])
            elif shutil.which('open'):
                subprocess.Popen(['open', html_path])
            elif shutil.which('start'):
                subprocess.Popen(['start', html_path], shell=True)
            else:
                print(f"Please open {html_path} in your browser")
            return True
        except Exception as e:
            print(f"Could not open browser: {e}")
            print(f"Please open {html_path} manually in your browser")
            return True
    
    # Check for Python file
    py_files = [f for f in files if f.endswith('.py')]
    if py_files:
        py_file = py_files[0]
        py_path = os.path.join(project_path, py_file)
        try:
            result = subprocess.run(['python3', py_path], 
                                  cwd=project_path, 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=30)
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(result.stderr)
            return result.returncode == 0
        except Exception as e:
            print(f"Error running Python: {e}")
            return False
    
    # Check for Node.js/JavaScript
    js_files = [f for f in files if f.endswith('.js') and not f.endswith('.min.js')]
    if js_files:
        js_file = js_files[0]
        js_path = os.path.join(project_path, js_file)
        try:
            result = subprocess.run(['node', js_path], 
                                  cwd=project_path, 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=30)
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(result.stderr)
            return result.returncode == 0
        except Exception as e:
            print(f"Error running Node.js: {e}")
            return False
    
    return False

def setup_project(task, code_output, summary=""):
    """Complete project setup: create folder, save files, create README."""
    project_path, folder_name = create_project_folder(task)
    
    # Save files from code output with debug info
    saved_files = save_files_to_project(project_path, code_output)
    
    # Debug: Check if any files were actually saved
    if not saved_files:
        # No files extracted - this is a problem
        print(f"⚠️  Warning: No code files were extracted from the output")
        print(f"    Looking for code patterns in output...")
        
        # Check what code indicators exist
        indicators = []
        if "```" in code_output:
            indicators.append("markdown code blocks (```)")
        if "<!DOCTYPE" in code_output or "<html" in code_output:
            indicators.append("HTML tags")
        if "def " in code_output or "class " in code_output:
            indicators.append("Python syntax")
        if "function " in code_output or "const " in code_output:
            indicators.append("JavaScript syntax")
        
        if indicators:
            print(f"    Found: {', '.join(indicators)}")
            print(f"    Try checking the output format - files may not be properly formatted")
    
    # Create README regardless
    readme_path = create_readme(project_path, task, summary)
    
    return project_path, saved_files
