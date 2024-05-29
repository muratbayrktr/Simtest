import requests
import pandas as pd
import json
from datetime import datetime as dt
import os

class BybitFutures:
    def __init__(self, start_date:str, final_date:str, interval:str, symbol:str) -> None:
        self.url = f'https://api.bybit.com//derivatives/v3/public/kline'
        self.category = 'linear'
        self.symbol = symbol
        self.concat_path = None

        interval_mapping = {
            '1m': '1',
            '3m': '3',
            '5m': '5',
            '15m': '15',
            '30m': '30',
            '1h': '60',
            '2h': '120',
            '4h': '240',
            '6h': '360',
            '12h': '720',
            # @TODO: Fill the rest of the mapping
        }
        self.interval = interval_mapping[str(interval.lower())]
        self.fixed_interval = None

        self.start_date = start_date
        self.start_unix = str(int(dt(int(self.start_date.split('-')[0]), int(self.start_date.split('-')[1]), int(self.start_date.split('-')[2])).timestamp()) * 1000)
        self.final_date = final_date
        self.final_unix = str(int(dt(int(self.final_date.split('-')[0]), int(self.final_date.split('-')[1]), int(self.final_date.split('-')[2])).timestamp()) * 1000)

        try:
            self.fixed_interval = str(int(self.interval)) + 'm'
            if self.fixed_interval == '60m':
                self.fixed_interval = '1h'
        except:
            self.fixed_interval = self.interval

        self.request_params = {'category':self.category, 'symbol':self.symbol, 'interval':self.interval, 'start':self.start_unix, 'end':self.final_unix}
        self.df = None
        self.date_range = pd.date_range(self.start_date, self.final_date)
        self.date_range = list(map(lambda x: str(x).split(' ')[0], self.date_range))
        
        self.final_date = self.date_range[-1]

        # generate paths
        self.bybit_raw_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 'SimTest', 'data',  self.__class__.__name__,'raw', f'{self.symbol}', f'{self.fixed_interval}')
        if not os.path.exists(self.bybit_raw_path):
            os.makedirs(self.bybit_raw_path)

        self.bybit_processed_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 'SimTest', 'data', self.__class__.__name__, 'processed', f'{self.symbol}', f'{self.fixed_interval}')
        if not os.path.exists(self.bybit_processed_path):
            os.makedirs(self.bybit_processed_path)

        self.bybit_raw_cache = os.listdir(self.bybit_raw_path)
        self.bybit_processed_cache = os.listdir(self.bybit_processed_path)

        # pipeline
        if not self.check_processed_cache():
            self.fetch_each_days_ohlcv_separately()
            self.concat_path = self.concat_csv_files()

    def get_columns(self):
            return ['structured_date','date', 'open', 'high', 'low', 'close', 'volume', 'turnover']

    def get_path(self):
        if self.concat_path == None:
            raise Exception("DataCollector has not been initialized yet.")
        return self.concat_path

    
    def check_processed_cache(self):
        """
        - checks if the interval is cached
        - returns True if cached, False if not
        """
        for csv_file in self.bybit_processed_cache:
            if(self.start_date in csv_file and self.final_date in csv_file):
                self.concat_path = os.path.join(self.bybit_processed_path, csv_file)
                return True
        return False
    

    def check_raw_cache(self, date):
        """
        - checks if the interval is cached
        - returns True if cached, False if not
        """

        for csv_file in self.bybit_raw_cache:
            if(date in csv_file):
                return True
        return False
    

    def fetch_each_days_ohlcv_separately(self):
        current_path = os.getcwd()
        os.chdir(self.bybit_raw_path)
        for i in range(len(self.date_range)):
            try:
                start = self.date_range[i]
                end = self.date_range[i + 1]

                # If the file is already in the cache, it will not be downloaded again
                if self.check_raw_cache(date=start):
                    continue

                start_unix = str(int(dt(int(start.split('-')[0]), int(start.split('-')[1]), int(start.split('-')[2])).timestamp()) * 1000)
                final_unix = str(int(dt(int(end.split('-')[0]), int(end.split('-')[1]), int(end.split('-')[2])).timestamp()) * 1000)
                self.request_params['start'] = start_unix
                self.request_params['end'] = final_unix

                df_ohlcv = pd.DataFrame(json.loads(requests.get(self.url, self.request_params).text)['result']['list'], columns=['open_time', 'open', 'high', 'low', 'close', 'volume', 'turnover'])
                df_ohlcv.sort_values(by='open_time', ascending=True, ignore_index=True, inplace=True)
                last_timestamp = str(df_ohlcv['open_time'][len(df_ohlcv) - 1])

                while int(last_timestamp) < int(final_unix):
                    self.request_params['start'] = str(last_timestamp)
                    df2 = pd.DataFrame(json.loads(requests.get(self.url, params=self.request_params).text)['result']['list'], columns=['open_time', 'open', 'high', 'low', 'close', 'volume', 'turnover'])
                    df2.sort_values(by='open_time', ascending=True, ignore_index=True, inplace=True)
                    df2 = df2.iloc[1:, :]

                    df_ohlcv = pd.concat([df_ohlcv, df2], axis=0, ignore_index=True)
                    
                    try:
                        last_timestamp = str(df_ohlcv['open_time'][len(df_ohlcv) - 1])
                    except:
                        break
                df_ohlcv = df_ohlcv.iloc[:-1, :]

                # add dates to df
                dates = list(df_ohlcv['open_time'])
                dates = pd.DataFrame({"date":[dt.fromtimestamp(int(x) / 1000).strftime('%Y-%m-%d %H:%M:%S') for x in dates]})
                df_ohlcv = pd.concat([dates, df_ohlcv], axis=1)

                # @TODO: her günü ayrı ayrı raw_path'e kaydet
                date = f'{start.split("-")[0]}-{start.split("-")[1].zfill(2)}-{start.split("-")[2].zfill(2)}'
                save_path = os.path.join(self.bybit_raw_path, f'{self.symbol}-{self.fixed_interval}-{date}.csv')
                df_ohlcv.to_csv(save_path, index=False)
            except Exception as e:
                print(e)
        os.chdir(current_path)
    
    def concat_csv_files(self):
        """ 
        - combine csv files between start date and final date using csv files in the data/raw
        - saves combined csv file to the data/processed
        - returns combined csv
        """
        concat = pd.DataFrame()
        # read all the csv files in the self.date_range and concate them
        self.date_range.pop()
        for date in self.date_range:
            print(self.symbol)
            filename = f"{self.symbol}-{self.fixed_interval}-{date}.csv"
            file_read_path = os.path.join(self.bybit_raw_path, filename)
            df = pd.read_csv(file_read_path)
            # concat the df to concat
            concat = pd.concat([concat, df], ignore_index=True)
        # save the concat df to the data/processed
        start_date = f'{self.start_date.split("-")[0]}-{self.start_date.split("-")[1].zfill(2)}-{self.start_date.split("-")[2].zfill(2)}'
        final_date = f'{self.final_date.split("-")[0]}-{self.final_date.split("-")[1].zfill(2)}-{self.final_date.split("-")[2].zfill(2)}'
        concat_file_name = f"{self.symbol}-{self.fixed_interval}-{start_date}-to-{final_date}.csv"
        file_write_path = os.path.join(self.bybit_processed_path, concat_file_name)
        concat.to_csv(file_write_path, index=False, columns=['date', 'open_time', 'open', 'high', 'low', 'close', 'volume', 'turnover'])
        return file_write_path

