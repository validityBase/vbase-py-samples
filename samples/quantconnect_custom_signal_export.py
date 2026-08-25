# region imports
from AlgorithmImports import *

# endregion


class VirtualBlackGuanaco(QCAlgorithm):
    """Export target portfolio weights with QuantConnect's vBase provider."""

    def initialize(self):
        self.set_start_date(2024, 1, 9)
        self.set_end_date(2024, 1, 10)
        self.set_cash(100000)
        self.add_equity("SPY", Resolution.MINUTE)
        self.add_equity("BND", Resolution.MINUTE)
        self.signal_exported = False

        api_key = self.get_parameter("VBASE_API_KEY")
        collection_name = self.get_parameter("VBASE_COLLECTION_NAME")
        if not api_key or not collection_name:
            raise ValueError(
                "Set the VBASE_API_KEY and VBASE_COLLECTION_NAME project parameters."
            )

        self.signal_export.add_signal_export_provider(
            VBaseSignalExport(
                api_key,
                collection_name,
                store_stamped_file=True,
                idempotent=False,
            )
        )

    def on_data(self, data: Slice):
        if self.signal_exported:
            return

        targets = [
            PortfolioTarget("SPY", 1.00),
            PortfolioTarget("BND", 0.00),
        ]
        if not self.signal_export.set_target_portfolio(targets):
            raise RuntimeError("QuantConnect could not export the portfolio targets.")
        self.signal_exported = True
