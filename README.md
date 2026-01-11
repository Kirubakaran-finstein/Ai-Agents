# 🤖 AI Multi-Agent CLI System

A powerful, production-ready multi-agent system that uses Gemini AI to automatically complete tasks, create projects, analyze codebases, and generate documentation.

## ✨ Features

### Core Capabilities
- **Automatic Task Execution** - Just describe what you need, the system handles everything
- **Multi-Agent Architecture** - Supervisor, Planner, Executor, Reviewer, Code Reviewer, and Summarizer agents work together
- **Project Creation** - Automatically creates project folders, saves files, and runs projects
- **Code Analysis** - Analyzes existing codebases and generates comprehensive documentation
- **Smart Model Selection** - Automatically uses the best AI models with fallback to free tier
- **Persistent Memory** - Remembers previous tasks and learns from them
- **Error Recovery** - Automatic retry logic and error handling

### What It Can Do

1. **Create Projects**
   - Web applications (HTML/CSS/JavaScript)
   - Python applications
   - Any programming project
   - Automatically saves files and runs them

2. **Analyze Projects**
   - Analyze existing codebases
   - Generate documentation (MD files)
   - Create project summaries
   - Detect languages, dependencies, and structure

3. **Complete Tasks**
   - Write code
   - Create documentation
   - Build applications
   - Solve problems
   - Review and improve code

## 🚀 Quick Start

### Installation

1. **Clone or navigate to the project:**
   ```bash
   cd agents
   ```

2. **Run setup:**
   ```bash
   ./setup.sh
   ```
   
   Or manually:
   ```bash
   python3 -m venv gemini-system
   source gemini-system/bin/activate
   pip install -r requirements.txt
   ```

3. **Configure API Key:**
   
   Create `.env` file:
   ```bash
   cp .env.example .env
   nano .env
   ```
   
   Add your Gemini API key:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```
   
   Get your API key from: https://makersuite.google.com/app/apikey

4. **Run the system:**
   ```bash
   source gemini-system/bin/activate
   python main.py
   ```

## 📖 Usage

### Basic Usage

Simply enter your task when prompted:

```
📝 Task: make one xox game i need gui too
```

The system will:
1. Analyze your task
2. Create an execution plan
3. Generate code/files
4. Create project folder
5. Save all files
6. Run the project

### Example Tasks

**Create Projects:**
```
make a calculator app
create a todo list with react
build a REST API with Python Flask
make one xox game i need gui too
```

**Analyze Projects:**
```
analyze this project
summary of my project folder
create documentation for this codebase
```

**General Tasks:**
```
write a Python function to sort lists
explain how machine learning works
create a markdown documentation template
```

### Project Analysis

To analyze an existing project:

```
📝 Task: analyze this project
```

Or specify a project:
```
📝 Task: analyze projects/my-project-name
```

The system will:
- Analyze project structure
- Detect languages and technologies
- Find dependencies
- Generate `PROJECT_DOCUMENTATION.md`
- Create `SUMMARY.md`

## 📁 Project Structure

```
agents/
├── main.py                    # Entry point - run this
├── orchestrator.py            # Main workflow orchestrator
├── gemini_client.py           # Gemini API client
├── model_router.py            # Smart model selection
├── prompt_builder.py          # Prompt templates
├── file_manager.py            # File operations
├── project_analyzer.py         # Project analysis
├── documentation_generator.py  # Documentation generation
├── agents/                    # Agent modules
│   ├── supervisor.py         # Task supervision
│   ├── planner.py            # Planning agent
│   ├── executor.py           # Execution agent
│   ├── reviewer.py           # Review agent
│   ├── code_reviewer.py      # Code review agent
│   └── summarizer.py         # Summary agent
├── memory/                    # Persistent memory
│   └── memory.py             # SQLite storage
├── projects/                  # Generated projects (auto-created)
├── .env                       # Your API key (create this)
├── requirements.txt           # Python dependencies
├── setup.sh                   # Quick setup script
└── README.md                  # This file
```

## 🔧 Configuration

### Environment Variables

Create `.env` file:
```
GEMINI_API_KEY=your_gemini_api_key_here
```

### Model Selection

The system automatically:
- Uses best models (Gemini 3 Pro) for complex tasks
- Falls back to free tier models when quota is exceeded
- Handles model switching automatically

## 💡 How It Works

### Workflow

1. **Supervision** - Analyzes task and breaks it down
2. **Planning** - Creates detailed execution plan
3. **Execution** - Executes steps with retry logic
4. **Review** - Reviews output for correctness
5. **Code Review** - If code detected, runs specialized review
6. **Summary** - Generates execution summary
7. **Project Creation** - Saves files to project folder
8. **Execution** - Runs the project automatically

### Agents

- **Supervisor** - Splits tasks into manageable parts
- **Planner** - Creates step-by-step execution plans
- **Executor** - Executes tasks and generates output
- **Reviewer** - Reviews and corrects output
- **Code Reviewer** - Specialized code review and fixes
- **Summarizer** - Generates comprehensive summaries

## 📝 Output

### Simple Terminal Output

The system provides clean, simple output:

```
📝 Task: make a calculator app

🔍 Analyzing task...
📋 Planning...
⚙️  Executing...
🔍 Reviewing...

✅ COMPLETE
📁 Project: calculator-app_20260111_120000
📄 Files: index.html, style.css, script.js
```

### Generated Files

Projects are saved in `projects/` folder:
- All source files
- `README.md` - Project description
- Organized structure

## 🛠️ Troubleshooting

### API Key Issues
```
Error: GEMINI_API_KEY not found
```
**Solution:** Create `.env` file with your API key

### Import Errors
```
ModuleNotFoundError: No module named 'google.generativeai'
```
**Solution:** Run `pip install -r requirements.txt`

### Quota Errors
The system automatically falls back to free tier models. No action needed.

### Project Not Found
```
No project found to analyze
```
**Solution:** Specify project path or ensure projects exist in `projects/` folder

## 🎯 Best Practices

1. **Be Specific** - Clear tasks get better results
2. **Use Projects Folder** - All generated projects are saved there
3. **Check Documentation** - Generated projects include README files
4. **Analyze Before Modifying** - Use analysis feature to understand projects first

## 📚 Examples

### Create a Web Game
```
📝 Task: make one xox game i need gui too
```
Result: Complete Tic-Tac-Toe game with GUI, saved in projects folder

### Analyze Existing Project
```
📝 Task: analyze this project
```
Result: Comprehensive documentation and summary files

### Create Documentation
```
📝 Task: create documentation for this codebase
```
Result: `PROJECT_DOCUMENTATION.md` with full project details

## 🔐 Security

- Never commit `.env` file (already in `.gitignore`)
- Keep your API key secure
- Projects folder is for generated content only

## 📦 Dependencies

- `google-generativeai` - Gemini AI API
- `rich` - Terminal UI
- `sqlite-utils` - Database operations
- `python-dotenv` - Environment variables

## 🚀 Advanced Features

### Project Analysis
- Automatic language detection
- Dependency analysis
- Complexity assessment
- Entry point detection

### Documentation Generation
- Comprehensive project docs
- Setup instructions
- Usage examples
- Architecture details

### Smart Model Routing
- Automatic model selection
- Quota-aware fallback
- Error recovery

## 📄 License

This project is provided as-is for development use.

## 🤝 Contributing

This is a developer tool. Feel free to modify and enhance for your needs.

## 📞 Support

For issues:
1. Check `.env` file has correct API key
2. Ensure dependencies are installed
3. Check API quota limits
4. Review execution logs if needed

---

**Ready to use!** Just run `python main.py` and start giving tasks. 🚀
