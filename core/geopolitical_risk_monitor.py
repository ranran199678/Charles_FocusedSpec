from utils import data_fetcher

class GeopoliticalRiskMonitor:
    def __init__(self, config=None):
        pass

    def analyze(self, symbol, price_df=None):
        geo = data_fetcher.get_geo_risk_score(symbol)
        score = int(100 - geo * 100)
        return max(1, min(100, score))
