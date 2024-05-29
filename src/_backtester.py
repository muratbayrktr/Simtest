from _orders import OrderBook, Order, NoOrder
from _base_socket import Server
from time import time, ctime, sleep
from datetime import datetime
import os 
import pandas as pd
from matplotlib import pyplot as plt
import logging
import yaml



class Backtester(Server):
    def __init__(self, interval, start_date, final_date, pair):
        super().__init__()
        # Available exchanges
        # - Binance Spot
        # - Binance Futures
        # - Bybit Futures
        available_exchanges = ['binance_spot', 'binance_futures', 'bybit_futures']

        # load config.yaml get the speed
        self.logger = logging.getLogger('Backtester')
        try:
            with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.yaml')) as f:
                config = yaml.load(f, Loader=yaml.FullLoader)
                speed = config['speed']
                exchange = config['exchange']
                market_type = config['market_type']
        except yaml.YAMLError as exc:
            self.logger.error(exc)

        if exchange.lower() + "_" + market_type.lower() not in available_exchanges:
            raise Exception("Invalid exchange or market type. Please check config.yaml")
        self.logger.info(f"Exchange: {exchange.capitalize()} - Market Type: {market_type.capitalize()}")

        # Conditional import
        if exchange.lower() == 'binance':
            if market_type.lower() == 'spot':
                from data_ingestion.binance_spot import BinanceSpot as DataCollector
            elif market_type.lower() == 'futures':
                from data_ingestion.binance_futures import BinanceFutures as DataCollector
        elif exchange.lower() == 'bybit':
            if market_type.lower() == 'futures':
                from data_ingestion.bybit_futures import BybitFutures as DataCollector

        self.is_running = False
        self.speed = 10**(-speed)
        self.OrderBook = OrderBook(pair=pair)
        self.logger.info(f"Dataset summary: from {start_date} to {final_date} with {interval} interval with pair {pair}.")
        self.collector = DataCollector(start_date, final_date, interval, pair)
        self.data_path = self.collector.get_path()
        self.logger.info(f"Dataset path: {self.data_path}")
        self.convert_dates = lambda x: datetime.strptime(str(x), '%Y-%m-%d %H:%M:%S')
        self.cumulative_profit = 0

    def load_data(self):
        # load data from data_path  
        self.df = pd.read_csv(self.data_path)
        # rename columns=['date', 'open', 'high', 'low', 'close', 'volume']
        self.df.columns = self.collector.get_columns()
        # set the date column as the indexl
        self.df.set_index('date', inplace=True)
        self.tick = 0
        self.logger.info(f"Data loaded successfully: Size: {len(self.df)}")
        return True

    def feed_data(self):
        if self.tick >= len(self.df):
            self.send({'message' : 'END'})
            self.OrderBook.close_orderbook(self.df['close'].iloc[-1],str(self.df.index[-1])[:-3],self.df)
            self.stop()
            return
        data = {'price' : self.df['close'].iloc[self.tick], 
                'tick' : self.tick,
                'time':str(self.df.index[self.tick])[:-3], 
                'message' : 'PRICE', 'size' : len(self.df),
                'data' : self.df.iloc[self.tick].to_dict()}
        self.OrderBook.update_price(data['data'],data['time'])
        data['open_orders'] = len(self.OrderBook.get_open_orders())
        self.send(data)
        # print("Bt: sent:", data)
        self.tick += 1
        sleep(self.speed)
    
    def on_receive(self, data):
        if data['message'] == 'START':
            self.tick = 0
        elif data['message'] == 'NO_ORDER':
            self.OrderBook.add_order(NoOrder(data['order_time']))
        elif data['message'] == 'ORDER':
            self.OrderBook.add_order(Order(data['order_id'], data['order_type'], data['order_time'], data['order_price'], data['order_size'], data['order_SL'], data['order_TP']))
        elif data['message'] == 'ORDERLIST':
            for order in data['data']:
                self.OrderBook.add_order(Order(order['order_id'], order['order_type'], order['order_time'], order['order_price'], order['order_size'],order['order_SL'],order['order_TP']))
        if self.is_running:
            self.feed_data()

    def disconnect(self):
        super().disconnect()
        return self.OrderBook
        
if __name__ == '__main__':
    logger = logging.getLogger('Backtester Main')
    try:
        backtester = Backtester('1m','2023-06-01','2023-06-02')
        backtester.load_data()
        backtester.start()
    except ConnectionRefusedError:
        backtester.port += 1
        logger.warning("Connection refused. Using another port: ", backtester.port)
        backtester.start()
    backtester.disconnect()
    logger.info("\nBacktester stopped")
    backtester.plot()
    