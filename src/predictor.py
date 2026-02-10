import logging
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from sklearn.preprocessing import MinMaxScaler

from src.config import MODEL_PATH, SEQUENCE_LENGTH, PREDICTION_HOURS

logger = logging.getLogger(__name__)


class PriceLSTM(nn.Module):
    """LSTM network for electricity price forecasting."""

    def __init__(
        self,
        input_size: int = 1,
        hidden_size: int = 64,
        num_layers: int = 2,
        output_size: int = PREDICTION_HOURS,
    ):
        super().__init__()
        self.lstm = nn.LSTM(
            input_size, hidden_size, num_layers, batch_first=True, dropout=0.2
        )
        self.fc = nn.Sequential(
            nn.Linear(hidden_size, 32),
            nn.ReLU(),
            nn.Linear(32, output_size),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        _, (h_n, _) = self.lstm(x)
        return self.fc(h_n[-1])


class PricePredictor:
    """Manages LSTM model training and inference for price prediction."""

    def __init__(self):
        self.model = PriceLSTM()
        self.scaler = MinMaxScaler()
        self.is_trained = False
        self._load_model()

    def _load_model(self):
        path = Path(MODEL_PATH)
        if not path.exists():
            logger.info("No saved model found at %s", path)
            return
        checkpoint = torch.load(path, map_location="cpu", weights_only=False)
        self.model.load_state_dict(checkpoint["model_state"])
        self.scaler.min_ = checkpoint["scaler_min"]
        self.scaler.scale_ = checkpoint["scaler_scale"]
        self.scaler.data_min_ = checkpoint["scaler_data_min"]
        self.scaler.data_max_ = checkpoint["scaler_data_max"]
        self.scaler.data_range_ = checkpoint["scaler_data_range"]
        self.is_trained = True
        logger.info("Model loaded from %s", path)

    def _save_model(self):
        path = Path(MODEL_PATH)
        path.parent.mkdir(parents=True, exist_ok=True)
        torch.save(
            {
                "model_state": self.model.state_dict(),
                "scaler_min": self.scaler.min_,
                "scaler_scale": self.scaler.scale_,
                "scaler_data_min": self.scaler.data_min_,
                "scaler_data_max": self.scaler.data_max_,
                "scaler_data_range": self.scaler.data_range_,
            },
            path,
        )
        logger.info("Model saved to %s", path)

    def train(self, prices: pd.Series, epochs: int = 50, lr: float = 0.001):
        """Train LSTM on historical price data."""
        values = prices.values.reshape(-1, 1).astype(np.float32)
        scaled = self.scaler.fit_transform(values)

        # Build sequences
        X, y = [], []
        for i in range(len(scaled) - SEQUENCE_LENGTH - PREDICTION_HOURS):
            X.append(scaled[i : i + SEQUENCE_LENGTH])
            y.append(
                scaled[
                    i + SEQUENCE_LENGTH : i + SEQUENCE_LENGTH + PREDICTION_HOURS
                ].flatten()
            )

        if len(X) == 0:
            raise ValueError(
                f"Not enough data: need at least {SEQUENCE_LENGTH + PREDICTION_HOURS} "
                f"hours, got {len(values)}"
            )

        X_t = torch.FloatTensor(np.array(X))
        y_t = torch.FloatTensor(np.array(y))

        optimizer = torch.optim.Adam(self.model.parameters(), lr=lr)
        loss_fn = nn.MSELoss()

        self.model.train()
        for epoch in range(epochs):
            optimizer.zero_grad()
            output = self.model(X_t)
            loss = loss_fn(output, y_t)
            loss.backward()
            optimizer.step()

            if (epoch + 1) % 10 == 0:
                logger.info("Epoch %d/%d — Loss: %.6f", epoch + 1, epochs, loss.item())

        self.is_trained = True
        self._save_model()
        logger.info("Training complete")

    def predict(self, recent_prices: pd.Series) -> np.ndarray:
        """Predict next 24h prices from recent history."""
        if not self.is_trained:
            raise RuntimeError("Model not trained yet")

        values = (
            recent_prices.values[-SEQUENCE_LENGTH:].reshape(-1, 1).astype(np.float32)
        )
        scaled = self.scaler.transform(values)
        x = torch.FloatTensor(scaled).unsqueeze(0)

        self.model.eval()
        with torch.no_grad():
            pred = self.model(x).numpy()[0]

        return self.scaler.inverse_transform(pred.reshape(-1, 1)).flatten()
