import os
import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

ETF_MAPPING = {
    'AAPL': 'XLK',
    'MSFT': 'XLK',
    'NVDA': 'SMH',
    'JPM': 'XLF',
    'TSLA': 'XLY',
    'GOOGL': 'XLC'
    # יש להרחיב לפי הצורך
}

class ReturnForecaster:
    def __init__(self, symbol, model_type='linear', window_size=60, forecast_days=5, model_dir="models"):
        self.symbol = symbol
        self.model_type = model_type
        self.window_size = window_size
        self.forecast_days = forecast_days
        self.model = None
        self.model_path = os.path.join(model_dir, f"{symbol}_{model_type}_model.pkl")
        os.makedirs(model_dir, exist_ok=True)

    def _prepare_features(self, price_df, etf_df=None):
        df = price_df.copy().dropna().sort_index()
        df['returns'] = df['close'].pct_change()
        df['volatility'] = df['returns'].rolling(self.window_size).std()
        df['momentum'] = df['close'] / df['close'].shift(self.window_size) - 1
        df['avg_volume'] = df['volume'].rolling(self.window_size).mean()

        if etf_df is not None:
            etf_df = etf_df.copy().dropna().sort_index()
            etf_df['etf_return'] = etf_df['close'].pct_change(self.forecast_days)
            df['etf_return'] = etf_df['etf_return']
        else:
            df['etf_return'] = 0  # fallback

        df['future_return'] = df['close'].shift(-self.forecast_days) / df['close'] - 1
        df = df.dropna()
        return df

    def train(self, price_df, etf_df=None):
        df = self._prepare_features(price_df, etf_df)
        X = df[['volatility', 'momentum', 'avg_volume', 'etf_return']]
        y = df['future_return']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

        if self.model_type == 'linear':
            self.model = LinearRegression()
        else:
            self.model = GradientBoostingRegressor(n_estimators=100, max_depth=3)

        self.model.fit(X_train, y_train)
        y_pred = self.model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)

        # שמירת המודל
        joblib.dump(self.model, self.model_path)

        return {'mse': mse, 'last_train_date': df.index[-1], 'model_path': self.model_path}

    def load_model(self):
        if os.path.exists(self.model_path):
            self.model = joblib.load(self.model_path)
        else:
            raise FileNotFoundError(f"Model file not found at {self.model_path}")

    def predict(self, price_df, etf_df=None):
        if self.model is None:
            self.load_model()

        df = self._prepare_features(price_df, etf_df)
        X = df[['volatility', 'momentum', 'avg_volume', 'etf_return']]
        latest_data = X.iloc[[-1]]
        forecast = self.model.predict(latest_data)[0]

        std_estimate = df['future_return'].std()
        conf_interval = 1.96 * std_estimate

        result = {
            'expected_return': round(forecast, 4),
            'std_dev': round(std_estimate, 4),
            'confidence_interval': [round(forecast - conf_interval, 4), round(forecast + conf_interval, 4)],
            'model_used': self.model_type
        }

        # ניתוח Feature Importance אם GBM
        if hasattr(self.model, "feature_importances_"):
            result['feature_importance'] = dict(zip(
                ['volatility', 'momentum', 'avg_volume', 'etf_return'],
                self.model.feature_importances_.round(4)
            ))

        return result
