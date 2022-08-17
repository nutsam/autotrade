
from . import config
from .binance_api import BinanceAPIManager
from .logger import Logger
from .config import Config
from .websocket import WebSocketManager
from .strategy import nullstrategy

def main():
    logger = Logger()
    logger.info("Starting")

    config = Config()
    manager = BinanceAPIManager(config, logger)
    wsm = WebSocketManager('btcusdt', '1m')
    wsm.run('btcusdt', '1m')

    strategy = nullstrategy(manager, wsm, logger)
    


if __name__ == '__main__':
    main()