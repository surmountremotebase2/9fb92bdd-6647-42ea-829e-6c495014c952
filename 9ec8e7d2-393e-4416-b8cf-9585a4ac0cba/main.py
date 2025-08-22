from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import ROC
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        super().__init__()
        self.tickers = ["TQQQ", "SPY"]

    @property
    def interval(self):
        # Daily interval to review performance
        return "1day"

    @property
    def assets(self):
        return self.tickers

    def run(self, data):
        # Initialize allocation with no position
        allocation_dict = {"TQQQ": 0.0, "SPY": 0.0}

        # Compute the 5-day Rate of Change (ROC) for TQQQ and SPY
        roc_tqqq = ROC("TQQQ", data["ohlcv"], 5)
        roc_spy = ROC("SPY", data["ohlcv"], 5)

        # Be sure we have both ROCs calculated
        if roc_tqqq and roc_spy:
            last_roc_tqqq = roc_tqqq[-1]
            last_roc_spy = roc_spy[-1]

            # Log the ROC for review
            log(f"TQQQ 5-day ROC: {last_roc_tqqq}, SPY 5-day ROC: {last_roc_spy}")

            # Strategy: Compare the ROC of TQQQ and SPY, allocate to the one with higher recent performance
            if last_roc_tqqq > last_roc_spy:
                # If TQQQ outperforms SPY, allocate more to TQQQ
                allocation_dict["TQQQ"] = 0.9  # Allocate 90% to TQQQ
                allocation_dict["SPY"] = 0.1  # Leave 10% as a hedge with SPY
            else:
                # If SPY outperforms TQQQ, allocate more to SPY
                allocation_dict["TQQQ"] = 0.1  # Allocate 10% to TQQQ to maintain exposure
                allocation_dict["SPY"] = 0.9  # Allocate 90% to SPY

        return TargetAllocation(allocation_dict)