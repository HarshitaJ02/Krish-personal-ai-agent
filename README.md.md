# 🤖 Krish - Production-Grade AI Agent on Telegram

<div align="center">

![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)
![Telegram](https://img.shields.io/badge/Telegram-Bot%20API-blue.svg)
![Groq](https://img.shields.io/badge/LLM-Groq%20%7C%20Llama%203.3-green.svg)
![ChromaDB](https://img.shields.io/badge/Vector%20DB-ChromaDB-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

**A custom-built ReAct AI assistant with memory, RAG, tool orchestration, and scheduled jobs — engineered from scratch without agent frameworks.**

[Features](#-features) • [Architecture](#-architecture) • [Installation](#-installation) • [Usage](#-usage) • [Tools](#-available-tools) • [Configuration](#%EF%B8%8F-configuration)

</div>

---

## 🌟 What Is Krish?

**Krish** is a personal AI agent that lives inside Telegram. It holds conversations, remembers you, searches the web, manages your GitHub repos, writes to Notion, and schedules reminders — all while chaining multi-step tasks autonomously.

### Why Krish Stands Out

- **🧠 Built from Scratch** - No LangChain, AutoGen, or pre-built frameworks. Every layer — the reasoning loop, memory system, vector retrieval, intent classification, and tool execution — was designed and implemented from the ground up.

- **🎯 ReAct Reasoning** - Uses a Reason + Act loop where the LLM thinks through tasks step-by-step, selects the right tools, executes them, and learns from results before responding.

- **💾 Persistent Memory** - Remembers your preferences, context from past conversations, and important details across sessions using file-based memory and vector search.

- **🔍 RAG-Powered Context** - Indexes all conversation logs with embeddings, allowing semantic search over your entire chat history.

- **⚡ Intelligent Routing** - Classifies every message (casual, tool-requiring, knowledge-based, or personal) and dynamically adjusts context budgets to stay within token limits.

---

## ✨ Features

### 🗣️ **Conversational Intelligence**
- Natural language understanding with **Llama 3.3 70B** via Groq
- Multi-turn conversations with context awareness
- Personality-driven responses (sharp, direct, thoughtful, and polite)
- Detects and handles ambiguous queries gracefully

### 🧠 **Memory System**
- **Short-term**: In-memory conversation history (last 20 messages)
- **Long-term**: File-based storage in `MEMORY.md`, `USER.md`, and `SOUL.md`
- **Vector Memory**: ChromaDB-powered semantic search over all past conversations
- Automatically extracts and persists important information

### 🛠️ **Tool Orchestration**
Krish can execute actions across multiple platforms:

| Tool | Description |
|------|-------------|
| 🌐 **Web Search** | Real-time web search via SerpAPI |
| 💻 **GitHub Integration** | List repos, create issues, manage projects |
| 📝 **Notion** | Append notes, create pages, sync summaries |
| ⏰ **Reminders** | Natural language time-based reminders |
| 💬 **Telegram Messaging** | Send messages to known chats/groups |

### 📊 **Observability**
- Conversation logs stored daily in `memory/logs/`
- Metrics tracking (tool usage, context size, routing decisions)
- Automatic log indexing on startup

### 🕐 **Scheduled Jobs**
- Morning briefings with news and reminders
- Drink water reminders at intervals
- Cricket score updates
- Channel activity summaries
- Scheduled message posting

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Telegram User                          │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    Bot Handlers Layer                       │
│  /start  /help  /memory  /clear  + message handling        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    Agent Core (ReAct Loop)                  │
│                                                             │
│  1. Classify message (casual/tool/knowledge/personal)       │
│  2. Build system prompt with appropriate context            │
│  3. Execute ReAct reasoning loop:                           │
│     ┌──────────────────────────────────────────┐           │
│     │  LLM thinks → selects tool → executes    │           │
│     │  → observes result → decides next action │           │
│     └──────────────────────────────────────────┘           │
│  4. Return final response                                   │
│  5. Log to memory, extract if needed                        │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┬─────────────┐
         ▼               ▼               ▼             ▼
    ┌────────┐     ┌─────────┐     ┌─────────┐   ┌──────────┐
    │  LLM   │     │  Tools  │     │ Memory  │   │   RAG    │
    │ (Groq) │     │ Executor│     │  Store  │   │(ChromaDB)│
    └────────┘     └─────────┘     └─────────┘   └──────────┘
         │               │               │             │
         │          ┌────┴────┐          │             │
         │          │         │          │             │
         ▼          ▼         ▼          ▼             ▼
    Llama 3.3   GitHub   SerpAPI    SOUL.md      Embeddings
     70B/8B     Notion   Telegram   USER.md      (all-MiniLM)
               Reminders          MEMORY.md
```

### Core Components

#### 1. **Intent Classifier** (`agent/classifier.py`)
- Uses **Llama 3.1 8B Instant** for fast classification
- Returns scores for: `casual`, `tool`, `knowledge`, `personal`
- Determines whether tools should be invoked

#### 2. **Context Builder** (`agent/context.py`)
- Dynamically constructs system prompts based on classification scores
- Applies token budgets per category:
  - Casual: 400 tokens
  - Tool: 600 tokens
  - Knowledge: 2000 tokens
  - Personal: 3000 tokens
- Loads relevant memory chunks and personality guidelines from `SOUL.md`

#### 3. **ReAct Loop** (`agent/core.py`)
- Implements the Reason-Act-Observe cycle
- Maximum 5 tool iterations to prevent infinite loops
- Handles XML fallback parsing when LLM hallucinates malformed tool calls
- Logs all decisions to `memory/logs/metrics.jsonl`

#### 4. **Tool Execution** (`agent/tools.py`)
- Each tool follows OpenAI function calling schema
- Tools are filtered based on message keywords and intent scores
- Executes asynchronously with proper error handling
- Returns structured results to the LLM

#### 5. **Memory Store** (`memory/store.py`)
- Reads/writes to `SOUL.md` (personality), `USER.md` (profile), `MEMORY.md` (facts)
- Daily conversation logs in `memory/logs/YYYY-MM-DD.md`
- Chunks memory by relevance to avoid context bloat
- Appends important extractions automatically

#### 6. **RAG System** (`rag/`)
- **Indexer**: Embeds all daily logs using `sentence-transformers`
- **Retriever**: Semantic search over ChromaDB for context recall
- Auto-syncs on bot startup
- Deduplicates based on message IDs

---

## 🚀 Installation

### Prerequisites
- **Python 3.12+**
- **uv** (Python package manager) - Install via:
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

### Step 1: Clone the Repository
```bash
git clone https://github.com/yourusername/telegram-ai-agent.git
cd telegram-ai-agent
```

### Step 2: Install Dependencies
```bash
uv sync
```

This will install:
- `python-telegram-bot` - Telegram Bot API wrapper
- `groq` - Groq API client for LLM inference
- `chromadb` - Vector database for RAG
- `sentence-transformers` - Embedding models
- `apscheduler` - Cron-like job scheduling
- `google-search-results` (SerpAPI) - Web search
- `tiktoken` - Token counting
- `requests` - HTTP client

### Step 3: Configure Environment Variables

Create a `.env` file in the root directory:

```env
# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather
TELEGRAM_CHAT_ID=your_personal_chat_id
TELEGRAM_GROUP_ID=your_group_chat_id  # Optional

# LLM (Groq)
GROQ_API_KEY=your_groq_api_key

# Web Search
SERPAPI_KEY=your_serpapi_key

# GitHub (Optional)
GITHUB_TOKEN=your_github_personal_access_token

# Notion (Optional)
NOTION_TOKEN=your_notion_integration_token
NOTION_PAGE_ID=your_notion_page_id
```

#### How to Get API Keys:

<details>
<summary><b>🤖 Telegram Bot Token</b></summary>

1. Open Telegram and search for `@BotFather`
2. Send `/newbot` and follow the prompts
3. Copy the token provided
4. Get your chat ID by messaging `@userinfobot`
</details>

<details>
<summary><b>⚡ Groq API Key</b></summary>

1. Go to [console.groq.com](https://console.groq.com)
2. Sign up / log in
3. Navigate to API Keys section
4. Create a new key
</details>

<details>
<summary><b>🔍 SerpAPI Key</b></summary>

1. Visit [serpapi.com](https://serpapi.com)
2. Sign up for a free account (100 searches/month free)
3. Copy your API key from the dashboard
</details>

<details>
<summary><b>💻 GitHub Token (Optional)</b></summary>

1. Go to GitHub Settings → Developer Settings → Personal Access Tokens
2. Generate new token (classic)
3. Grant `repo` and `user` scopes
</details>

<details>
<summary><b>📝 Notion Token (Optional)</b></summary>

1. Go to [notion.so/my-integrations](https://www.notion.so/my-integrations)
2. Create a new integration
3. Copy the Internal Integration Token
4. Share a Notion page with your integration
5. Copy the page ID from the URL
</details>

---

## 🎯 Usage

### Start the Bot
```bash
uv run python main.py
```

You should see:
```
Syncing ChromaDB with latest logs...
Indexed X messages. Total: Y
Scheduler started!
Krish is running ...
```

### Commands

| Command | Description |
|---------|-------------|
| `/start` | Introduction and feature overview |
| `/help` | Show available commands |
| `/memory` | Display current memory state |
| `/clear` | Clear conversation history (keeps logs) |

### Example Interactions

#### 💬 Casual Conversation
```
You: Hey, how's it going?
Krish: All good! What's on your mind?
```

#### 🌐 Web Search
```
You: What's the weather in Bengaluru today?
Krish: [executes web_search]
Based on the latest data, Bengaluru is at 24°C with partly cloudy skies...
```

#### 💻 GitHub Integration
```
You: List my GitHub repos
Krish: [executes github_list_repos]
Here are your repositories:
- telegram-ai-agent: A production-grade AI assistant...
- portfolio-site: Personal portfolio built with Next.js...
```

```
You: Create a GitHub issue in telegram-ai-agent titled "Add error handling" 
     with description "Need better error messages when API calls fail"
Krish: [executes github_create_issue]
Issue created: https://github.com/yourusername/telegram-ai-agent/issues/42
```

#### 📝 Notion Integration
```
You: Save this to Notion: "Idea for next project - build a habit tracker app"
Krish: [executes notion_append]
Saved to your Krish Notes page. You can find it at notion.so/[page_id]
```

#### ⏰ Reminders
```
You: Remind me to call Mom tomorrow at 6pm
Krish: [executes set_reminder]
Got it! I'll remind you tomorrow at 6:00 PM to call Mom.
```

#### 🧠 Memory Recall
```
You: What did we discuss about my AI engineering goals?
Krish: [retrieves from MEMORY.md and RAG]
Based on our past conversations, you're working towards becoming an AI Engineer...
```

---

## 🛠️ Available Tools

### 1. **web_search**
Searches the web using SerpAPI and returns the top 3 results.

**Triggers**: Weather queries, news, sports scores, current events, "what's happening", "today"

**Example**:
```python
{
  "query": "latest news on AI regulation"
}
```

### 2. **github_list_repos**
Lists all GitHub repositories for the configured user.

**Triggers**: "show repos", "list repositories", "my GitHub projects"

### 3. **github_create_issue**
Creates a new issue in a specified repository.

**Triggers**: "create issue", "add bug", "raise issue in [repo]"

**Example**:
```python
{
  "repo": "telegram-ai-agent",
  "title": "Fix memory leak in RAG indexer",
  "body": "The indexer consumes too much RAM when processing large log files..."
}
```

### 4. **notion_append**
Appends a paragraph to an existing Notion page.

**Triggers**: "save to Notion", "add note", "write this down"

**Example**:
```python
{
  "content": "Meeting notes: discussed new feature roadmap for Q2"
}
```

### 5. **notion_create_page**
Creates a new Notion page with title and content.

**Triggers**: "create Notion page", "new document in Notion"

**Example**:
```python
{
  "title": "Weekly Review - March 2026",
  "content": "Key accomplishments:\n- Shipped v2.0...\n"
}
```

### 6. **set_reminder**
Schedules a time-based reminder using natural language parsing.

**Triggers**: "remind me", "set reminder", "don't forget"

**Example**:
```python
{
  "reminder_text": "call dentist at 3pm tomorrow"
}
```

### 7. **send_telegram_message**
Sends a message to a known chat or group.

**Triggers**: "send message to", "announce to group", "tell [recipient]"

**Example**:
```python
{
  "recipient": "group",
  "message": "Team standup in 10 minutes!"
}
```

---

## ⚙️ Configuration

### `config.py`

Key settings you can adjust:

```python
# Memory & Context
MAX_HISTORY = 20              # Conversation turns to keep in memory
RECENT_LOGS_DAYS = 1          # Days of logs to include in context
MAX_CONTEXT_TOKENS = 4000     # Hard limit on system prompt size
MAX_TOOL_ITERATIONS = 5       # Max tool calls per query

# LLM Models
MODEL_MAIN = "llama-3.3-70b-versatile"      # Main reasoning model
MODEL_CLASSIFIER = "llama-3.1-8b-instant"   # Fast intent classifier

# Context Budgets (tokens allocated per category)
CONTEXT_BUDGETS = {
    "casual":    400,   # Lightweight for chit-chat
    "tool":      600,   # Moderate for tool orchestration
    "knowledge": 2000,  # Heavy for factual queries
    "personal":  3000,  # Maximum for personal context
}

# GitHub
GITHUB_USERNAME = "your_github_username"

# Notion
NOTION_VERSION = "2022-06-28"  # Notion API version
```

### Customizing Personality

Edit `SOUL.md` to change Krish's personality, tone, and behavior:

```markdown
## Tone & Personality
- Sharp, direct, thoughtful and polite
- Speaks like a knowledgeable friend, never like a corporate chatbot
- Uses analogies and examples naturally
- Has a playful side but knows when to be serious
```

### User Profile

Edit `USER.md` to add personal context:

```markdown
# User Profile
- Name: Hash
- Goal: Become an AI Engineer
- Interests: Cricket, AI/ML, building production systems
- Current projects: telegram-ai-agent, personal portfolio
```

### Memory

`MEMORY.md` is automatically updated by the agent, but you can manually add important facts:

```markdown
- Hash prefers concise explanations unless depth is requested
- Hash is working on a production-grade AI agent
- Hash uses Python, Telegram, and Groq for this project
```

---

## 📊 Observability & Debugging

### Conversation Logs
All conversations are stored in `memory/logs/YYYY-MM-DD.md`:

```markdown
[14:32:05] user: What's the weather today?
[14:32:07] assistant: Based on the latest data, it's 24°C and partly cloudy...
```

### Metrics Tracking
Every interaction is logged to `memory/logs/metrics.jsonl`:

```json
{
  "ts": "2026-03-15T14:32:05",
  "msg": "What's the weather today?",
  "scores": {"casual": 0.1, "tool": 0.8, "knowledge": 0.3, "personal": 0.1},
  "tools_used": ["web_search"],
  "ctx_chars": 1250
}
```

### Analyzing Patterns

Use `jq` to analyze metrics:

```bash
# Tool usage distribution
cat memory/logs/metrics.jsonl | jq -r '.tools_used[]' | sort | uniq -c

# Average context size per category
cat memory/logs/metrics.jsonl | jq -r '[.scores | to_entries | max_by(.value) | .key] | .[0]' | sort | uniq -c
```

### ChromaDB Inspection

Query the vector database directly:

```python
from rag.retriever import search_memory

results = search_memory("What did I say about my AI goals?", top_k=5)
for result in results:
    print(f"{result['date']} - {result['content']}")
```

---

## 🧪 Testing

### Manual Testing
```bash
# Test RAG retrieval
uv run python test_retrieval.py

# Test individual tools
uv run python -c "from agent.tools import web_search; print(web_search('Python news'))"
```

### Run the Classifier
```bash
uv run python -c "from agent.classifier import classify_message; print(classify_message('What\\'s the weather?'))"
```

---

## 🗂️ Project Structure

```
telegram-ai-agent/
│
├── agent/                    # Core agent logic
│   ├── classifier.py         # Intent classification (casual/tool/knowledge/personal)
│   ├── context.py            # System prompt builder with dynamic context budgets
│   ├── core.py               # ReAct reasoning loop
│   ├── llm.py                # Groq LLM client wrapper
│   ├── memory_ops.py         # Memory extraction and checking logic
│   └── tools.py              # Tool definitions and execution
│
├── bot/                      # Telegram bot handlers
│   └── handlers.py           # Command and message handlers
│
├── memory/                   # Persistent storage
│   ├── logs/                 # Daily conversation logs
│   │   ├── YYYY-MM-DD.md     # Daily chat transcript
│   │   └── metrics.jsonl     # Observability metrics
│   └── store.py              # File-based memory operations
│
├── rag/                      # Vector retrieval system
│   ├── indexer.py            # Embeds logs into ChromaDB
│   └── retriever.py          # Semantic search over indexed messages
│
├── scheduler/                # Cron-like scheduled jobs
│   ├── jobs.py               # Job definitions (reminders, briefings, etc.)
│   └── __init__.py
│
├── docs/                     # Documentation
│   ├── ARCHITECTURE.md       # System design decisions
│   ├── DEPLOYMENT.md         # Deployment guide
│   └── DESIGN_DECISIONS.md   # Why things are built this way
│
├── SOUL.md                   # Agent personality and behavioral guidelines
├── USER.md                   # User profile and context
├── MEMORY.md                 # Persistent facts and preferences
├── TOOLS.md                  # Tool documentation
├── PROGRESS.md               # Development progress tracker
│
├── config.py                 # Configuration and environment variables
├── main.py                   # Application entry point
├── pyproject.toml            # Python dependencies
├── uv.lock                   # Locked dependency versions
├── .env                      # Environment variables (not committed)
└── README.md                 # This file
```

---

## 🎨 Design Decisions

### Why No Agent Frameworks?

**LangChain/AutoGen/CrewAI are great for rapid prototyping, but they abstract away too much.**

Building from scratch gives you:
- **Full control** over the reasoning loop
- **Transparency** in how decisions are made
- **Fine-grained observability** - you know exactly what happened and why
- **No bloat** - only the code you need
- **Learning** - understanding every layer of an AI agent

### Why Groq?

- **Speed**: Llama 3.3 70B runs at ~300 tokens/second
- **Cost**: Cheaper than OpenAI for equivalent quality
- **Open Models**: Full control, no vendor lock-in
- **ReAct-friendly**: Groq models excel at tool use and reasoning chains

### Why File-Based Memory?

- **Simplicity**: No database setup required
- **Portability**: Easy to backup, version, and migrate
- **Transparency**: Human-readable markdown files
- **Auditability**: Git-trackable memory changes
- **Hybrid approach**: Combines with ChromaDB for best of both worlds

---

## 🚧 Roadmap

- [ ] **Multi-modal support** - Image understanding and generation
- [ ] **Voice messages** - Transcribe and respond to voice notes
- [ ] **Email integration** - Read and draft emails via Gmail API
- [ ] **Calendar sync** - Google Calendar event management
- [ ] **Proactive notifications** - Send unsolicited updates based on context
- [ ] **Multi-user support** - User-specific memory isolation
- [ ] **Web dashboard** - Monitor conversations and metrics
- [ ] **Function chaining** - Allow LLM to plan multi-step tool sequences
- [ ] **Self-improvement loop** - Analyze metrics to refine prompts

---

## 🐛 Troubleshooting

### Bot doesn't respond
1. Check if the bot is running (`python main.py`)
2. Verify `TELEGRAM_BOT_TOKEN` is correct
3. Ensure your chat ID matches `TELEGRAM_CHAT_ID`

### "Failed to fetch repos" error
- Verify `GITHUB_TOKEN` has `repo` scope
- Check `GITHUB_USERNAME` is correct

### ChromaDB indexing fails
```bash
# Clear and re-index
rm -rf .chroma
uv run python -c "from rag.indexer import index_all_logs; index_all_logs()"
```

### Tool calls not working
- Enable debug logging: `print(f"[DEBUG] {tool_name}, {tool_args}")`
- Check API keys for external services (SerpAPI, Notion, GitHub)

---

## 🤝 Contributing

Contributions are welcome! Here's how to get started:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** and add tests if applicable
4. **Commit**: `git commit -m "Add amazing feature"`
5. **Push**: `git push origin feature/amazing-feature`
6. **Open a Pull Request**

### Guidelines
- Follow PEP 8 style guidelines
- Add docstrings to new functions
- Update `PROGRESS.md` with your changes
- Test thoroughly before submitting

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 💬 Contact

Built by **Hash** - [GitHub](https://github.com/HarshitaJ02)

Have questions or suggestions? Open an issue or reach out!

---

## 🙏 Acknowledgments

- **Anthropic** for Claude (this README was generated by Claude!)
- **Groq** for blazing-fast LLM inference
- **Telegram** for their excellent Bot API
- **ChromaDB** for vector storage
- **SerpAPI** for web search capabilities

---

<div align="center">

**⭐ If you found this project helpful, consider giving it a star!**

Built with ❤️ and lots of ☕

</div>
