import json
import websocket
from ..logger import Logger

class WebSocketManager:
    def __init__(self, logger: Logger):
        self.logger = logger
        self.close = None

    def run(self, symbol, interval):
        socket = f'wss://fstream.binance.com/ws/{symbol}@kline_{interval}'
        ws = websocket.WebSocketApp(socket, on_message=self.on_message, on_error=self.on_error, on_close=self.on_close)
        ws.run_forever()
    
    def on_message(self, ws, message):
        message = json.loads(message)
        self.open = message['k']['o']
        self.close = message['k']['c']
        self.high = message['k']['h']
        self.low = message['k']['l']
        self.logger.debug(f'Open: {self.open}, Close: {self.close}, High: {self.high}, Low: {self.low}')

    def on_error(self, ws, message):
        print(message)

    def on_close(self, ws, code, message):
        if message: print(message)

    def get_latest_price(self):
        return self.close


if __name__ == '__main__':
    wsm = WebSocketManager()
    wsm.run('btcusdt', '1m')