# OmniMarkdown
A Python skill for building an AI-powered smart notebook — manage your Markdown notes with natural language, no coding required.
<img src=".assets/demo.png" width="200"/>

# What This Does
**OmniMarkdown** lets anyone store, query, and edit a personal Markdown notebook by simply typing plain English commands. It uses a "skill card" approach: instead of memorizing syntax or writing code, you click a button and describe what you want in natural language.

# Key Features
- **Zero Frontend**: Runs entirely in Python with Gradio. No React, no npm, no build tools.
- **Skill-Card Interface**: Four one-click skill buttons auto-fill the right command prefix, so non-technical users never need to remember syntax.
- **Plain English Editing**: Add, delete, or modify notes by describing your intent. The AI figures out the rest.
- **Extensible by Design**: Every skill is a plain Markdown file. Add a new `.md` file to the `skills/` folder and it appears as a button automatically — no Python changes needed.
- **Local & Private**: Everything runs on your own machine. Notes are stored as a plain .md file you always own.
- **LLM Agnostic**: Works with DeepSeek, OpenAI, or any OpenAI-compatible endpoint. Just change one line in the config.

# Installation
## 1. Clone or download the project
```
git clone https://github.com/Bubble-OoO/OmniMarkdown.git
cd OmniMarkdown
```
## 2. Install dependencies
```
pip install -r requirements.txt
```
## 3. Add your API key
```
Edit llm_config.json and replace YOUR_API_KEY_HERE
```

Then, the browser opens automatically at `http://localhost:7860`.

## Usage

### Query Your Notes
```
? What is my GitHub password?
? What tasks are still pending this week?
? Summarize the key information in my notes
```

### Edit Your Notes
```
! add: team meeting tomorrow at 3 PM
! delete: remove all completed tasks
! modify: change the GitHub password from 123456 to newPass@2024
```

### Or Just Click

Hit a skill button — **Query**, **Add**, **Delete**, or **Modify** — and the prefix is filled in automatically. Just finish the sentence.

## Project Structure
```
OmniMarkdown/
├── app.py               # Main application (Gradio UI)
├── skills_loader.py     # Skill engine (parses Markdown skill files)
├── llm_client.py        # LLM wrapper (OpenAI-compatible)
├── requirements.txt
│
├── llm_config.json      # API key and model config
│
├── skills/              # ⭐ Skill definitions — edit or add freely
│   ├── query.md         # 🔍 Query notes
│   ├── add.md           # ✏️  Add content
│   ├── delete.md        # 🗑️  Delete content
│   └── modify.md        # 🔧 Modify content
│
└── user_files/
    └── notebook.md      # Your note file (auto read/write)
