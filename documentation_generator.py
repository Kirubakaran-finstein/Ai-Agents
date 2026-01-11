"""
Documentation Generator - Creates comprehensive documentation for projects.
"""

import os
from pathlib import Path
from project_analyzer import ProjectAnalyzer
from gemini_client import call_gemini
from model_router import choose_model

def generate_project_documentation(project_path: str, output_file: str = "PROJECT_DOCUMENTATION.md"):
    """Generate comprehensive documentation for a project."""
    
    # Analyze the project
    analyzer = ProjectAnalyzer(project_path)
    analysis = analyzer.analyze()
    summary = analyzer.generate_summary()
    
    # Read key files for context
    key_files_content = _read_key_files(project_path, analysis)
    
    # Generate documentation using AI
    model = choose_model("complex")
    
    prompt = f"""
Analyze this project and create comprehensive documentation.

PROJECT ANALYSIS:
{summary}

KEY FILES CONTENT:
{key_files_content}

Create a detailed PROJECT_DOCUMENTATION.md file that includes:

1. **Project Overview**
   - What the project does
   - Main features and functionality
   - Technology stack

2. **Architecture**
   - Project structure
   - Key components
   - Design patterns used

3. **Setup & Installation**
   - Prerequisites
   - Installation steps
   - Configuration

4. **Usage**
   - How to run the project
   - Main commands
   - Examples

5. **File Structure**
   - Important files and their purposes
   - Directory organization

6. **Dependencies**
   - Required packages/libraries
   - Version information

7. **Development**
   - How to contribute
   - Code style
   - Testing

8. **Troubleshooting**
   - Common issues
   - Solutions

Format the output as a complete markdown document ready to save.
"""
    
    system = """You are a Technical Documentation Expert. Create clear, comprehensive, and professional documentation.
Focus on making it useful for developers who need to understand, use, or contribute to the project."""
    
    try:
        documentation = call_gemini(prompt, system, model)
        
        # Save to project folder
        output_path = os.path.join(project_path, output_file)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(documentation)
        
        return output_path, documentation
    except Exception as e:
        # Fallback to basic documentation
        basic_doc = f"""# {analysis['project_name']} - Documentation

{summary}

## Generated Documentation

This documentation was automatically generated. For more details, please review the source code.

## Project Structure

"""
        for file_info in analysis['files'][:20]:  # Top 20 files
            basic_doc += f"- `{file_info['path']}` ({file_info['language']}, {file_info['lines']} lines)\n"
        
        output_path = os.path.join(project_path, output_file)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(basic_doc)
        
        return output_path, basic_doc

def _read_key_files(project_path: str, analysis: dict, max_files: int = 10) -> str:
    """Read content from key files for context."""
    key_files = []
    
    # Prioritize entry points and important files
    entry_points = analysis.get('entry_points', [])
    for ep in entry_points[:3]:
        key_files.append(ep)
    
    # Add README if exists
    readme_files = analysis.get('documentation', {}).get('readme_files', [])
    if readme_files:
        key_files.append(readme_files[0])
    
    # Add largest/most important code files
    files = sorted(analysis.get('files', []), key=lambda x: x.get('lines', 0), reverse=True)
    for file_info in files[:max_files]:
        if file_info['path'] not in key_files:
            key_files.append(file_info['path'])
    
    content = ""
    for file_path in key_files[:max_files]:
        full_path = os.path.join(project_path, file_path)
        try:
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                file_content = f.read()
                # Limit file size
                if len(file_content) > 5000:
                    file_content = file_content[:5000] + "\n... (truncated)"
                content += f"\n\n=== {file_path} ===\n{file_content}\n"
        except Exception as e:
            content += f"\n\n=== {file_path} ===\n[Could not read: {str(e)}]\n"
    
    return content

def create_summary_md(project_path: str, task: str = "") -> str:
    """Create a quick summary markdown file."""
    analyzer = ProjectAnalyzer(project_path)
    analysis = analyzer.analyze()
    
    md_content = f"""# {analysis['project_name']} - Summary

Generated: {analysis.get('generated_at', 'N/A')}

## Quick Overview

- **Type**: {', '.join(analysis['languages'].keys()) if analysis['languages'] else 'Unknown'}
- **Complexity**: {analysis['complexity']['level']}
- **Files**: {analysis['complexity']['total_files']}
- **Lines of Code**: {analysis['complexity']['total_lines']:,}

## Main Languages

"""
    for lang, count in analysis['languages'].items():
        md_content += f"- {lang}: {count} files\n"
    
    md_content += "\n## Entry Points\n\n"
    if analysis['entry_points']:
        for ep in analysis['entry_points']:
            md_content += f"- `{ep}`\n"
    else:
        md_content += "- No standard entry points detected\n"
    
    md_content += "\n## Project Structure\n\n"
    for dir_info in analysis['structure']['directories'][:10]:
        md_content += f"- `{dir_info['path']}` ({dir_info['files']} files, {dir_info['subdirs']} subdirs)\n"
    
    output_path = os.path.join(project_path, "SUMMARY.md")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    return output_path
