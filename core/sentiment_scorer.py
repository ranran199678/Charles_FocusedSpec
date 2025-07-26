from utils import data_fetcher

class SentimentScorer:
    def __init__(self, config=None):
        pass

    def analyze(self, symbol, price_df=None):
        sentiment = data_fetcher.get_sentiment_score(symbol)
        score = int((sentiment + 1) * 50)
        return max(1, min(100, score))
