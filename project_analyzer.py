"""
Project Analyzer - Analyzes existing codebases and generates documentation.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple

class ProjectAnalyzer:
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.analysis = {}
    
    def analyze(self) -> Dict:
        """Perform comprehensive project analysis."""
        if not self.project_path.exists():
            raise ValueError(f"Project path does not exist: {self.project_path}")
        
        self.analysis = {
            "project_name": self.project_path.name,
            "project_path": str(self.project_path),
            "structure": self._analyze_structure(),
            "files": self._analyze_files(),
            "languages": self._detect_languages(),
            "dependencies": self._find_dependencies(),
            "entry_points": self._find_entry_points(),
            "documentation": self._check_documentation(),
            "complexity": self._assess_complexity()
        }
        
        return self.analysis
    
    def _analyze_structure(self) -> Dict:
        """Analyze project directory structure."""
        structure = {
            "directories": [],
            "file_count": 0,
            "total_size": 0
        }
        
        for root, dirs, files in os.walk(self.project_path):
            # Skip hidden directories and common ignore patterns
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'venv', 'env']]
            
            rel_root = os.path.relpath(root, self.project_path)
            if rel_root == '.':
                rel_root = '/'
            
            structure["directories"].append({
                "path": rel_root,
                "files": len(files),
                "subdirs": len(dirs)
            })
            
            structure["file_count"] += len(files)
            
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    structure["total_size"] += os.path.getsize(file_path)
                except:
                    pass
        
        return structure
    
    def _analyze_files(self) -> List[Dict]:
        """Analyze individual files."""
        files_info = []
        code_extensions = {
            '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h',
            '.html', '.css', '.scss', '.vue', '.php', '.rb', '.go', '.rs',
            '.swift', '.kt', '.dart', '.sh', '.bash', '.zsh'
        }
        
        for root, dirs, files in os.walk(self.project_path):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                file_path = Path(root) / file
                rel_path = file_path.relative_to(self.project_path)
                
                # Skip common ignore files
                if any(ignore in str(rel_path) for ignore in ['node_modules', '__pycache__', '.git', 'venv', 'env']):
                    continue
                
                ext = file_path.suffix.lower()
                if ext in code_extensions or file in ['Dockerfile', 'Makefile', 'package.json', 'requirements.txt', 'pom.xml']:
                    file_info = {
                        "path": str(rel_path),
                        "extension": ext,
                        "size": file_path.stat().st_size,
                        "language": self._detect_language(file_path),
                        "lines": self._count_lines(file_path)
                    }
                    files_info.append(file_info)
        
        return sorted(files_info, key=lambda x: x["lines"], reverse=True)
    
    def _detect_language(self, file_path: Path) -> str:
        """Detect programming language from file."""
        ext_map = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.jsx': 'React/JSX',
            '.tsx': 'React/TSX',
            '.java': 'Java',
            '.cpp': 'C++',
            '.c': 'C',
            '.h': 'C/C++ Header',
            '.html': 'HTML',
            '.css': 'CSS',
            '.scss': 'SCSS',
            '.vue': 'Vue.js',
            '.php': 'PHP',
            '.rb': 'Ruby',
            '.go': 'Go',
            '.rs': 'Rust',
            '.swift': 'Swift',
            '.kt': 'Kotlin',
            '.dart': 'Dart',
            '.sh': 'Shell',
            '.bash': 'Bash',
            '.zsh': 'Zsh'
        }
        
        ext = file_path.suffix.lower()
        return ext_map.get(ext, 'Unknown')
    
    def _count_lines(self, file_path: Path) -> int:
        """Count lines in a file."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return sum(1 for _ in f)
        except:
            return 0
    
    def _detect_languages(self) -> Dict[str, int]:
        """Detect all languages used in project."""
        languages = {}
        for file_info in self.analysis.get("files", []):
            lang = file_info.get("language", "Unknown")
            languages[lang] = languages.get(lang, 0) + 1
        return languages
    
    def _find_dependencies(self) -> Dict:
        """Find project dependencies."""
        dependencies = {
            "python": [],
            "node": [],
            "other": []
        }
        
        # Python dependencies
        req_file = self.project_path / "requirements.txt"
        if req_file.exists():
            try:
                with open(req_file, 'r') as f:
                    dependencies["python"] = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            except:
                pass
        
        # Node.js dependencies
        package_json = self.project_path / "package.json"
        if package_json.exists():
            try:
                import json
                with open(package_json, 'r') as f:
                    data = json.load(f)
                    deps = data.get("dependencies", {})
                    dev_deps = data.get("devDependencies", {})
                    dependencies["node"] = list(deps.keys()) + list(dev_deps.keys())
            except:
                pass
        
        return dependencies
    
    def _find_entry_points(self) -> List[str]:
        """Find potential entry points."""
        entry_points = []
        
        common_entry_points = [
            "main.py", "app.py", "index.py", "__main__.py",
            "index.js", "app.js", "main.js", "server.js",
            "index.html", "index.php",
            "main.java", "App.java",
            "main.cpp", "main.c"
        ]
        
        for file_info in self.analysis.get("files", []):
            filename = os.path.basename(file_info["path"])
            if filename.lower() in common_entry_points:
                entry_points.append(file_info["path"])
        
        return entry_points
    
    def _check_documentation(self) -> Dict:
        """Check existing documentation."""
        doc_files = []
        readme_files = []
        
        for root, dirs, files in os.walk(self.project_path):
            for file in files:
                if file.lower().endswith('.md'):
                    rel_path = os.path.relpath(os.path.join(root, file), self.project_path)
                    if 'readme' in file.lower():
                        readme_files.append(rel_path)
                    else:
                        doc_files.append(rel_path)
        
        return {
            "has_readme": len(readme_files) > 0,
            "readme_files": readme_files,
            "doc_files": doc_files,
            "total_docs": len(readme_files) + len(doc_files)
        }
    
    def _assess_complexity(self) -> Dict:
        """Assess project complexity."""
        files = self.analysis.get("files", [])
        total_lines = sum(f.get("lines", 0) for f in files)
        total_files = len(files)
        languages = len(self.analysis.get("languages", {}))
        
        complexity_score = 0
        if total_lines > 10000:
            complexity_score += 3
        elif total_lines > 5000:
            complexity_score += 2
        elif total_lines > 1000:
            complexity_score += 1
        
        if total_files > 50:
            complexity_score += 2
        elif total_files > 20:
            complexity_score += 1
        
        if languages > 3:
            complexity_score += 1
        
        complexity_level = "Simple"
        if complexity_score >= 5:
            complexity_level = "Very Complex"
        elif complexity_score >= 3:
            complexity_level = "Complex"
        elif complexity_score >= 2:
            complexity_level = "Moderate"
        
        return {
            "score": complexity_score,
            "level": complexity_level,
            "total_lines": total_lines,
            "total_files": total_files,
            "languages_count": languages
        }
    
    def generate_summary(self) -> str:
        """Generate a text summary of the analysis."""
        if not self.analysis:
            self.analyze()
        
        summary = f"""# Project Analysis: {self.analysis['project_name']}

## Overview
- **Path**: {self.analysis['project_path']}
- **Complexity**: {self.analysis['complexity']['level']} ({self.analysis['complexity']['score']}/7)
- **Total Files**: {self.analysis['complexity']['total_files']}
- **Total Lines**: {self.analysis['complexity']['total_lines']:,}

## Languages Used
"""
        for lang, count in self.analysis['languages'].items():
            summary += f"- **{lang}**: {count} files\n"
        
        summary += "\n## Entry Points\n"
        if self.analysis['entry_points']:
            for ep in self.analysis['entry_points']:
                summary += f"- `{ep}`\n"
        else:
            summary += "- No standard entry points found\n"
        
        summary += "\n## Dependencies\n"
        deps = self.analysis['dependencies']
        if deps['python']:
            summary += f"- **Python**: {len(deps['python'])} packages\n"
        if deps['node']:
            summary += f"- **Node.js**: {len(deps['node'])} packages\n"
        
        summary += "\n## Documentation\n"
        doc = self.analysis['documentation']
        summary += f"- README: {'Yes' if doc['has_readme'] else 'No'}\n"
        summary += f"- Documentation files: {doc['total_docs']}\n"
        
        return summary
