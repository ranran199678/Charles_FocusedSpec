from core.trend_shift_detector import TrendShiftDetector

if __name__ == "__main__":
    symbol = "PLTR"
    interval = "1min"
    frequency = 60  # שניות בין הרצות
    cycles = 3      # כמות חזרות (None ללולאה אינסופית)

    agent = TrendShiftDetector(
        symbol=symbol,
        interval=interval,
        frequency_sec=frequency,
        live_mode=True
    )
    agent.run_live(cycles=cycles)
