from utils import data_fetcher

class EarningsSurpriseTracker:
    def __init__(self, config=None):
        pass

    def analyze(self, symbol, price_df=None):
        _, surprise_pct = data_fetcher.get_last_earnings_surprise(symbol)
        if surprise_pct is not None:
            score = int(min(100, max(1, surprise_pct + 50)))
            return score
        return 1
