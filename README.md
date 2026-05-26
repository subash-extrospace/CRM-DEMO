# AI Omnichannel CRM

An AI-powered omnichannel CRM backend built using FastAPI, Celery, Redis, WhatsApp Cloud API, and Facebook Messenger API.

This project receives messages from multiple communication platforms such as:

* WhatsApp
* Facebook Messenger
* Instagram
* Telegram (planned)
* LinkedIn (planned)

and processes all conversations inside a unified CRM backend.

The system is designed so that AI can:

* automatically reply to customers
* summarize chats
* provide insights
* automate support workflows

---

# Core Concept

This CRM is a multi-tenant omnichannel communication platform.

Each tenant can be:

* an organization
* a company
* a person
* a freelancer

Each tenant connects:

* WhatsApp
* Messenger
* Instagram
* etc

All conversations are centralized in one backend system.

---

# High Level Architecture

```text
Customer
   ↓
WhatsApp / Messenger
   ↓
Meta Webhook
   ↓
FastAPI Webhook Endpoint
   ↓
Normalize Incoming Messages
   ↓
Celery Queue
   ↓
AI Processing
   ↓
Send Reply Back To Platform
```

---

# Tech Stack

| Technology         | Purpose                            |
| ------------------ | ---------------------------------- |
| FastAPI            | Backend API                        |
| Celery             | Background task processing         |
| Redis              | Celery broker/backend              |
| Meta Webhooks      | Incoming WhatsApp/Messenger events |
| WhatsApp Cloud API | WhatsApp messaging                 |
| Messenger API      | Facebook Messenger messaging       |
| ngrok              | Local webhook exposure             |

---

# Project Structure

```text
project/
│
├── app.py
├── celery_app.py
│
├── scripts/
│   ├── receive_messages.py
│   ├── send_message_whatsapp.py
│   ├── send_message_messenger.py
│   └── tasks.py
│
└── README.md
```

---

# File Explanations

---

# app.py

Main FastAPI application.

Responsibilities:

* webhook verification
* receiving Meta webhook events
* triggering Celery background tasks
* exposing send-message APIs

Main endpoints:

| Endpoint                    | Purpose                             |
| --------------------------- | ----------------------------------- |
| GET /webhook/meta           | Meta webhook verification           |
| POST /webhook/meta          | Receive WhatsApp/Messenger messages |
| POST /whatsapp/send-message | Send WhatsApp message manually      |

---

# receive_messages.py

Responsible for:

* parsing incoming webhook payloads
* identifying platform type
* normalizing all incoming messages into a common structure

This file converts platform-specific payloads into:

```python
{
    "platform": "whatsapp",
    "sender": "97798xxxx",
    "message": "Hello",
}
```

This normalization allows the backend to treat all platforms uniformly.

---

# send_message_whatsapp.py

Responsible for sending outgoing WhatsApp messages using:

```text
WhatsApp Cloud API
```

Uses:

* PHONE_NUMBER_ID
* ACCESS_TOKEN

to send replies back to users.

---

# send_message_messenger.py

Responsible for sending outgoing Facebook Messenger replies.

Uses:

* Facebook Page Access Token

to reply to Messenger users.

---

# tasks.py

Contains Celery background tasks.

Purpose:

* avoid blocking webhook requests
* process AI logic asynchronously
* send automated replies

Current flow:

1. Webhook receives message
2. Celery task starts
3. Fake AI response generated
4. Reply sent back to user

Current AI response:

```text
Hello how can i help you?
```

In future this will be replaced with:

* OpenAI
* Claude
* Gemini
* custom AI pipeline

---

# celery_app.py

Celery configuration file.

Responsible for:

* Redis connection
* Celery broker setup
* task queue setup

---

# Why Celery Is Needed

Meta webhooks expect a very fast response.

If AI processing takes too long:

* Meta retries webhook delivery
* duplicate messages happen
* webhook may fail

So:

* FastAPI immediately returns 200 OK
* heavy processing happens in Celery

