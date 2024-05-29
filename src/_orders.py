# Order types:
from matplotlib import pyplot as plt
import logging
import copy
import os,yaml

class Order:
    def __init__(self, order_id, order_type, order_time, order_price, order_size, SL=None, TP=None):
        self.message = 'ORDER'
        self.order_id = order_id
        self.order_type = order_type
        self.order_time = order_time
        self.order_price = order_price
        self.order_size = order_size
        
        self.order_SL = SL
        self.order_TP = TP

        self.order_SL_price = None
        self.order_TP_price = None

        # Calculate SL and TP prices
        if self.order_type == 'OPEN_LONG':
            self.order_SL_price = self.order_price * (1 - abs(SL)/100) if self.order_SL is not None else None
            self.order_TP_price = self.order_price * (1 + abs(TP)/100) if self.order_TP is not None else None

        elif self.order_type == 'OPEN_SHORT':
            self.order_SL_price = self.order_price * (1 + abs(SL)/100) if self.order_SL is not None else None
            self.order_TP_price = self.order_price * (1 - abs(TP)/100) if self.order_TP is not None else None


    def __str__(self):
        # round to 6 significant digits
        return f'Order[{self.order_id}],{self.order_type},{self.order_size:.8f},{self.order_price:.6f},{self.order_time},{self.order_SL_price},{self.order_TP_price}'
        #return f'Order[{self.order_id}],{self.order_type},{self.order_size},{self.order_price},{self.order_time}'

    def __repr__(self):
        return f'Order[{self.order_id}],{self.order_type},{self.order_size:.8f},{self.order_price:.6f},{self.order_time},{self.order_SL_price},{self.order_TP_price}'

    def __eq__(self, other):
        return self.order_id == other.order_id

    def __hash__(self):
        return hash(self.order_id)
    
    def to_dict(self):
        return {
            'message': self.message,
            'order_id': self.order_id,
            'order_type': self.order_type,
            'order_time': self.order_time,
            'order_price': self.order_price,
            'order_size': self.order_size,
            'order_SL': self.order_SL,
            'order_TP': self.order_TP,
        }
    
    @classmethod
    def from_dict(cls, order_dict):
        return cls(
            message = order_dict['message'],
            order_id=order_dict['order_id'],
            order_type=order_dict['order_type'],
            order_time=order_dict['order_time'],
            order_price=order_dict['order_price'],
            order_size=order_dict['order_size'],
            SL=order_dict['order_SL'],
            TP=order_dict['order_TP']
        )
    
    @classmethod
    def isinstance(cls, other):
        return cls.order_id == other.order_id

class OpenLong(Order):
    def __init__(self, order_id, order_time, order_price, order_size,SL = None, TP = None):
        super().__init__(order_id, 'OPEN_LONG', order_time, order_price, order_size, SL, TP)

    @classmethod
    def isinstance(cls, other):
        return other.order_type == 'OPEN_LONG'

class OpenShort(Order):
    def __init__(self, order_id, order_time, order_price, order_size,SL = None, TP = None):
        super().__init__(order_id, 'OPEN_SHORT', order_time, order_price, order_size, SL, TP)

    @classmethod
    def isinstance(cls, other):
        return other.order_type == 'OPEN_SHORT'

class CloseLong(Order):
    def __init__(self, order_id, order_time, order_price, order_size,SL = None, TP = None):
        super().__init__(order_id, 'CLOSE_LONG', order_time, order_price, order_size, SL, TP)

    @classmethod
    def isinstance(cls, other):
        return other.order_type == 'CLOSE_LONG'

class CloseShort(Order):
    def __init__(self, order_id, order_time, order_price, order_size,SL = None, TP = None):
        super().__init__(order_id, 'CLOSE_SHORT', order_time, order_price, order_size, SL, TP)

    @classmethod
    def isinstance(cls, other):
        return other.order_type == 'CLOSE_SHORT'

class NoOrder(Order):
    def __init__(self,time):
        super().__init__(None, 'NO_ORDER', time, None, None, None, None)
        self.message = 'NO_ORDER'


class Position:
    def __init__(self, margin) -> None:
        self.margin = margin 


class Long(Position):
    def __init__(self, margin) -> None:
        super().__init__(margin)
        self.message = 'LONG'

    def __str__(self):
        return f'Position[{self.message}],{self.margin}'

    def __repr__(self):
        return f'Position[{self.message}],{self.margin}'
    
    def to_dict(self):
        return {
            'message': self.message,
            'margin': self.margin
        }
    
    @classmethod
    def from_dict(cls, position_dict):
        return cls(
            message = position_dict['message'],
            margin=position_dict['margin']
        )
    
    @classmethod
    def isinstance(cls, other):
        return other.message == 'LONG'
    
