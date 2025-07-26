from utils import data_fetcher

class GrowthConsistencyScanner:
    def __init__(self, config=None):
        pass

    def analyze(self, symbol, price_df=None):
        growth = data_fetcher.get_growth_rate(symbol)
        score = int(min(100, max(1, growth + 50)))
        return score
