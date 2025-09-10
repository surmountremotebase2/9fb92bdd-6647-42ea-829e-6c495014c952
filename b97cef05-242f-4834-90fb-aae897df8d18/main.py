from surmount.base_class import Strategy, TargetAllocation
from surmount.data import InstitutionalOwnership, InsiderTrading

class TradingStrategy(Strategy):
    def __init__(self):
        # Define the assets under consideration.
        self.tickers = ["AAPL", "MSFT", "GOOGL", "AMZN"]
        # Add InstitutionalOwnership and InsiderTrading data objects for each ticker to the data_list.
        self.data_list = [InstitutionalOwnership(ticker) for ticker in self.tickers] + \
                         [InsiderTrading(ticker) for ticker in self.tickers]

    @property
    def assets(self):
        return self.tickers

    @property
    def interval(self):
        """Specify the data frequency required for this strategy."""
        return "1day"

    @property
    def data(self):
        """Return the data list containing InstitutionalOwnership and InsiderTrading data objects."""
        return self.data_list

    def run(self, data):
        """Define the core logic of the trading strategy."""
        allocation_dict = {}
        
        for ticker in self.tickers:
            allocation = 0.25  # Start with an equal allocation strategy as a base.
            
            # Check the latest institutional ownership data for positive changes.
            inst_key = ("institutional_ownership", ticker)
            if inst_key in data and len(data[inst_key]) > 0:
                recent_data = data[inst_key][-1]
                if recent_data["ownershipPercentChange"] > 0:
                    allocation += 0.1  # Encourage allocation if ownership percent is increasing.

            # Check the latest insider trading data for purchase actions.
            insider_key = ("insider_trading", ticker)
            if insider_key in data and len(data[insider_key]) > 0:
                latest_insider_action = data[insider_key][-1]
                if latest_insider_action["transactionType"].startswith("P") and latest_insider_action["acquisitionOrDisposition"] == 'A':
                    allocation += 0.1  # Encourage allocation if there's a recent insider purchase.
                elif latest_insider_action["transactionType"].startswith("S") and latest_insider_action["acquisitionOrDisposition"] == 'D':
                    allocation -= 0.1  # Discourage allocation if there's a recent insider sale.
            
            # Ensure allocation remains between 0 and 1.
            allocation = min(max(allocation, 0), 1)
            
            allocation_dict[ticker] = allocation

        # Normalize allocations to ensure they sum up to 1 or less.
        total_allocation = sum(allocation_dict.values())
        for ticker in allocation_dict:
            allocation_dict[ticker] /= total_allocation

        return TargetAllocation(allocation_dict)