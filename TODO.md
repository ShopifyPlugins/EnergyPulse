# BizBot — TODO

## Phase 1: MVP (Current)

- [x] Project structure & configuration
- [x] SQLite database layer (knowledge, conversations, admins, settings)
- [x] TF-IDF knowledge base with RAG retrieval
- [x] LLM-powered response generation (OpenAI-compatible)
- [x] Customer Telegram commands (/start, /help, /human)
- [x] Admin commands (/admin, /add, /list, /delete, /stats, /setprompt, /setgreeting)
- [x] Free-text message handling with AI reply
- [x] Human escalation with admin notification
- [ ] Unit tests for db, knowledge_base, and ai_engine
- [ ] File upload support for knowledge base (PDF, TXT, CSV)
- [ ] Deploy to VPS and test with a real business
- [ ] Rate limiting per chat to control LLM costs

## Phase 2: Hardening

- [ ] Docker + docker-compose for one-click deployment
- [ ] CI: GitHub Actions for lint + tests
- [ ] Conversation export to CSV/JSON for business analytics
- [ ] Typing indicator while waiting for LLM response
- [ ] Graceful error recovery for LLM API timeouts
- [ ] Image/document message handling (forward to admin or OCR)
- [ ] Admin command: /reply <chat_id> <message> to respond as human through the bot
- [ ] Webhook mode for production (replace polling)

## Phase 3: Monetization

- [ ] Stripe integration for monthly subscription ($50-200/month per business)
- [ ] Landing page (single HTML or Carrd) for SEO & conversion
- [ ] Multi-bot management dashboard (FastAPI + HTMX)
- [ ] Managed hosting: businesses just provide their bot token, we run everything
- [ ] Usage-based pricing tier: charge per message beyond monthly quota
- [ ] White-label: remove all BizBot branding, fully customizable

## Phase 4: Scale

- [ ] WhatsApp Business API integration (much larger addressable market)
- [ ] Vector embeddings (replace TF-IDF with OpenAI/Cohere embeddings + ChromaDB)
- [ ] Multi-business platform: one deployment serves many businesses
- [ ] Analytics dashboard: response quality scores, common questions, gaps in knowledge
- [ ] Automated knowledge base builder: scrape business website to seed FAQ
- [ ] Canned responses / quick replies for common queries
- [ ] Multilingual knowledge base: auto-translate entries

## Ideas Backlog

- [ ] Shopify integration: pull product catalog as knowledge base automatically
- [ ] Voice message support: transcribe and respond
- [ ] Sentiment analysis: flag negative conversations for urgent admin review
- [ ] A/B test different system prompts to optimize customer satisfaction
- [ ] Telegram Mini App: visual admin panel inside Telegram
