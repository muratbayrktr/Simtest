from _orders import OrderBook, OpenLong, OpenShort, CloseLong, CloseShort, NoOrder
from matplotlib import pyplot as plt
from datetime import datetime
from tqdm import tqdm
import pandas as pd
import os
import yaml
import logging
import json
# import groupby
from itertools import groupby

class TradingMetrics:
    def __init__(self, order_book, verbose=True):
        self.verbose = verbose
        # set logger name to TradingMetrics
        self.logger = logging.getLogger('TradingMetrics')
        self.logger.info("TradingMetrics initialized.")
        if not self.verbose:
            # set logging level to ERROR
            self.logger.setLevel(logging.ERROR)
        self.order_book = order_book
        if self.order_book is None:
            self.logger.error("Error in TradingMetrics: order_book is None. Quitting.")
            exit()
        if self.order_book.win == 0 and self.order_book.loss == 0:
            self.logger.warning("Warning in TradingMetrics: Win and Loss are both 0. Either strategy did NOT trade (this may be due to the frequency of the strategy and the backtesting period) or possible error in strategy. Please double check.")
        self.open_orders = {}
        self.num_trades = len(self.order_book.order_history)
        ########### define metrics to be tracked
        self.longs = []
        self.shorts = []
        self.win_rate = []
        self.pnl = []
        self.profit_factor = []
        self.drawdown = []
        self.rrr = []
        self.average_pnl = []
        self._core = {}
        self.total_position_size = 0
        self.position_count = 0
        self.avg_position_size = 0

        self.profits = 0
        self.losses = 0
        self.winning_count = 0
        self.losing_count = 0

        self.largest_open_position_size = 0
        self.largest_open_position_size_usd = 0
        self.maximum_unrealized_loss = 0

        ########## long-short specific metrics to be tracked
        self.winning_count_long = 0
        self.winning_count_short = 0
        self.losing_count_long = 0
        self.losing_count_short = 0
        self.profits_long = 0
        self.profits_short = 0
        self.losses_long = 0
        self.losses_short = 0


        ########## define metrics to be tracked

        # Order Book price information
        self.df = self.order_book.df
        self.price_dict = {}
        try:
            for i in tqdm(range(len(self.df)), desc="Creating price dictionary"):
                self.price_dict[str(self.df.iloc[i].name)[:-3]] = self.df.iloc[i].close
        except Exception as e:
            self.logger.error(e)
            self.logger.error("Error in TradingMetrics: Either df is None or df is not in the correct format")
        # config.yaml path is relative to the main.py file
        with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.yaml')) as f:
            self.config = yaml.load(f, Loader=yaml.FullLoader)
            self.save_fig = self.config['save_fig']
            self.save_entry_exit = self.config['save_entry_exit']
        self.save_path = None
        self.font_size = 14


    def calculate_metrics(self, save_path):
        # check if list index out of range 
        if self.num_trades == 0:
            self.logger.warning("Warning in TradingMetrics: Number of trades is 0")
        else:
            for order_index in tqdm(range(self.num_trades),desc="Adding orders to TradingMetrics"):
                self.add_order(self.order_book.order_history[order_index])
                tick_price = self.price_dict[str(self.order_book.order_history[order_index].order_time)]
                self.calculate_maximum_unrealized_loss(tick_price)
            
            self.post_process()

            # Save these results as csv files
            self.save_results(save_path=save_path)
            try:
                max_key_length = max(len(str(key)) for key in self._core.keys())
                for key, value in self._core.items():
                    if key == "Pair":
                        info = f"{key.ljust(max_key_length)}: {value.ljust(10)}"
                    elif int(value) == value:
                        value = int(value)
                        info = f"{key.ljust(max_key_length)}: {str(value).ljust(10)}"
                    else:
                        info = f"{key.ljust(max_key_length)}: {str(round(value,5)).ljust(10)}"

                    self.logger.info(info)
            except:
                pass
            if self.save_fig:
                try:
                    self.plot_all(save_fig=True, save_path=save_path)
                except Exception as e:
                    self.logger.error(e)
            if self.save_entry_exit:
                try:
                    abs_save_path = os.path.abspath(save_path)
                    self.plot_position_entry_exit(abs_save_path=abs_save_path)
                except Exception as e:
                    self.logger.error(e)
        return self._core
    
    def calculate_largest_position_size(self,price):
        money_spent = 0
        for order in self.open_orders.values():
            money_spent += order.order_price * order.order_size
        if money_spent > self.largest_open_position_size_usd:
            self.largest_open_position_size_usd = money_spent
            self.largest_open_position_size = money_spent / price

    def calculate_maximum_unrealized_loss(self,price):
        """This function calculates the maximum unrealized loss of the strategy
        in order to calculate the suggested leverage and stop loss.

        Args:
            price (_type_): price
        """
        curr_pnl = 0
        for order in self.open_orders.values():
            if "LONG" in order.order_type:
                curr_pnl += (price - order.order_price) * order.order_size
            elif "SHORT" in order.order_type:
                curr_pnl += (order.order_price - price) * order.order_size
        if curr_pnl < self.maximum_unrealized_loss:
            self.maximum_unrealized_loss = curr_pnl

    
    def add_order(self, order):
        try:
            if OpenLong.isinstance(order) or OpenShort.isinstance(order):
                self.total_position_size += order.order_size
                self.position_count += 1
                self.open_orders[order.order_id] = order
                self.calculate_largest_position_size(order.order_price)
            elif CloseLong.isinstance(order) or CloseShort.isinstance(order):
                open_order = self.open_orders.pop(order.order_id)
                self._pnl(open_order, order)
        except KeyError as e:
            self.logger.error(e)
            exit()

    def _pnl(self, open_order, close_order):
        if CloseLong.isinstance(close_order):
            # pnl = (close_order.order_price - open_order.order_price) * open_order.order_size
            pnl = close_order.order_price * close_order.order_size - open_order.order_price * open_order.order_size
            # if self.order_book.fee_included:
            #     pnl -= open_order.order_price * open_order.order_size * self.order_book.fee_percent
            #     pnl -= close_order.order_price * open_order.order_size * self.order_book.fee_percent
            self.pnl.append((pnl,open_order.order_time,close_order.order_time,open_order.order_type))
            self.price_dict[open_order.order_time] = open_order.order_price
            self.price_dict[close_order.order_time] = close_order.order_price
            self.longs.append((open_order.order_time,close_order.order_time))
        elif CloseShort.isinstance(close_order):
            # pnl = (open_order.order_price - close_order.order_price) * open_order.order_size
            pnl = open_order.order_price * open_order.order_size - close_order.order_price * open_order.order_size
            # if self.order_book.fee_included:
            #     pnl -= open_order.order_price * open_order.order_size * self.order_book.fee_percent
            #     pnl -= close_order.order_price * open_order.order_size * self.order_book.fee_percent
            self.pnl.append((pnl,open_order.order_time,close_order.order_time,open_order.order_type))
            self.price_dict[open_order.order_time] = open_order.order_price
            self.price_dict[close_order.order_time] = close_order.order_price
            self.shorts.append((open_order.order_time,close_order.order_time))

    def post_process(self):
        self.calculate_all()

        self._core = self.calculate_final_results()

        
    def calculate_performance_grade(self, win_rate, profit_factor, average_pnl_norm, rrr, roi):
        # Define default settings
        default_win_rate = 0.5
        default_profit_factor = 2
        default_average_pnl = 10
        default_rrr = 2
        default_roi = 50

        # Assign weights to each metric
        weights = {
            'win_rate': 0.2,
            'profit_factor': 0.3,
            'rrr': 0.1,
            'roi': 0.2,
            'average_pnl': 0.2,
        }
        # Calculate scores for each metric
        if win_rate > default_win_rate*1.5: # 0.75
            win_rate_score = 100
        elif win_rate < default_win_rate*0.5: # 0.25
            win_rate_score = 0
        else:
            win_rate_score = abs(win_rate - default_win_rate*0.5) * 100 / default_win_rate

        if profit_factor == -1:
            profit_factor_score = 100
        elif profit_factor > default_profit_factor*1.5:
            profit_factor_score = 100
        elif profit_factor < default_profit_factor*0.5:
            profit_factor_score = 0
        else:
            profit_factor_score = abs(profit_factor - default_profit_factor*0.5) * 100 / default_profit_factor

        if average_pnl_norm > default_average_pnl*1.5:
            average_pnl_score = 100
        elif (average_pnl_norm < default_average_pnl*0.3):
            average_pnl_score = 0
        else:
            average_pnl_score = abs(average_pnl_norm - default_average_pnl*0.3) * 100 / default_average_pnl*1.2

        if rrr > default_rrr*1.5:
            rrr_score = 100
        elif rrr < default_rrr*0.5:
            rrr_score = 0
        else:
            rrr_score = abs(rrr - default_rrr*0.5) * 100 / default_rrr

        if roi > default_roi*1.5:
            roi_score = 100
        elif roi < 0:
            roi_score = 0
        else:
            roi_score = roi * 100 / default_roi*1.5

        # Calculate weighted average score
        weighted_scores = {
            'win_rate': win_rate_score * weights['win_rate'],
            'profit_factor': profit_factor_score * weights['profit_factor'],
            'average_pnl': average_pnl_score * weights['average_pnl'],
            'rrr': rrr_score * weights['rrr'],
            'roi': roi_score * weights['roi']
        }

        performance_grade = sum(weighted_scores.values())

        # Determine performance grade based on the total score
        if performance_grade > 100:
            performance_grade = 100
        elif performance_grade < 0:
            performance_grade = 0
            
        return performance_grade
    
    def init_dict(self):
        result_dict = {
            'Pair': self.order_book.pair,
            'Fee Included': self.order_book.fee_included,
            'Fee Percent': self.order_book.fee_percent,
            'Stop Loss': self.order_book.stop_loss,
            'ROI%': 0,
            'Win Rate': 0,
            'Profit Factor': 0,
            'Average PnL': 0,
            'RRR': 0,
            'Performance': 0,
            'Max. DD': 0,
            'Max. DD Duration': 0,
            'Total Trades': 0,
            'Winning Trades': 0,
            'Losing Trades': 0,
            'Total Win': 0,
            'Total Loss': 0,
            'Total Fee Paid': -1*self.order_book.paid_fee,
            'Final Balance': self.order_book.balance,
            'Average Fee Paid': self.order_book.paid_fee / len(self.pnl)*2 if len(self.pnl)*2 > 0 else 0,
            'Average Win': 0,
            'Average Loss': 0,
            'Average Trade': 0,
            'Average Position Size': 0,
            'Best Win': 0,
            'Worst Loss': 0,
            'Max. USD in Position': 0,
            'Max. Consec. Wins': 0,
            'Max. Consec. Losses': 0,
            'Max. Unreal. Loss': 0,
            'Max. Loss Perctg.': 0,
            'Theoric Leverage': 0,
            'Sugg. Leverage': 0,
            'Sugg. Stop Loss': 0,
            '# of SL Triggered': self.order_book.sl_triggered_order_count,
            'SL/Total Trades(%)': 0,
            'Long PF': 0,
            'Long Win Rate': 0,
            'Long SL/Total Trades(%)': 0,
            'Short PF': 0,
            'Short Win Rate': 0,
            'Short SL/Total Trades(%)': 0,
        }
        return result_dict

    def calculate_final_results(self):
        result_dict = self.init_dict()
        try:
            result_dict['Win Rate'] = self.win_rate[-1][0]
            result_dict['Profit Factor'] = self.profit_factor[-1][0]
            result_dict['RRR'] = self.rrr[-1][0]

            # NUMERICS
            # 1. Calculate max drawdown
            result_dict['Max. DD'] = min(self.drawdown)[0] 

            # 2. Calculate max drawdown duration
            max_drawdown_duration = 0
            for drawdown in self.drawdown:
                if drawdown[0] == result_dict['Max. DD']:
                    # drawdown[2] is the timestamp of the end of the drawdown as string
                    # drawdown[1] is the timestamp of the start of the drawdown as string
                    close = int(drawdown[2])
                    open = int(drawdown[1])
                    max_drawdown_duration = close - open # as seconds
                    # convert timestamp difference to minutes
                    max_drawdown_duration = max_drawdown_duration / 60 # minutes
                    break
            result_dict['Max. DD Duration'] = max_drawdown_duration

            # Total number of trades
            result_dict['Total Trades'] = len(self.pnl)

            # Total number of winning trades
            result_dict['Winning Trades'] = len([pnl for pnl in self.pnl if pnl[0] > 0])
            result_dict['Losing Trades'] = len([pnl for pnl in self.pnl if pnl[0] < 0])

            # Total win amount 
            result_dict['Total Win'] = sum([pnl[0] for pnl in self.pnl if pnl[0] > 0])

            # Total loss amount
            result_dict['Total Loss'] = sum([pnl[0] for pnl in self.pnl if pnl[0] < 0])

            # Average win amount
            result_dict['Average Win'] = result_dict['Total Win'] / result_dict['Winning Trades'] if result_dict['Winning Trades'] > 0 else 0

            # Average loss amount
            result_dict['Average Loss'] = result_dict['Total Loss'] / result_dict['Losing Trades'] if result_dict['Losing Trades'] > 0 else 0

            # Average trade amount
            result_dict['Average Trade'] = (result_dict['Total Win'] + result_dict['Total Loss']) / result_dict['Total Trades'] if result_dict['Total Trades'] > 0 else 0

            # Average position size
            result_dict['Average Position Size'] = self.total_position_size / self.position_count if self.position_count > 0 else 0

            # Average PnL
            result_dict['Average PnL'] = self.average_pnl[-1][0] / result_dict['Average Position Size'] if result_dict['Average Position Size'] != 0 else 0

            # Best win
            result_dict['Best Win'] = max([pnl[0] for pnl in self.pnl])

            # Worst loss
            result_dict['Worst Loss'] = min([pnl[0] for pnl in self.pnl])

            # Max money spent
            result_dict['Max. USD in Position'] = self.largest_open_position_size_usd

            # Max Consecutive Wins
            result_dict['Max. Consec. Wins'] = max([len(list(group)) for key, group in groupby(self.pnl, lambda x: x[0] > 0) if key]) if len(list(filter(lambda x: x[0]>0,self.pnl))) != 0 else 0

            # Max Consecutive Losses
            result_dict['Max. Consec. Losses'] = max([len(list(group)) for key, group in groupby(self.pnl, lambda x: x[0] < 0) if key]) if len(list(filter(lambda x: x[0]<0,self.pnl))) != 0 else 0

            # Max Unreal. Loss
            result_dict['Max. Unreal. Loss'] = self.maximum_unrealized_loss

            # Max Loss Perctg.
            result_dict['Max. Loss Perctg.'] = min(100,(result_dict['RRR']/(1+result_dict['RRR'])) * 100) 

            # Theoric Leverage
            result_dict['Theoric Leverage'] = int(abs(result_dict['Max. USD in Position']) / abs(result_dict['Max. Unreal. Loss'])) if result_dict['Max. Unreal. Loss'] != 0 else 0

            # Sugg. Leverage
            result_dict['Sugg. Leverage'] = min(result_dict['Theoric Leverage'], 125,
                                                    int(result_dict['Max. USD in Position'] * (result_dict['Max. Loss Perctg.']/100) / abs(result_dict['Max. Unreal. Loss']))) if result_dict['Max. Unreal. Loss'] != 0 else 0

            # Calculate the suggested stop-loss
            result_dict['Sugg. Stop Loss'] = (abs(result_dict['Max. Unreal. Loss']) * (1 + result_dict['Max. Loss Perctg.']/100))*100/result_dict['Max. USD in Position'] if result_dict['Max. USD in Position'] != 0 else 0

            # Calculate the ratio of the stop loss triggered trades
            result_dict['SL/Total Trades(%)'] = result_dict['# of SL Triggered'] * 100 / result_dict['Total Trades'] if result_dict['Total Trades'] != 0 else 0 

            result_dict['ROI%'] = (result_dict['Total Win']+result_dict['Total Loss'])*100/result_dict['Max. USD in Position']

            # 'Long PF': 0,
            # 'Long Win Rate': 0,
            # 'Long SL/Total Trades(%)': 0,
            # 'Short Win Rate': 0,
            # 'Short PF': 0,
            # 'Short SL/Total Trades(%)': 0,
            result_dict['Long PF'] = self.profits_long / abs(self.losses_long) if self.losses_long != 0 else float('-1')
            result_dict['Long Win Rate'] = self.winning_count_long / (self.winning_count_long + self.losing_count_long) if (self.winning_count_long + self.losing_count_long) != 0 else 0
            result_dict['Long SL/Total Trades(%)'] = self.order_book.sl_triggered_order_count_long * 100 / (self.winning_count_long + self.losing_count_long) if (self.winning_count_long + self.losing_count_long) != 0 else 0
            result_dict['Short Win Rate'] = self.winning_count_short / (self.winning_count_short + self.losing_count_short) if (self.winning_count_short + self.losing_count_short) != 0 else 0
            result_dict['Short PF'] = self.profits_short / abs(self.losses_short) if self.losses_short != 0 else float('-1')
            result_dict['Short SL/Total Trades(%)'] = self.order_book.sl_triggered_order_count_short * 100 / (self.winning_count_short + self.losing_count_short) if (self.winning_count_short + self.losing_count_short) != 0 else 0
            # Win rate, Profit Factor, Average PnL and RRR
            # and assign a score to each of them. 
            # Define what from each metric represents 60/100 and 100/100
            # result_dict['Performance'] = ...
            result_dict['Performance'] = self.calculate_performance_grade(result_dict['Win Rate'], result_dict['Profit Factor'], result_dict['Average PnL'], result_dict['RRR'],result_dict['ROI%'])


        except IndexError as e:
            self.logger.error(f"Possible error in calculating final results. This may be caused if strategy didn't trade during SimTesting. IndexError:{e}")

        return result_dict
    
    def calculate_all(self):
        peak = 0
        for pnl_index in tqdm(range(len(self.pnl)),desc="Calculating metrics"):
            self.calculate_win_rate(pnl_index)
            self.calculate_profit_factor(pnl_index)
            peak = self.calculate_drawdown(pnl_index,peak=peak)
            self.calculate_average_pnl(pnl_index)
            self.calculate_risk_reward_ratio(pnl_index)
        

    def calculate_win_rate(self,pnl_index):
        num_winning_trades = self.winning_count
        total_trades = pnl_index + 1
        try:
            win_rate = num_winning_trades / total_trades
        except ZeroDivisionError:
            win_rate = 0
        self.win_rate.append((win_rate, self.pnl[pnl_index][1], self.pnl[pnl_index][2]))

    def calculate_drawdown(self,pnl_index,peak=0):
        pnl = self.pnl[pnl_index]
        peak = max(peak, pnl[0])
        try:
            drawdown = (pnl[0] - peak) / peak
        except ZeroDivisionError:
            drawdown = 0
        self.drawdown.append((drawdown, pnl[1], pnl[2]))
        return peak

    def calculate_profit_factor(self, pnl_index):
        pnl = self.pnl[pnl_index][0]
        self.profits += pnl if pnl > 0 else 0
        self.winning_count += 1 if pnl > 0 else 0
        self.losing_count += 1 if pnl < 0 else 0
        self.losses += pnl if pnl < 0 else 0
        profit_factor = self.profits / abs(self.losses) if self.losses != 0 else float('-1')
        self.profit_factor.append((profit_factor, self.pnl[pnl_index][1], self.pnl[pnl_index][2]))
        # Calculate long and short specific metrics
        if self.pnl[pnl_index][0] > 0:
            self.winning_count_long += 1 if "LONG" in self.pnl[pnl_index][3] else 0
            self.winning_count_short += 1 if "SHORT" in self.pnl[pnl_index][3] else 0
            self.profits_long += pnl if "LONG" in self.pnl[pnl_index][3] else 0
            self.profits_short += pnl if "SHORT" in self.pnl[pnl_index][3] else 0
        elif self.pnl[pnl_index][0] < 0:
            self.losing_count_long += 1 if "LONG" in self.pnl[pnl_index][3] else 0
            self.losing_count_short += 1 if "SHORT" in self.pnl[pnl_index][3] else 0
            self.losses_long += pnl if "LONG" in self.pnl[pnl_index][3] else 0
            self.losses_short += pnl if "SHORT" in self.pnl[pnl_index][3] else 0


    def calculate_average_pnl(self, pnl_index):
        total_pnl = self.profits + self.losses
        average_pnl = total_pnl / (pnl_index+1)
        self.average_pnl.append((average_pnl, self.pnl[pnl_index][1], self.pnl[pnl_index][2]))
    
    def calculate_risk_reward_ratio(self, pnl_index):
        average_profit = self.profits / (self.winning_count+1) 
        average_loss = -self.losses / (self.losing_count+1) 
        risk_reward_ratio = average_profit / average_loss if average_loss > 0 else float('1')
        self.rrr.append((risk_reward_ratio, self.pnl[pnl_index][1], self.pnl[pnl_index][2]))

    def plot_all(self, save_fig:bool, save_path:str):
        self.logger.info('Saving results to {}'.format(save_path))
        if self.win_rate == [] or self.drawdown == [] or self.profit_factor == [] or self.pnl == [] or self.average_pnl == [] or self.rrr == []:
            self.logger.warning('No results to plot!')
            self.logger.warning('Failed to save!')
            return
        self.plot(self.win_rate, 'Win Rate', 'green',save_fig=save_fig,save_path=save_path)
        self.plot(self.drawdown, 'Drawdown', 'red',save_fig=save_fig,save_path=save_path)
        self.plot(self.profit_factor, 'Profit Factor', 'blue',save_fig=save_fig,save_path=save_path)
        self.plot(self.pnl, 'PnL', 'orange',save_fig=save_fig,save_path=save_path)
        self.plot(self.average_pnl, 'Average PnL', 'purple',save_fig=save_fig,save_path=save_path)
        self.plot(self.rrr, 'Risk Reward Ratio', 'navy',save_fig=save_fig,save_path=save_path)
        self.logger.info('Successfully saved!')

    def plot_position_entry_exit(self, abs_save_path:str):
        from matplotlib.dates import DateFormatter
        from datetime import datetime as dt
        self.logger.info('Saving results to {}'.format(abs_save_path))
        if self.longs == [] or self.shorts == []:
            self.logger.warning('No results to plot!')
            self.logger.warning('Failed to save!')
            return
        
        price = []
        time = []
        for k,v in self.price_dict.items():
            price.append(v)
            time.append(dt.fromtimestamp(int(k)))
        ax1 = plt.figure(figsize=(25, 10)).gca()
        ax1.plot(time, price, c='black', linewidth=2.5, label='Price', alpha=0.75)
        ax1.set_ylabel('Price')
        ax1.set_ylim(min(price) * 0.99, max(price) * 1.01)
        ax1.grid(True)
        for opentime, closetime in self.longs:
            opentime_index = time.index(dt.fromtimestamp(int(opentime)))
            closetime_index = time.index(dt.fromtimestamp(int(closetime)))
            ax1.plot(time[opentime_index], price[opentime_index], '^', markersize=15, label='Open', color='green', alpha=0.75)
            ax1.plot(time[closetime_index], price[closetime_index], 'v', markersize=15, label='Close', color='red', alpha=0.75)
            # annotate the opening and closing
            ax1.plot(time[opentime_index:closetime_index], price[opentime_index:closetime_index], color='green',linewidth=3.5 , alpha=0.5)
        
        for opentime, closetime in self.shorts:
            opentime_index = time.index(dt.fromtimestamp(int(opentime)))
            closetime_index = time.index(dt.fromtimestamp(int(closetime)))
            ax1.plot(time[opentime_index], price[opentime_index], 'v', markersize=15, label='Open', color='red', alpha=0.75)
            ax1.plot(time[closetime_index], price[closetime_index], '^', markersize=15, label='Close', color='green', alpha=0.75)
            # annotate the opening and closing
            ax1.plot(time[opentime_index:closetime_index], price[opentime_index:closetime_index], color='red',linewidth=3.5 , alpha=0.5)

        strategy_name = abs_save_path.split('results/')[-1].split('/')[0]
        plt.title(f'{strategy_name} | Position Entry & Exit by Time')

        # Adjust the x-axis ticks
        ax1.xaxis.set_major_locator(plt.MaxNLocator(10))
        ax1.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d %H:%M:%S'))
        plt.xticks(rotation=45)
        plt.tight_layout()
        # save figures to the save_path
        dest = os.path.join(abs_save_path, 'position_entry_exit.png')
        plt.savefig(dest)
        self.logger.info('Successfully saved!')

        plt.close()


    def plot(self, results:list, title:str, color:str, save_fig:bool=False, save_path:str=None):
        from matplotlib.dates import DateFormatter
        from datetime import datetime as dt
        plt.figure(figsize=(25, 10))

        # self.longs and self.short is defined and 
        # I have prices and times list. I want to 
        # plot every position (long and short) on 
        # the prices vs times plot by marks. Position 
        # openings are marked as ^ up arrow and position 
        # closings are marked v down arrow. Long position 
        # openings and closings are green; whereas, short ones are plotted red.
         
        price = []
        time = []
        for k,v in self.price_dict.items():
            price.append(v)
            time.append(dt.fromtimestamp(int(k)))
        x = [dt.fromtimestamp(int(result[2])) for result in results]  # Close times
        y = [result[0] for result in results]  # Values
        # plot prices on the same plot with different vertical axis
        ax1 = plt.gca()
        ax2 = ax1.twinx()
        ax3 = ax2.twiny()
        ax1.plot(time, price, c='black', linewidth=2.5, label='Price', alpha=0.75)
        ax1.set_ylabel('Price')
        ax1.set_ylim(min(price) * 0.99, max(price) * 1.01)
        ax1.grid(True)
        ax3.plot(x, y, c=color, linewidth=3.0, label=title, alpha=0.5)
        ax3.set_ylabel(title)
        if title == 'Profit Factor':
            ax3.set_ylim(min(y) * 0.99, 10)
        else:
            ax3.set_ylim(min(y) * 0.99, max(y) * 1.01)
            
        ax3.grid(True)
        plt.title(title)

        # Plotting the opening and closing nodes for each tuple
        for opentime, closetime in self.longs:
            opentime_index = time.index(dt.fromtimestamp(int(opentime)))
            closetime_index = time.index(dt.fromtimestamp(int(closetime)))
            ax1.plot(time[opentime_index], price[opentime_index], '^', markersize=15, label='Open', color='green', alpha=0.75)
            ax1.plot(time[closetime_index], price[closetime_index], 'v', markersize=15, label='Close', color='red', alpha=0.75)
            # annotate the opening and closing
            ax1.plot(time[opentime_index:closetime_index], price[opentime_index:closetime_index], color='green',linewidth=3.5 , alpha=0.5)

        for opentime, closetime in self.shorts:
            opentime_index = time.index(dt.fromtimestamp(int(opentime)))
            closetime_index = time.index(dt.fromtimestamp(int(closetime)))
            ax1.plot(time[opentime_index], price[opentime_index], 'v', markersize=15, label='Open', color='red', alpha=0.75)
            ax1.plot(time[closetime_index], price[closetime_index], '^', markersize=15, label='Close', color='green', alpha=0.75)
            # annotate the opening and closing
            ax1.plot(time[opentime_index:closetime_index], price[opentime_index:closetime_index], color='red',linewidth=3.5 , alpha=0.5)
            
        # Adjust the x-axis ticks
        ax1.xaxis.set_major_locator(plt.MaxNLocator(10))
        ax1.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d %H:%M:%S'))  # Customize date format
        ax3.xaxis.set_major_locator(plt.MaxNLocator(10))
        ax3.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d %H:%M:%S'))  # Customize date format

        plt.xticks(rotation=45)
        plt.tight_layout()
        # save figures to the save_path
        if save_fig:
            dest = os.path.join(save_path, title + '.png')
            plt.savefig(dest)
        plt.close()
        return x,y
    
    def plot_bar_pnl(self, abs_save_path):
        barpath = os.path.join(abs_save_path, 'pnl.csv')
        data = pd.read_csv(barpath)

        # data['profit'] is the positive pnl
        # data['loss'] is the negative pnl
        data['profit'] = data['data'].apply(lambda x: x if x > 0 else 0)
        data['loss'] = data['data'].apply(lambda x: x if x < 0 else 0)
        # Convert timestamp into datetime
        data['date_day'] = data['timestamp'].apply(lambda x: datetime.fromtimestamp(x).strftime('%Y-%m-%d'))
        data['date_week'] = data['timestamp'].apply(lambda x: datetime.fromtimestamp(x).strftime('%Y-%W'))
        data['date_month'] = data['timestamp'].apply(lambda x: datetime.fromtimestamp(x).strftime('%Y-%m'))
        data['date_year'] = data['timestamp'].apply(lambda x: datetime.fromtimestamp(x).strftime('%Y'))

        strategy_name = abs_save_path.split('results/')[-1].split('/')[0]
        timeframes = ['date_day', 'date_week', 'date_month', 'date_year']

        bar_save_path = os.path.join(abs_save_path, 'bar_plots')

        if not os.path.exists(bar_save_path):
            os.makedirs(bar_save_path)

        # To suppress categories warning
        plt.set_loglevel('WARNING')
        # Group by timeframe
        self.logger.info('Plotting bar plots for PnL and Profit Factor. This may take a while...')
        for timeframe in timeframes:
            data_new = data.groupby(timeframe).sum(numeric_only=True).reset_index()
            # PnL
            fig = plt.figure(figsize=(25, 10))
            # Plot the bars
            plt.xlabel(timeframe.split("_")[1].capitalize())
            plt.ylabel('PnL')
            plt.xticks(rotation=45)
            plt.title(f'{strategy_name} | PnL by {timeframe.split("_")[1].capitalize()}', y=1.08, fontsize=self.font_size)
            plt.grid(True)

            profit_bar = plt.bar(data_new[timeframe], data_new['profit'], color='forestgreen', label='Profit')
            loss_bar = plt.bar(data_new[timeframe], data_new['loss'], color='lightcoral', label='Loss')

            # Add counts above the two bar graphs
            for rect in profit_bar + loss_bar:
                height = rect.get_height()
                if height > 0:
                    x = rect.get_x() + rect.get_width()/4
                else:
                    x = rect.get_x() + rect.get_width()*3/4


                    # color = 'white'
                plt.text(x, height, f'{height:.1f}', 
                         ha='center', va='bottom', fontsize=self.font_size)

           
            plt.legend()
            plt.tight_layout()

            # save figures to the save_path
            dest = os.path.join(bar_save_path, f'pnl_{timeframe}.png')
            plt.savefig(dest)
            
            plt.close()
            # Profit factor
            data_new['profit_factor'] = data_new['profit'] / abs(data_new['loss'])

            # Plot the data
            plt.figure(figsize=(25,10))
            # We will colorize the bars based on the profit factor
            colors = []
            # Shouldn't use red or green it represent profit & loss
            for i, v in enumerate(data_new['profit_factor']):
                # if profit factor is above 5, we will annotate the bar with the value
                # if profit factor is inf (division by zero), we will annotate the bar with the no loss and clamp the bar to 5
                if v == float('inf'):
                    plt.text(i, 5.1, 'No Loss', ha='center', fontsize=self.font_size)
                elif v > 5:
                    plt.text(i, 5.1, str(round(v, 2)), ha='center', fontsize=self.font_size)
                else:
                    plt.text(i, v+0.1, str(round(v, 2)), ha='center', fontsize=self.font_size)

            for pf in data_new['profit_factor']:
                if pf == float('inf'):
                    colors.append('gray')
                elif pf > 2:
                    colors.append('orange')
                elif pf < 1:
                    colors.append('black')
                else:
                    colors.append('blue')
            
            data_new['profit_factor'] = data_new['profit_factor'].apply(lambda x: 5 if x == float('inf') else x)

            plt.bar(data_new[timeframe], data_new['profit_factor'], color=colors, label='Profit Factor')
            plt.axhline(y=1, color='black', linestyle='--', label='Break Even')
            plt.legend()
            plt.title(f'{strategy_name} | Profit Factor by {timeframe.split("_")[1].capitalize()}', y=1.08, fontsize=self.font_size)
            plt.xlabel(timeframe.split("_")[1].capitalize())
            plt.ylabel('Profit Factor')
            plt.ylim(0, 5)
            # Add values to the bars

            plt.xticks(rotation=45)
            plt.tight_layout()
            # save figures to the save_path
            dest = os.path.join(bar_save_path, f'profit_factor_{timeframe}.png')
            plt.savefig(dest)
            del data_new
            plt.close()
        self.logger.info('Successfully saved bar plots for PnL and Profit Factor under {}'.format(bar_save_path))

    
    def save_results(self, save_path):
        try:

            if save_path is None:
                self.logger.error("Error in TradingMetrics: save_path is None. Please specify a save_path")
                exit(1)

            if not os.path.exists(save_path):
                os.makedirs(save_path)
            
            abs_save_path = os.path.abspath(save_path)
            self.logger.info(f"Saving results to {abs_save_path}")
            # Save the metrics as csv files
            with open(os.path.join(save_path, 'win_rate.csv'), 'w') as f:
                f.write("data,timestamp\n")
                for item in self.win_rate:
                    f.write(f"{item[0]},{item[2]}\n")
            with open(os.path.join(save_path, 'profit_factor.csv'), 'w') as f:
                f.write("data,timestamp\n")
                for item in self.profit_factor:
                    f.write(f"{item[0]},{item[2]}\n")
            with open(os.path.join(save_path, 'drawdown.csv'), 'w') as f:
                f.write("data,timestamp\n")
                for item in self.drawdown:
                    f.write(f"{item[0]},{item[2]}\n")
            with open(os.path.join(save_path, 'average_pnl.csv'), 'w') as f:
                f.write("data,timestamp\n")
                for item in self.average_pnl:
                    f.write(f"{item[0]},{item[2]}\n")
            with open(os.path.join(save_path, 'rrr.csv'), 'w') as f:
                f.write("data,timestamp\n")
                for item in self.rrr:
                    f.write(f"{item[0]},{item[2]}\n")
            with open(os.path.join(save_path, 'pnl.csv'), 'w') as f:
                f.write("data,timestamp\n")
                for item in self.pnl:
                    f.write(f"{item[0]},{item[2]}\n")
            # Save the price_dict
            with open(os.path.join(save_path, 'price.csv'), 'w') as f:
                f.write("data,timestamp\n")
                for key, value in self.price_dict.items():
                    f.write(f"{value},{key}\n")
            
            # Save the result_dict as json
            with open(os.path.join(save_path, 'result.json'), 'w') as f:
                json.dump(self._core, f)

            
            self.logger.info(f"Results successfully saved to csv files under {abs_save_path}")
            self.plot_bar_pnl(abs_save_path)
        except Exception as e:
            self.logger.error(e)
            self.logger.error("Error in TradingMetrics: Unable to save results to csv files")
