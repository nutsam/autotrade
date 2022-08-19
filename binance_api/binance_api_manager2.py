import traceback
import time
from typing import Dict, Optional

from binance.client import Client
from binance.exceptions import BinanceAPIException

from ..config import Config
from ..logger import Logger
from .binance_stream_manager import BinanceCache, BinanceOrder, BinanceStreamManager, OrderGuard


class BinanceAPIManager:
    def __init__(self, config: Config, logger: Logger):
        # initializing the client class calls `ping` API endpoint, verifying the connection
        self.binance_client = Client(
            config.BINANCE_API_KEY,
            config.BINANCE_API_SECRET_KEY,
            tld=config.BINANCE_TLD,
        )
        # self.db = db
        self.logger = logger
        self.config = config

        self.cache = BinanceCache()
        self.stream_manager: BinanceStreamManager(
            self.cache,
            self.config,
            self.binance_client,
            self.logger,
        )

    def retry(self, func, *args, **kwargs):
        for attempt in range(20):
            try:
                return func(*args, **kwargs)
            except Exception:  # pylint: disable=broad-except
                self.logger.warning(f"Failed to Buy/Sell. Trying Again (attempt {attempt}/20)")
                if attempt == 0:
                    self.logger.warning(traceback.format_exc())
                time.sleep(1)
        return None

    def buy(self, symbol: str, price: float, quantity: float) -> BinanceOrder:
        return self.retry(self._buy, symbol, price, quantity)

    def _buy(self, symbol: str, price: float, quantity: float):
        with self.cache.open_balances() as balances:
            balances.clear()

        # Try to buy until successful
        order = None
        order_guard = self.stream_manager.acquire_order_guard()
        while order is None:
            try:
                order = self.binance_client.order_limit_buy(
                    symbol=symbol,
                    quantity=quantity,
                    price=price,
                )
                self.logger.info(order)
            except BinanceAPIException as e:
                self.logger.info(e)
                time.sleep(1)
            except Exception as e:  # pylint: disable=broad-except
                self.logger.warning(f"Unexpected Error: {e}")

        order_guard.set_order(origin_symbol, target_symbol, int(order["orderId"]))
        order = self.wait_for_order(order["orderId"], origin_symbol, target_symbol, order_guard)

        if order is None:
            return None

        self.logger.info(f"Bought {origin_symbol}")

        trade_log.set_complete(order.cumulative_quote_qty)

        return order