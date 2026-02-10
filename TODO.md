# EnergyPulse — TODO

## Phase 1: MVP (Current)

- [x] Project structure & configuration
- [x] ENTSO-E data fetcher (day-ahead prices)
- [x] LSTM predictor (train + inference)
- [x] Telegram bot commands (/price, /predict, /zone, /subscribe)
- [x] Message formatter with recommendations
- [x] APScheduler daily push
- [ ] Unit tests for predictor and formatter
- [ ] Error handling: ENTSO-E API rate limiting & retry logic
- [ ] Validate bot on live Telegram with real ENTSO-E data
- [ ] Deploy to VPS and run 7-day pilot

## Phase 2: Hardening

- [ ] Replace in-memory subscriber store with SQLite
- [ ] Add `/admin` command with token-based auth for /train
- [ ] Model auto-retrain cron (weekly on fresh data)
- [ ] Add weather features to LSTM input (temperature correlates with demand)
- [ ] Prediction accuracy tracking (MAE / MAPE logged per day)
- [ ] Graceful shutdown & state persistence on restart
- [ ] Docker + docker-compose for one-click deployment
- [ ] CI: GitHub Actions for lint + tests

## Phase 3: Monetization

- [ ] Stripe integration for Pro subscription
- [ ] Free tier: 1x daily push, 3 /predict per day
- [ ] Pro tier (3-5 EUR/month): unlimited predictions, 15-min resolution, personalized device scheduling
- [ ] Landing page (single HTML or Carrd) for SEO & conversion
- [ ] Referral system: invite 3 friends → 1 month free

## Phase 4: Feature Expansion

- [ ] MILP optimizer: given battery capacity + EV schedule, compute optimal charge/discharge plan
- [ ] Tesla Powerwall / SolarEdge API integration for automated control
- [ ] Multi-language support (DE, FR, NL, EN)
- [ ] Web dashboard (lightweight — FastAPI + HTMX)
- [ ] Support more zones: ES, IT, PL, DK, NO, SE
- [ ] Push channel options: Telegram + Email + WhatsApp

## Ideas Backlog

- [ ] Compare LSTM vs. Transformer vs. XGBoost for price prediction
- [ ] Negative price alerts (pay users to consume — real in DE market)
- [ ] Community feature: share savings leaderboard
- [ ] B2B pivot: API access for energy consultants (usage-based pricing)
- [ ] Raw material cost prediction for Shopify merchants (cross-pollinate original idea)
