import numpy as np
import pandas as pd


def _find_best_window(values: np.ndarray, window: int = 3, minimize: bool = True):
    """Find the best contiguous window of given size."""
    best_idx = 0
    best_total = float("inf") if minimize else float("-inf")
    for i in range(len(values) - window + 1):
        total = values[i : i + window].sum()
        if (minimize and total < best_total) or (not minimize and total > best_total):
            best_total = total
            best_idx = i
    return best_idx


def format_price_forecast(
    predictions: np.ndarray,
    start_hour: int = 0,
    currency: str = "\u20ac",
) -> str:
    """Format 24h price predictions into a Telegram-friendly message."""
    min_price = predictions.min()
    max_price = predictions.max()
    avg_price = predictions.mean()

    # Best 3h window for cheap usage
    cheap_idx = _find_best_window(predictions, window=3, minimize=True)
    cheap_start = (start_hour + cheap_idx) % 24
    cheap_end = (cheap_start + 3) % 24

    # Worst 3h window to avoid
    peak_idx = _find_best_window(predictions, window=3, minimize=False)
    peak_start = (start_hour + peak_idx) % 24
    peak_end = (peak_start + 3) % 24

    # Rough monthly savings estimate
    monthly_savings = (max_price - min_price) * 3 * 30

    lines = [
        "\u26a1 *Electricity Price Forecast*",
        "\u2501" * 22,
        f"\U0001f49a Cheapest: {cheap_start:02d}:00\u2013{cheap_end:02d}:00"
        f" \u2192 {currency}{min_price:.4f}/kWh",
        f"\U0001f534 Peak:       {peak_start:02d}:00\u2013{peak_end:02d}:00"
        f" \u2192 {currency}{max_price:.4f}/kWh",
        f"\U0001f4ca Average:  {currency}{avg_price:.4f}/kWh",
        "\u2501" * 22,
        "\U0001f4a1 *Recommendations:*",
        f"  \u2022 EV charging \u2192 set to {cheap_start:02d}:00",
        f"  \u2022 Washer/Dryer \u2192 set to {cheap_start:02d}:00",
        f"  \u2022 Avoid heavy usage {peak_start:02d}:00\u2013{peak_end:02d}:00",
        "\u2501" * 22,
        f"\U0001f4b0 Est. monthly savings: ~{currency}{monthly_savings:.1f}",
    ]
    return "\n".join(lines)


def format_current_prices(prices: pd.Series, currency: str = "\u20ac") -> str:
    """Format current day's actual prices as a visual chart."""
    now = pd.Timestamp.now(tz="Europe/Berlin")
    current_hour = now.hour
    price_max = prices.max()

    lines = ["\U0001f4ca *Today's Electricity Prices*", "\u2501" * 22]

    for ts, price in prices.items():
        hour = ts.hour
        pointer = "\U0001f449" if hour == current_hour else "  "
        bar_len = max(1, int(price / price_max * 10)) if price_max > 0 else 1
        bar = "\u2588" * bar_len
        lines.append(f"{pointer} {hour:02d}:00 {bar} {currency}{price:.4f}")

    lines.append("\u2501" * 22)
    lines.append(
        f"Min: {currency}{prices.min():.4f} | "
        f"Max: {currency}{prices.max():.4f} | "
        f"Avg: {currency}{prices.mean():.4f}"
    )
    return "\n".join(lines)
