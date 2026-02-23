# Tools & Environment

## Environment
- Platform: Telegram
- Language: Python 3.12
- Package Manager: uv
- OS: Windows

## API Keys & Services
- Telegram Bot Token: stored in .env as TELEGRAM_BOT_TOKEN
- Groq API Key: stored in .env as GROQ_API_KEY
- GitHub Token: to be added as GITHUB_TOKEN
- Notion Token: to be added as NOTION_TOKEN

## Bot Details
- Bot Name: Krish
- Bot Username: kanha_assistant_bot
- Created via: BotFather on Telegram

## LLM
- Provider: Groq
- Model: llama-3.3-70b-versatile
- Max Tokens: 1024

## Vector Database
- Provider: ChromaDB
- Type: Local, in-process
- Storage: .chroma/ folder in project root
- Embedding Model: sentence-transformers

## Memory Files
- MEMORY.md: long term curated memory
- USER.md: user identity and preferences
- SOUL.md: agent personality and behavior
- TOOLS.md: this file, environment notes
- memory/logs/: daily conversation logs

## Scheduled Tasks
- Scheduler: APScheduler
- State File: heartbeat-state.json
- Default Timezone: IST / GMT+5:30

## MCP Integrations
- GitHub MCP Server: mcp/github_server.py
- Notion MCP Server: mcp/notion_server.py

## Future Additions
- Mem0 for dynamic memory management
- Google Drive sync
- Email drafting via SMTP or Gmail API