This is production architecture.

---

# Message Flow

---

# WhatsApp Flow

```text
User sends WhatsApp message
    ↓
Meta sends webhook to FastAPI
    ↓
FastAPI receives payload
    ↓
receive_messages.py normalizes data
    ↓
Celery task triggered
    ↓
AI generates response
    ↓
send_message_whatsapp.py sends reply
```

---

# Messenger Flow

```text
User sends Messenger message
    ↓
Meta webhook triggered
    ↓
FastAPI receives event
    ↓
Message normalized
    ↓
Celery task started
    ↓
AI reply generated
    ↓
send_message_messenger.py sends reply
```

---

# Why Message Normalization Is Important

Every platform sends different payload structures.

Example:

WhatsApp:

```json
{
  "from": "97798xxxx"
}
```

Messenger:

```json
{
  "sender": {
    "id": "28121884440735080"
  }
}
```

Normalization converts everything into one internal format.

This allows:

* same AI pipeline
* same database structure
* same CRM architecture

across all platforms.

---

# Why Echo Messages Are Ignored

Messenger sends webhook events even for messages sent by our own bot.

Without filtering:

* infinite reply loops happen

This condition prevents that:

```python
if message.get("is_echo"):
    continue
```

---

# Current Limitations

Current implementation:

* no database
* no authentication
* no frontend
* no conversation storage
* no AI memory

This is currently a backend communication prototype.

---

# Future Roadmap

Planned features:

* PostgreSQL integration
* Multi-tenant architecture
* CRM inbox UI
* AI conversation memory
* Human agent assignment
* Role management
* Instagram support
* Telegram support
* LinkedIn support
* Analytics dashboard
* Conversation insights
* AI summarization
* AI auto-tagging

---

# Multi-Tenant Architecture Plan

Each tenant:

* organization
* company
* person

will have:

* their own connected channels
* their own conversations
* their own CRM workspace

Backend codebase remains shared.

Database may later become:

* database-per-tenant

OR

* shared database with tenant isolation

depending on scaling requirements.

---

# Local Development Setup

---

# 1. Create Virtual Environment

```bash
python -m venv myenv
```

---

# 2. Activate Environment

Mac/Linux:

```bash
source myenv/bin/activate
```

Windows:

```bash
myenv\Scripts\activate
```

---

# 3. Install Dependencies

```bash
pip install fastapi uvicorn celery redis requests
```

---

# 4. Start Redis

Mac:

```bash
brew services start redis
```

Linux:

```bash
sudo service redis-server start
```

---

# 5. Start FastAPI

```bash
python app.py
```

---

# 6. Start Celery Worker

```bash
celery -A celery_app.celery worker --loglevel=info
```

---

# 7. Start ngrok

```bash
ngrok http 8000
```

Copy generated HTTPS URL into Meta Webhook settings.

Example:

```text
https://abcd123.ngrok-free.app/webhook/meta
```

---

# Meta Webhook Verification

Meta sends:

```text
hub.challenge
hub.verify_token
hub.mode
```

Backend verifies token and returns challenge.

If verification succeeds:

* webhook becomes active

---

# Important Notes

* Never commit access tokens to GitHub
* Use environment variables in production
* Use HTTPS in production
* Use proper database storage
* Use message deduplication
* Use logging and monitoring

---

# Production Recommendations

Recommended production stack:

| Component     | Recommendation       |
| ------------- | -------------------- |
| Backend       | FastAPI              |
| Queue         | Celery               |
| Broker        | Redis                |
| Database      | PostgreSQL           |
| Deployment    | Docker               |
| Reverse Proxy | Nginx                |
| Hosting       | AWS / GCP / Azure    |
| Monitoring    | Prometheus + Grafana |

---

# Main Goal Of This Project

Build a unified AI-powered CRM where businesses can manage:

* WhatsApp
* Messenger
* Instagram
* Telegram
* LinkedIn
* Email

from a single platform with AI automation.
