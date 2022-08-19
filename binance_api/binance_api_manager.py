from statistics import quantiles
from binance.client import Client
from ..logger import Logger
from ..config import Config
from enum import Enum

class Order(Enum):
    EMPTY = 'EMPTY',
    COMPLETE = 'COMPLETE',
    REJECTED = 'REJECTED',
    

class BinanceAPIManager:
    def __init__(self, config: Config, logger: Logger):
        self.api_key = config.BINANCE_API_KEY
        self.api_secret = config.BINANCE_API_SECRET_KEY
        self.logger = logger
        self.position = 0
        self.lock = False

    def create_order(self, symbol, side, quantity):
        client = Client(self.api_key, self.api_secret)
        # market order
        if not self.lock:
            client.futures_create_order(symbol=symbol, side=side, type='MARKET', quantity=quantity)
            self.logger.info(f'Create market order, symbol:{symbol}, quantity:{quantity}')
            self.lock = self._check_position(symbol, expectAmt=quantity)
        else:
            self.logger.debug(f'There is something wrong, transaction system is locked.')

    def create_stop_order(self, symbol, price):
        client = Client(self.api_key, self.api_secret)
        if not self.lock:
            client.futures_create_order(
                symbol=symbol, side='SELL', type='STOP_MARKET', stopPrice=price, closePosition=True)
            self.lock = self._check_position(symbol, expectAmt=0)
        else:
            self.logger.debug(f'There is something wrong, transaction system is locked.')

    def create_take_profit_order(self, symbol, price):
        client = Client(self.api_key, self.api_secret)
        if not self.lock:
            client.futures_create_order(
                symbol=symbol, side='SELL', type='TAKE_PROFIT_MARKET', stopPrice=price, closePosition=True)
            self.lock = self._check_position(symbol, expectAmt=0)
        else:
            self.logger.debug(f'There is something wrong, transaction system is locked.')

    def get_entry_price(self, symbol):
        client = Client(self.api_key, self.api_secret)
        posinfo = client.futures_position_information(symbol=symbol)[0]
        return posinfo['entryPrice']

    def get_wallet_balance(self):
        client = Client(self.api_key, self.api_secret)
        return client.futures_account()['totalWalletBalance']

    def _check_position(self, symbol, expectAmt):
        client = Client(self.api_key, self.api_secret)
        posinfo = client.futures_position_information(symbol=symbol)[0]
        return expectAmt != posinfo['positionAmt']

    
        



        