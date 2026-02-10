# BizBot

White-label AI customer service bot for Telegram. Help small businesses automate customer support with an LLM-powered assistant trained on their own knowledge base.

## Features

- **AI-powered replies** — answers customer questions using any OpenAI-compatible LLM
- **Knowledge base (RAG)** — admins upload FAQ/docs, bot retrieves relevant context before answering
- **Conversation memory** — maintains chat history for natural multi-turn conversations
- **Human escalation** — customers can request a human; all admins get notified instantly
- **Admin dashboard** — manage knowledge base, customize prompts, view usage stats via Telegram commands
- **SQLite persistence** — conversations, knowledge, and settings survive restarts
- **Multi-language** — replies in whatever language the customer uses

## Architecture

```
src/
├── config.py           # Environment-based configuration
├── db.py               # SQLite database (knowledge, conversations, admins, settings)
├── knowledge_base.py   # TF-IDF based knowledge retrieval (RAG)
├── ai_engine.py        # LLM API wrapper with context injection
├── bot.py              # Telegram handlers (customer + admin)
└── main.py             # Entry point
```

## Quick Start

### 1. Prerequisites

- Python 3.11+
- [Telegram Bot Token](https://core.telegram.org/bots#botfather) from @BotFather
- An OpenAI API key (or any OpenAI-compatible endpoint)

### 2. Setup

```bash
# Clone
git clone https://github.com/ShopifyPlugins/EnergyPulse.git
cd EnergyPulse

# Virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Dependencies
pip install -r requirements.txt

# Configuration
cp .env.example .env
# Edit .env — fill in TELEGRAM_BOT_TOKEN, LLM_API_KEY, BUSINESS_NAME, ADMIN_PASSWORD
```

### 3. Run

```bash
python -m src.main
```

### 4. First Use

Open your bot in Telegram:

```
/start              — See welcome message
/admin <password>   — Authenticate as admin
/add FAQ            — Add a knowledge base entry (send content in next message)
/list               — View all knowledge entries
```

Then send any message as a customer — the bot will answer using the knowledge base + LLM.

## Bot Commands

### Customer Commands

| Command | Description |
|---------|-------------|
| `/start` | Show welcome message |
| `/help` | List available commands |
| `/human` | Request human assistance (notifies all admins) |
| *(any text)* | AI-generated reply based on knowledge base |

### Admin Commands

| Command | Description |
|---------|-------------|
| `/admin <password>` | Authenticate as admin |
| `/add <title>` | Add knowledge entry (send content in next message) |
| `/list` | List all knowledge base entries |
| `/delete <id>` | Delete a knowledge entry |
| `/stats` | View usage statistics |
| `/setprompt` | Set custom AI system instructions |
| `/setgreeting` | Set custom welcome message |

## Configuration

All settings via environment variables (`.env` file):

| Variable | Default | Description |
|----------|---------|-------------|
| `TELEGRAM_BOT_TOKEN` | — | Telegram bot token from @BotFather |
| `LLM_API_KEY` | — | OpenAI (or compatible) API key |
| `LLM_BASE_URL` | `https://api.openai.com/v1` | LLM API endpoint |
| `LLM_MODEL` | `gpt-4o-mini` | Model name |
| `BUSINESS_NAME` | `My Business` | Shown in welcome message and system prompt |
| `ADMIN_PASSWORD` | `changeme` | Password for `/admin` authentication |
| `DB_PATH` | `data/bizbot.db` | SQLite database path |
| `CHUNK_SIZE` | `500` | Max characters per knowledge chunk |
| `TOP_K` | `3` | Number of knowledge chunks retrieved per query |
| `MAX_HISTORY` | `10` | Conversation messages included in LLM context |

## Tech Stack

| Component | Technology |
|-----------|------------|
| Bot framework | python-telegram-bot 21.7 |
| LLM client | openai (any OpenAI-compatible API) |
| Knowledge retrieval | scikit-learn TF-IDF + cosine similarity |
| Database | SQLite |
| Config | python-dotenv |

## How It Works

1. Business owner creates a Telegram bot via @BotFather
2. Configures BizBot with their bot token and LLM API key
3. Adds FAQ/product info/policies to the knowledge base via `/add`
4. Customers message the bot — BizBot retrieves relevant knowledge, injects it into the LLM prompt, and generates a contextual reply
5. If the bot can't answer, customers type `/human` to escalate

## Deployment

A $5/month VPS (e.g. Hetzner, DigitalOcean) is sufficient:

```bash
nohup python -m src.main > bizbot.log 2>&1 &
```

## License

MIT
