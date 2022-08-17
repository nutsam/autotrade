from cmath import log
from multiprocessing import managers
from sys import last_traceback
from ..binance_api import BinanceAPIManager
from ..logger import Logger
from ..websocket import WebSocketManager

class nullstrategy:
    def __init__(self, manager: BinanceAPIManager, websocket: WebSocketManager, logger: Logger):
        self.manager = manager
        self.websocket = websocket
        self.logger = logger
        self.symbol = 'ETHUSDT'
        self.position = False
        self.buyprice = 1879
        self.cash = 0
        self.stopprice = 0
        self.profitprice = 0
        self.quantity = 0
    
    def run_strategy(self):
        while True:
            latest_price = self.websocket.get_latest_price()

            if self.position:
                if latest_price <= self.stopprice or latest_price >= self.profitprice:
                    self.manager.create_order(self.symbol, 'SELL', self.quantity)
                    self.logger.info(f'{self.symbol}  SELL  price: {})
                    
                    self.position = False
            else:
                if self.buyprice*(1-0.1) <= latest_price <= self.buyprice*(1+0.1):    
                    self.cash = self.manager.get_wallet_balance()
                    quantity = (self.cash * 0.06) / latest_price
                    self.manager.create_order(self.symbol, 'BUY', quantity)
                    entry_price = self.manager.get_entry_price()
                    self.stopprice = entry_price * (1-0.05)
                    self.profitprice = entry_price * (1+0.10)
                    self.position = True
                