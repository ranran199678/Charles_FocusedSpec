from utils import data_fetcher

class FinancialStabilityAgent:
    def __init__(self, config=None):
        self.leverage_weight = config.get("leverage_weight", 0.5) if config else 0.5
        self.liquidity_weight = config.get("liquidity_weight", 0.5) if config else 0.5

    def analyze(self, symbol, price_df=None):
        # שליפת נתוני מאזן אחרון
        try:
            balance = data_fetcher.get_balance_sheet(symbol)
            if balance is None or balance.empty:
                return {
                    "score": 50,
                    "explanation": "אין נתוני מאזן זמינים",
                    "details": {}
                }

            # חישוב יחס חוב להון
            try:
                total_debt = float(balance.iloc[0].get("totalDebt", 0) or 0)
                total_equity = float(balance.iloc[0].get("totalEquity", 1) or 1)
                leverage = total_debt / total_equity if total_equity > 0 else 1
            except Exception:
                leverage = 1

            # חישוב יחס שוטף (currentRatio)
            try:
                current_assets = float(balance.iloc[0].get("totalCurrentAssets", 0) or 0)
                current_liabilities = float(balance.iloc[0].get("totalCurrentLiabilities", 1) or 1)
                current_ratio = current_assets / current_liabilities if current_liabilities > 0 else 1
            except Exception:
                current_ratio = 1

            # ניקוד איתנות פיננסית: מינימום 1, מקסימום 100
            leverage_score = max(1, min(100, int((1.5 - leverage) * 50)))  # חוב נמוך = ניקוד גבוה
            liquidity_score = max(1, min(100, int((current_ratio - 1) * 50 + 50)))  # יחס שוטף מעל 1=ניקוד גבוה
            score = int(self.leverage_weight * leverage_score + self.liquidity_weight * liquidity_score)
            
            return {
                "score": max(1, min(100, score)),
                "explanation": f"יחס חוב: {leverage:.2f}, יחס שוטף: {current_ratio:.2f}",
                "details": {
                    "leverage": leverage,
                    "current_ratio": current_ratio,
                    "leverage_score": leverage_score,
                    "liquidity_score": liquidity_score
                }
            }
        except Exception as e:
            return {
                "score": 50,
                "explanation": f"שגיאה בניתוח פיננסי: {str(e)}",
                "details": {}
            }
