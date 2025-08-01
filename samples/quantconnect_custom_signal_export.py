# region imports
from AlgorithmImports import *
import requests
# endregion


# This sample demonstrates how to use a custom signal export provider
# to export portfolio targets to vBase.
# The sample follows the QuantConnect documentation on custom signal exports:
# https://www.quantconnect.com/docs/v2/writing-algorithms/live-trading/signal-exports/key-concepts#04-Custom-Signal-Exports


# The standard production vBase API URL.
VBASE_STAMP_API_URL = "https://app.vbase.com/api/v1/stamp/"
# Replace with the collection CID of the collection you want to export to.
# Collection CID is the SHA3-256 hash of the collection name.
# It can be found in the collections section of the user profile in the vBase app.
COLLECTION_CID = "0x36f028580bb02cc8272a9a020f4200e346e276ae664e45ee80745574e2f5ab80"


class CustomSignalExport:
    """
    This is a custom signal export provider that exports portfolio targets to vBase.
    """

    def __init__(self, algorithm, vbase_api_key):
        self.algorithm = algorithm
        self.algorithm.log("CustomSignalExport.__init__()")
        self.algorithm.log(
            f"CustomSignalExport.__init__(): vbase_api_key = {vbase_api_key}"
        )
        self.vbase_api_key = vbase_api_key

    def send(self, parameters: SignalExportTargetParameters) -> bool:
        self.algorithm.log("CustomSignalExport.send()")

        # Get the portfolio.
        targets = [
            PortfolioTarget.percent(parameters.algorithm, x.symbol, x.quantity)
            for x in parameters.targets
        ]
        df_data = pd.DataFrame(
            [{"sym": x.symbol.value, "wt": x.quantity} for x in targets]
        )

        # Convert DataFrame to CSV string (no index).
        csv_data = df_data.to_csv(index=False)
        self.algorithm.log(f"CustomSignalExport.send(): csv_data = \n{csv_data}")

        try:
            # Make the vBase API request.
            response = requests.post(
                VBASE_STAMP_API_URL,
                # vBase API authenticates using the API key in the Authorization header.
                headers={"Authorization": f"Bearer {self.vbase_api_key}"},
                # The data to send to vBase.
                data={
                    # The collectionCid is the CID of the collection to export to.
                    "collectionCid": COLLECTION_CID,
                    # The data is the CSV string of the portfolio targets.
                    "data": csv_data,
                    # A boolean indicating whether to store the stamped file.
                    "storeStampedFile": "true",
                    # A boolean indicating whether to make the request idempotent.
                    # If the request is idempotent, only the first stamp for a given portfolio will be made.
                    # If the request is not idempotent, a new stamp will be made for each request.
                    "idempotent": "false",
                },
                # The timeout is the number of seconds to wait for the response.
                # Stamps may take a few seconds to process since they wait for
                # the confimation of the blockchain transaction.
                # We add a margin of satefy to account for any network contention.
                timeout=60,
            )
            response.raise_for_status()
            self.algorithm.log("CustomSignalExport.send(): Signal export succeeded")
            self.algorithm.log(
                f"CustomSignalExport.send(): response.json() =\n{response.json()}"
            )
            self.algorithm.log(
                f"CustomSignalExport.send(): Sent {len(parameters.targets)} targets."
            )
            success = True
        except Exception as e:
            self.algorithm.log(f"CustomSignalExport.send(): Signal export failed: {e}")
            success = False

        return success

    def dispose(self):
        pass


class VirtualBlackGuanaco(QCAlgorithm):
    """
    This is a sample algorithm that demonstrates how to use a custom signal export provider
    to export portfolio targets to vBase.
    """

    def initialize(self):
        self.log("VirtualBlackGuanaco.initialize()")
        self.set_start_date(2024, 1, 9)
        self.set_cash(100000)
        self.add_equity("SPY", Resolution.MINUTE)
        self.add_equity("BND", Resolution.MINUTE)
        vbase_api_key = self.get_parameter("VBASE_API_KEY")
        self.signal_export.add_signal_export_providers(
            CustomSignalExport(
                self,
                vbase_api_key,
            )
        )

    def on_data(self, data: Slice):
        if not self.portfolio.invested:
            self.set_holdings("SPY", 1.00)
            self.set_holdings("BND", 0.00)
