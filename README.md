# EnergyPulse

European electricity spot price prediction & alert Telegram bot.

Uses LSTM neural networks to forecast day-ahead electricity prices from the ENTSO-E Transparency Platform, helping EU households shift energy usage to the cheapest hours.

## Features

- **Real-time prices** — fetch today's hourly spot prices from ENTSO-E
- **LSTM forecasting** — predict next 24h price curve based on 7-day input sequences
- **Smart recommendations** — identify cheapest windows for EV charging, laundry, etc.
- **Daily push alerts** — automatic forecast delivery at 20:00 CET via Telegram
- **Multi-region** — supports DE/LU, FR, NL, AT, BE bidding zones

## Architecture

```
src/
├── config.py       # Environment-based configuration
├── fetcher.py      # ENTSO-E API client (day-ahead prices, EUR/kWh)
├── predictor.py    # LSTM model (training + inference)
├── formatter.py    # Telegram message formatting
├── bot.py          # Command handlers + subscriber management
└── main.py         # Entry point + APScheduler cron job
```

## Quick Start

### 1. Prerequisites

- Python 3.11+
- [Telegram Bot Token](https://core.telegram.org/bots#botfather) from @BotFather
- [ENTSO-E API Key](https://transparency.entsoe.eu/) (free registration)

### 2. Setup

```bash
# Clone
git clone https://github.com/ShopifyPlugins/Advanced-Lead-Time-Alert.git
cd Advanced-Lead-Time-Alert

# Virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Dependencies
pip install -r requirements.txt

# Configuration
cp .env.example .env
# Edit .env and fill in your TELEGRAM_BOT_TOKEN and ENTSOE_API_KEY
```

### 3. Run

```bash
python -m src.main
```

### 4. First Use

Open your bot in Telegram, then:

```
/start        — Register and see available commands
/train        — Train LSTM model on 90 days of historical data (run once)
/predict      — Get tomorrow's price forecast
/price        — See today's actual spot prices
/zone DE_LU   — Switch bidding zone
/subscribe    — Enable daily forecast push at 20:00 CET
```

## Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Register + show help |
| `/price` | Today's hourly spot prices with visual chart |
| `/predict` | LSTM-predicted next 24h prices with recommendations |
| `/zone <CODE>` | Set bidding zone (DE_LU, FR, NL, AT, BE) |
| `/subscribe` | Subscribe to daily 20:00 CET forecast push |
| `/unsubscribe` | Stop daily alerts |
| `/train` | Admin: retrain model on latest 90 days of data |

## Supported Regions

| Code | Region |
|------|--------|
| `DE_LU` | Germany / Luxembourg |
| `FR` | France |
| `NL` | Netherlands |
| `AT` | Austria |
| `BE` | Belgium |

## LSTM Model

- **Input**: 168 hours (7 days) of hourly spot prices
- **Architecture**: 2-layer LSTM (hidden=64) + FC head
- **Output**: 24-hour price prediction vector
- **Training data**: 90 days of ENTSO-E day-ahead prices
- **Preprocessing**: MinMaxScaler normalization

## Configuration

All settings are managed via environment variables (`.env` file):

| Variable | Default | Description |
|----------|---------|-------------|
| `TELEGRAM_BOT_TOKEN` | — | Telegram bot token from @BotFather |
| `ENTSOE_API_KEY` | — | ENTSO-E Transparency Platform API key |
| `DEFAULT_BIDDING_ZONE` | `DE_LU` | Default price zone |
| `MODEL_PATH` | `models/lstm_price.pt` | LSTM model save path |
| `SEQUENCE_LENGTH` | `168` | Input sequence length (hours) |
| `PREDICTION_HOURS` | `24` | Prediction horizon (hours) |
| `DAILY_FORECAST_HOUR` | `20` | Daily push time (CET, 24h format) |

## Tech Stack

| Component | Technology |
|-----------|------------|
| Bot framework | python-telegram-bot 21.7 |
| Price data | entsoe-py (ENTSO-E API) |
| ML model | PyTorch (LSTM) |
| Preprocessing | scikit-learn, pandas, numpy |
| Scheduling | APScheduler |
| Config | python-dotenv |

## Deployment

For production, a $5/month VPS (e.g. Hetzner, DigitalOcean) is sufficient:

```bash
# Run with systemd or screen/tmux
nohup python -m src.main > energypulse.log 2>&1 &
```

## License

MIT
