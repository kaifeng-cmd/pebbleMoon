# 🗨️ Japan Anime-Manga Bot

> **Multi-Agent AI Assistant for Anime & Manga Enthusiasts** - Built with Free Tier Services

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://share.streamlit.io)
[![Telegram](https://img.shields.io/badge/Telegram-26A5E4?style=for-the-badge&logo=telegram&logoColor=white)](https://telegram.org)
[![n8n](https://img.shields.io/badge/n8n-FF6B35?style=for-the-badge&logo=n8n&logoColor=white)](https://n8n.io)
[![Render](https://img.shields.io/badge/Render-000000?style=for-the-badge&logo=render&logoColor=white)](https://render.com)
[![Supabase](https://img.shields.io/badge/Supabase-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white)](https://supabase.com)
[![MongoDB](https://img.shields.io/badge/MongoDB-47A248?style=for-the-badge&logo=mongodb&logoColor=white)](https://mongodb.com)
[![Google AI](https://img.shields.io/badge/Google_AI-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://aistudio.google.com)

## 🌟 What is this Project?

**Japan Anime-Manga Bot** is a AI-powered assistant designed specifically for Japanese anime and manga enthusiasts. This project showcases how to build end to end AI application using entirely **free tier services**, demonstrating practical and experimental solutions.

### ✨ Key Features

- 🤖 **Multi-Agent AI System** powered by Google Gemini 2.5 Flash Lite
- 🎯 **Dual Chat Interfaces**: Telegram Bot + Streamlit Web App
- 🌸 **Anime & Manga Source Integration** via Jikan APIs (MyAnimeList unofficial API)
- 💬 **Anime Character Quotes** retrieve from Animechan APIs
- 🔍 **Web Search Capabilities** via Travily MCP server
- 💾 **Persistent Chat History** with MongoDB Atlas
- 🔐 **User Authentication** via Supabase
- ⚡ **Automated Workflow** orchestration with n8n
- 🚀 **Cloud Deployment** Render (for n8n docker image), Streamlit Cloud (for web app UI)

## 🪽 Functions

### Core AI Capabilities
- **Supervisor Agent**: Orchestrates and routes user queries to appropriate agents
- **Anime Agent**: Handles anime-related queries
- **Manga Agent**: Handles manga-related queries

### Anime & Manga Features
- **Search Functions**: Search anime, manga info
- **Seasonal Content**: Get current/past season anime list, upcoming releases
- **Top Rankings**: Access top-rated anime and manga lists
- **News & Updates**: All time anime/manga news from MyAnimeList
- **Recommendations**: Personalized suggestions
- **Character Search**: Find detailed character information
- **Image Retrieval** Retrieve anime/manga image URLs for viewing.
- **YouTube Anime Preview (PV)**: Watch anime previews on YouTube by fetching links.
- **Quote Retrival**: Random quotes or quotes by specific anime/character
- **Web Search**: For scenario of fallback or context enrichment

### Available Platform
- **Telegram**: Native Telegram built-in bot
- **Streamlit Web App**: Web UI with authentication & chat session tracking management

## 🏗️ Architecture & Tech Stack

### Technology
```
User Input (Telegram/Web App)
↓
Telegram Bot / Streamlit
↓
n8n Workflow Engine
↓
Multi-Agent System:
├── Supervisor Agent (Assign tasks, Decision making, Routes queries)
├── Anime Agent (Anime queries)
└── Manga Agent (Manga queries)
↓
External Tools:
├── Jikan APIs (MyAnimeList)
├── Animechan APIs (Anime quotes)
├── Mongodb (Persistent chat memory)
└── Travily MCP (Web search)
↓
Response via webhook
```

### Free Tier Services Used

| Service | Free Tier | Usage |
|---------|-----------|-------|
| **n8n.io** | Unlimited workflows | Workflow orchestration |
| **Render** | 750 hours/month | Docker container hosting |
| **Streamlit Cloud** | 1 GB resource limit | Web app hosting |
| **Telegram** | Free | Telegram Bot |
| **Google AI Studio** | Keep changing, pls refer to offical docs | Gemini model |
| **Supabase** | 500 MB db storage | Authentication & n8n workflow persistence |
| **MongoDB Atlas** | 512MB | Chat history storage |
| **Travily** | 1000 searches/month | Web search capabilities |
| **Uptime Robot** | 50 monitors | Keep Render active |

## 🚀 Quick Start

### Prerequisites
- Python 3.11 (I used this)
- Git
- Free accounts for all services mentioned above

### 1. Clone the Repository
```bash
git clone https://github.com/kaifeng-cmd/pebbleMoon.git
cd pebbleMoon
```

### 2. Create Virtual Environment
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup and host n8n on Render
- You need to use Render to host the n8n docker image (u can get this via n8n offcial provider from Docker Hub)
- After hosting, open the n8n and import `n8n_workflow (2).json` (download this from the project structure) and fill up your service credentials.

### 4. Environment Setup
Create a `.env` file in the root directory:
```env
# n8n Configuration
N8N_WEBHOOK_URL=https://xxxxx.onrender.com/webhook/chat
N8N_GET_HISTORY_URL=https://xxxxx.onrender.com/webhook/get-history
N8N_GET_SESSIONS_URL=https://xxxxx.onrender.com/webhook/get-sessions
N8N_API_KEY=your-n8n-api-key

# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-supabase-anon-key
```

For deploying n8n on Render with Supabase PostgreSQL:
```env
DB_POSTGRESDB_DATABASE=postgres
DB_POSTGRESDB_HOST=xxxxx.pooler.supabase.com
DB_POSTGRESDB_PASSWORD=xxxxx
DB_POSTGRESDB_POOL_SIZE=5
DB_POSTGRESDB_PORT=5432
DB_POSTGRESDB_SCHEMA=public
DB_POSTGRESDB_SSL=true
DB_POSTGRESDB_SSL_REJECT_UNAUTHORIZED=false
DB_POSTGRESDB_USER=xxxxxx
DB_TYPE=postgresdb
N8N_BASIC_AUTH_ACTIVE=true
N8N_BASIC_AUTH_PASSWORD=xxxxx
N8N_BASIC_AUTH_USER=xxxxx
N8N_ENCRYPTION_KEY=xxxxx
N8N_HOST=0.0.0.0
N8N_PORT=5678
WEBHOOK_URL=xxxxx.onrender.com
```

### 5. Run Locally
```bash
streamlit run main.py
```

### 6. Run on Streamlit Cloud
If you want to run on Streamlit Cloud, make sure u push your repos to GitHub and allow Streamlit Cloud to access, and then just paste your `.env` in secrets section provided by Streamlit Cloud.

## 🛠️ Challenges & Solutions

### 1. Render Free Tier Limitations
**Challenge**: Render free tier sleeps after 15 minutes of inactivity, causing n8n workflows to lose state.

**Solutions**: 
- Use **Uptime Robot** for automated pinging every 10 minutes.
- Switch from **SQLite** to **Supabase PostgreSQL** for persistent workflow storage, because n8n defaults to SQLite for workflow data, which doesn't persist on Render.
- Configure n8n to use external database `Supabase PostgreSQL` instead of file-based storage `SQLite`.

### 2. IPv4/IPv6 Compatibility Issues
**Challenge**: Render only supports IPv4 while Supabase uses IPv6 connections.

**Solution**:
- Use Supabase **session pooler** for db connection pooling.

### 3. Parameter Passing in n8n
**Challenge**: Complex multi-agent workflows require careful state management between nodes.

**Solution**: 
- Understand n8n's built-in data flow mechanisms.
- Design workflows with clear input/output contracts.

### 4. Authentication Trade-offs
**Challenge**: Using Supabase anon key instead of proper JWT tokens for simplicity.

**Solutions**:
- Implement email existence checking via dummy login attempts.
- Accept limitations for demo purposes.
- Focus on showcasing AI agent capabilities over security.

### 5. Prompt Engineering
**Challenge**: Optimizing AI responses for anime/manga context while maintaining accuracy.

**Solutions**:
- Iterative prompt testing and refinement.
- Context-aware system prompts.

## ⚠️ Limitations & Considerations

### Performance Limitations
- **Response Time**: 10-20 seconds per query (due to multi-agent complex processing instead of like LLM RAG 2-5 sec)
- **Rate Limits**: Various API quotas across all free tier services

### Technical Limitations
- **Authentication**: Uses Supabase anon key instead of token (main purpose just want to showcase the agent workflow and provide UI to input)
- **Database**: 500MB+ MongoDB limit may require cleanup if needed
- **Search**: Limited Travily requests/month
- **AI**: Google Gemini free tier rate limits (ex. 15 req/min, 1000/day)

## 📸 Screenshots

### Main Chat Interface
*[Add screenshot of Streamlit chat interface]*

### n8n Workflow Architecture
*[Add screenshot of n8n workflow nodes and connections]*

### Telegram Bot Integration
*[Add screenshot of Telegram bot in action]*

## 🤖 AI Agent Prompts
Detailed system prompts for all agents used in n8n: [`prompts.md`](prompts.md)
*You can change/modify according to your needs & style. Here's for a view, to change, go to your n8n agent nodes*

## 🙏 Acknowledgments

- **MyAnimeList** for the comprehensive anime/manga info
  *MyAnimeList is one of the largest and most popular anime/manga databases & platform worldwide*
- **Jikan API** for providing unofficial APIs access to MyAnimeList
- **Animechan** for anime character quotes APIs

---

<div align="center">
  <p><strong>🍣💎 Built for anime and manga enthusiasts</strong></p>
  <p><em>Showcasing the power of combining multiple free services into end to end solutions.</em></p>
</div>
