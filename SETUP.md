# Setup Guide

For complete documentation, see [README.md](README.md)

## Quick Setup

### 1. Run Setup Script
```bash
./setup.sh
```

### 2. Configure API Key
Edit `.env` file and add your Gemini API key:
```
GEMINI_API_KEY=your_api_key_here
```

Get your API key from: https://makersuite.google.com/app/apikey

### 3. Run
```bash
source gemini-system/bin/activate
python main.py
```

## Manual Setup

### Step 1: Virtual Environment
```bash
python3 -m venv gemini-system
source gemini-system/bin/activate
pip install --upgrade pip
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Configure API Key
Create `.env` file:
```bash
echo "GEMINI_API_KEY=your_api_key_here" > .env
```

### Step 4: Run
```bash
python main.py
```

## Troubleshooting

### API Key Not Found
- Ensure `.env` file exists in project root
- Check API key is correct
- Verify no extra spaces in `.env` file

### Import Errors
- Activate virtual environment: `source gemini-system/bin/activate`
- Reinstall dependencies: `pip install -r requirements.txt`

### Permission Denied (setup.sh)
```bash
chmod +x setup.sh
./setup.sh
```

## Project Structure

```
agents/
├── main.py              # Run this
├── orchestrator.py     # Core logic
├── agents/             # Agent modules
├── memory/             # Database
├── projects/           # Generated projects
└── .env                # Your API key (create this)
```

For more details, see [README.md](README.md)
