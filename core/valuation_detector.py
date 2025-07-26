from utils import data_fetcher

class ValuationAnomalyDetector:
    def __init__(self, config=None):
        pass

    def analyze(self, symbol, price_df=None):
        pe, sector_pe = data_fetcher.get_pe_ratio(symbol)
        if pe is not None and sector_pe != 0:
            rel = (sector_pe - pe) / sector_pe
            score = int(min(100, max(1, rel * 100 + 50)))
            return score
        return 1
