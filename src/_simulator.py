from _orders import OrderBook, Order, NoOrder
from _base_socket import Server
from _montecarlo import MonteCarlo
from time import time, ctime, sleep
from datetime import datetime
import os 
import pandas as pd
from matplotlib import pyplot as plt
import yaml
import logging



class Simulator(Server):
    def __init__(self, data_path = '../data/generated/long_sim.csv', host='127.0.0.1', port=5000):
        super().__init__(host, port)
        with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.yaml')) as f:
            config = yaml.load(f, Loader=yaml.FullLoader)

        speed = config['speed']
        self.speed = 10**(-speed)
        self.is_running = False
        self.OrderBook = OrderBook()
       	# code for getting data path	
        self.data_path = data_path
        self.convert_dates = lambda x: datetime.strptime(str(x), '%Y-%m-%d %H:%M:%S')
        self.cumulative_profit = 0

    def load_data(self):
        # load data from data_path  
        self.df = pd.read_csv(self.data_path)
        # rename columns=['date', 'open', 'high', 'low', 'close', 'volume']
        self.df.columns =['date','close']
        # set the date column as the indexl
        self.df.set_index('date', inplace=True)
        self.tick = 0
        logging.info(f"Data loaded successfully: Size: {len(self.df)}")

    def feed_data(self):
        if self.tick >= len(self.df):
            self.send({'message' : 'END'})
            self.OrderBook.close_orderbook(self.df['close'].iloc[-1],self.df)
            self.stop()
            return
        data = {'price' : self.df['close'].iloc[self.tick], 'tick' : self.tick,'time':str(self.df.index[self.tick])[:-3], 'message' : 'PRICE', 'size' : len(self.df)}
        self.send(data)
        self.tick += 1
        sleep(self.speed)
    
    def on_receive(self, data):
        if data['message'] == 'START':
            logging.info("STRATEGY: START")
            self.tick = 0
        elif data['message'] == 'NO_ORDER':
            self.OrderBook.add_order(NoOrder(data['order_time']))
        elif data['message'] == 'ORDER':
            self.OrderBook.add_order(Order(data['order_id'], data['order_type'], order['order_time'], data['order_price'], data['order_size']))
        elif data['message'] == 'ORDERLIST':
            for order in data['data']:
                self.OrderBook.add_order(Order(order['order_id'], order['order_type'], order['order_time'], order['order_price'], order['order_size']))
        if self.is_running:
            self.feed_data()

    def disconnect(self):
        super().disconnect()
        return self.OrderBook
        

    