class Short(Position):
    def __init__(self, margin) -> None:
        super().__init__(margin)
        self.message = 'SHORT'

    def __str__(self):
        return f'Position[{self.message}],{self.margin}'

    def __repr__(self):
        return f'Position[{self.message}],{self.margin}'

    def to_dict(self):
        return {
            'message': self.message,
            'margin': self.margin
        }
    
    @classmethod
    def from_dict(cls, position_dict):
        return cls(
            message = position_dict['message'],
            margin=position_dict['margin']
        )
    
    @classmethod
    def isinstance(cls, other):
        return other.message == 'SHORT'


class OrderBook():
    def __init__(self, pair : str = None) -> None:
        # Logger
        self.logger = logging.getLogger('OrderBook')
        self.logger.setLevel(logging.DEBUG)
        # Orders
        self.order_history = list()
        self.open_orders = dict()
        self.sl_tp_triggered_orders = set()
        self.sl_triggered_order_count = 0
        self.sl_triggered_order_count_long = 0
        self.sl_triggered_order_count_short = 0
        self.margin_failed_orders = set()
        # Orderbook 
        self.pair = pair
        self.price = None
        self.check_margin = False
        self.fee_included = False
        self.fee_percent = 0.0 
        self.paid_fee = 0.0
        self.stop_loss = None

        self.win = 0
        self.loss = 0

        # Margin
        # Read from config.yaml
        # self.margin = ...
        try:
            with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.yaml')) as f:
                config = yaml.load(f, Loader=yaml.FullLoader)
                self.balance = config['balance']
                self.check_fee = config['check_fee']
                if self.check_fee:
                    self.fee_percent = config['fee_percent']
                    self.fee_included = config['include_fee']
                self.check_margin = config['margin_check']
        except Exception as e:
            self.logger.error(f'Error reading config.yaml: {e}')
            exit()
        # Data to be saved
        self.df = None

    def get_open_orders(self):
        return [x.order_id for x in self.open_orders.values()]

    def set_stop_loss(self, stop_loss):
        if stop_loss is not None:
            self.stop_loss = stop_loss

    def close_orderbook(self, close_price, time, df):
        # Close all open orders
        self.logger.info("Closing orderbook")
        open_orders_copy = copy.deepcopy(self.open_orders)
        for id, order in open_orders_copy.items():
            if order.order_type == 'OPEN_LONG':
                close_order = CloseLong(id,time, close_price, order.order_size)
                close_order = self.fill_close_order(close_order)
                self.order_history.append(close_order)
                self.logger.debug(f'{close_order}')
            elif order.order_type == 'OPEN_SHORT':
                close_order = CloseShort(id,time, close_price, order.order_size)
                close_order = self.fill_close_order(close_order)
                self.order_history.append(close_order)
                self.logger.debug(f'{close_order}')
        self.logger.info(f"Win: {self.win} | Loss: {self.loss if self.loss != 0 else 1e-10} | Profit Factor: {self.win/abs(self.loss) if self.loss != 0 else self.win}")
        self.df = df

    def update_price(self, ohlcv, time):
        # data = {'open', 'high', 'low', 'close', 'volume'}
        self.handle_SL_TP(ohlcv, time)
        self.handle_margin_call(ohlcv["close"])

    def handle_SL_TP(self, ohlcv, time) -> None:
        """
        Handle stop loss and take profit orders

        Args:
            price (_type_): Updated price every tick by backtester and simulator.
        """
        open_price, high_price, low_price, close_price = ohlcv['open'], ohlcv['high'], ohlcv['low'], ohlcv['close']

        # Iterate open orders to check if SL/TP
        open_orders_copy = copy.deepcopy(self.open_orders)
        for id, order in open_orders_copy.items():
            if order.order_type == 'OPEN_LONG':
                if order.order_SL_price is not None and low_price <= order.order_SL_price:
                    close_order = CloseLong(id, time, order.order_SL_price, order.order_size)
                    close_order = self.fill_close_order(close_order)
                    self.order_history.append(close_order)
                    self.sl_tp_triggered_orders.add(id)
                    self.sl_triggered_order_count += 1
                    self.sl_triggered_order_count_long += 1
                    self.logger.debug(f'SL:{close_order}')
                elif order.order_TP_price is not None and high_price >= order.order_TP_price:
                    close_order = CloseLong(id, time, order.order_TP_price, order.order_size)
                    close_order = self.fill_close_order(close_order)
                    self.order_history.append(close_order)
                    self.sl_tp_triggered_orders.add(id)
                    
                    self.logger.debug(f'TP:{close_order}')
            elif order.order_type == 'OPEN_SHORT':
                if order.order_SL_price is not None and high_price >= order.order_SL_price:
                    close_order = CloseShort(id,time, order.order_SL_price, order.order_size)
                    close_order = self.fill_close_order(close_order)
                    self.order_history.append(close_order)
                    self.sl_tp_triggered_orders.add(id)
                    self.sl_triggered_order_count += 1
                    self.sl_triggered_order_count_short += 1
                    self.logger.debug(f'SL:{close_order}')
                elif order.order_TP_price is not None and low_price <= order.order_TP_price:
                    close_order = CloseShort(id,time, order.order_TP_price, order.order_size)
                    close_order = self.fill_close_order(close_order)
                    self.order_history.append(close_order)
                    self.sl_tp_triggered_orders.add(id)
                    
                    self.logger.debug(f'TP:{close_order}')


    def margin_check(self,price,order_size, order_id) -> bool:
        """
        Check if there is enough margin to open order.

        Returns:
            bool: True if there is enough margin, False otherwise.
        """
        if not self.check_margin:
            return True
        
        if self.balance < price * order_size * (1 + self.fee_percent):
            self.logger.debug(f'Insufficient margin to open order. Balance: {self.balance} | Order: {price * order_size * (1 + self.fee_percent)}')
            self.margin_failed_orders.add(order_id)
            return False
        return True

    def handle_margin_call(self, price) -> None:
        """
        Handle margin call. Close all open orders if margin call is triggered.


        Args:
            price (_type_): Updated price every tick by backtester and simulator.
        """
        # No leverage applied, no needed for now.
        pass


    def fill_open_order(self, order: Order):
        actual_order_size = order.order_size
        fee_taken_order_size = order.order_size * (1 - self.fee_percent)
        order.order_size = fee_taken_order_size if self.fee_included else actual_order_size
        self.open_orders[order.order_id] = order
        open_order_fee = order.order_price * actual_order_size * self.fee_percent
        self.paid_fee += open_order_fee
        self.balance -= order.order_price * actual_order_size 
        return order


    def fill_close_order(self, order: Order):
        actual_order_size = self.open_orders[order.order_id].order_size
        fee_taken_order_size = self.open_orders[order.order_id].order_size * (1 - self.fee_percent)
        order.order_size = fee_taken_order_size if self.fee_included else actual_order_size
        close_order_fee = order.order_price * actual_order_size * self.fee_percent   
        self.paid_fee += close_order_fee
        self.balance += self.open_orders[order.order_id].order_price  * fee_taken_order_size 
        profit = self.calculate_profit(self.open_orders[order.order_id], order)
        self.balance += profit
        return order

    def add_order(self, order: Order):
        try:
            # if no order add
            if order.order_type == 'NO_ORDER':
                self.order_history.append(order)
            elif OpenLong.isinstance(order) or OpenShort.isinstance(order):
                if order.order_id in self.open_orders.keys():
                    self.logger.error(f'Order already exists in orderbook. {order}')
                    return
                if self.margin_check(order.order_price, order.order_size, order.order_id):
                    order = self.fill_open_order(order)
                    self.order_history.append(order)
                    self.logger.debug(f'{order}')
                else:
                    self.logger.warning(f'Insufficient margin to open order. {order}')
                    self.order_history.append(NoOrder(order.order_time))
            elif CloseLong.isinstance(order) or CloseShort.isinstance(order):
                # It might be possible that the order is already closed by SL/TP
                if order.order_id in self.sl_tp_triggered_orders:
                    self.logger.debug(f'Order unable to close due to SL/TP. {order}')
                    self.sl_tp_triggered_orders.remove(order.order_id)
                    self.order_history.append(NoOrder(order.order_time))
                # It might be unopend order due to margin call
                elif order.order_id in self.margin_failed_orders:
                    self.logger.debug(f'Order unable to close due to failed opening as of margin call. {order}')
                    self.margin_failed_orders.remove(order.order_id)
                    self.order_history.append(NoOrder(order.order_time))
                elif order.order_id not in self.open_orders.keys():
                    self.logger.error(f'Order does not exist in orderbook. Moving on... (PLEASE CHECK YOUR CODE FOR POSSIBLE ERRORS){order}')
                else:
                    order = self.fill_close_order(order)
                    self.order_history.append(order)
                    self.logger.debug(f'{order}')
        except KeyError as e:
            self.logger.error(f'KeyError: {e}')
            self.logger.error(f'Dumping order book.')
            for key,value in self.open_orders.items():
                if value.order_type != 'NO_ORDER':
                    self.logger.error(f'[{key}]{value}')
            exit()
        except Exception as e:
            self.logger.error(f'Exception: {e}')
            self.logger.error(f'Dumping order book.')
            for key,value in self.open_orders.items():
                if value.order_type != 'NO_ORDER':
                    self.logger.error(f'[{key}]{value}')
            exit()
            
    def calculate_profit(self, open_order: Order, close_order: Order):
        if open_order.order_type == 'OPEN_LONG' and close_order.order_type == 'CLOSE_LONG':
            profit = (close_order.order_price - open_order.order_price) * open_order.order_size
            if profit > 0:
                # 0.35 - 0.2 * 2 = -0.05 
                self.win += profit 
            else:
                self.loss += profit 
            self.open_orders.pop(open_order.order_id)
            return profit
        elif open_order.order_type == 'OPEN_SHORT' and close_order.order_type == 'CLOSE_SHORT':
            profit = (open_order.order_price - close_order.order_price)*open_order.order_size
            if profit > 0:
                self.win += profit 
            else:
                self.loss += profit 
            self.open_orders.pop(open_order.order_id)
            return profit
        else:
            raise Exception('Invalid order types for calculating profit')