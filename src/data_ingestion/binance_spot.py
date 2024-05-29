import wget
import zipfile
import os
import pandas as pd

class BinanceSpot:
    def __init__(self, start_date, final_date, interval : str, pair:str):
        self.interval_list = ["12h", "15m", "1d", "1h", "1m", "2h", "30m", "3m", "4h", "5m", "6h", "8h"]
        self.start_date = start_date
        self.final_date = final_date
        self.pair = pair
        self.interval = interval.lower()

        self.date_range = pd.date_range(start_date, final_date)
        self.date_range = list(map(lambda x: str(x).split(" ")[0],self.date_range))
        self.concat_path = None

        # generate paths
        self.raw_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 'SimTest', 'data',  self.__class__.__name__,'raw', f'{self.pair}')
        self.processed_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 'SimTest', 'data',  self.__class__.__name__, 'processed', f'{self.pair}')
        self.raw_path = os.path.join(self.raw_path, self.interval)
        self.processed_path = os.path.join(self.processed_path, self.interval)

        # check if folder exists in raw path
        if not os.path.exists(self.raw_path):
            # if not, create it
            os.makedirs(self.raw_path)
        # check if folder exists in processed path
        if not os.path.exists(self.processed_path):
            # if not, create it
            os.makedirs(self.processed_path)

        self.raw_cache = os.listdir(self.raw_path)
        self.processed_cache = os.listdir(self.processed_path)
        # pipeline
        if not self.check_processed_cache():
            self.zip_urls = self.create_zip_urls()
            self.download_and_unzip(self.zip_urls)
            self.concat_path = self.concat_csv_files()

    def get_columns(self):
        return ['date','open','high','low','close','volume','close time','quote asset volume','number of trades','taker buy base asset volume','taker buy quote asset volume','ignore']

    def get_path(self):
        if self.concat_path == None:
            raise Exception("DataCollector has not been initialized yet.")
        return self.concat_path


    def check_processed_cache(self):
        """
        - checks if the interval is cached
        - returns True if cached, False if not
        """
        for csv_file in self.processed_cache:
            if(self.start_date in csv_file and self.final_date in csv_file):
                self.concat_path = os.path.join(self.processed_path, csv_file)
                return True
        return False
    
    def check_raw_cache(self, date):
        """
        - checks if the interval is cached
        - returns True if cached, False if not
        """

        for csv_file in self.raw_cache:
            if(date in csv_file):
                return True
        return False
        
    def create_zip_urls(self):
        """ 
        - creates zip file urls using start and final date
        - returns zip file names as list
        """
        zip_url_list = []
        for date in self.date_range:
            if(self.check_raw_cache(date)):
                continue
            zip_url = f"https://data.binance.vision/data/spot/daily/klines/{self.pair}/{self.interval}/{self.pair}-{self.interval}-{date}.zip"
            zip_url_list.append(zip_url)
        return zip_url_list
    
    def download_and_unzip(self, zip_url_list):
        """ 
        - if csv file doesn't exists in the data/raw file:
            - download the zip file
            - unzip the file
            - delete the zip file
        """
        current_path = os.getcwd()
        os.chdir(self.raw_path)
        for zip_url in zip_url_list:
            zip_file = zip_url.split("/")[-1]
            try:
                wget.download(zip_url, zip_file)
                with zipfile.ZipFile(zip_file) as zfile:
                    zfile.extractall()
                os.remove(zip_file)
            except Exception as e:
                print(e)
                exit()
        os.chdir(current_path)
        

    def concat_csv_files(self):
        """ 
        - combine csv files between start date and final date using csv files in the data/raw
        - saves combined csv file to the data/processed
        - returns combined csv
        """
        concat = pd.DataFrame()
        # read all the csv files in the self.date_range and concate them
        for date in self.date_range:
            filename = f"{self.pair}-{self.interval}-{date}.csv"
            file_read_path = os.path.join(self.raw_path, filename)
            df = pd.read_csv(file_read_path, comment="o", header=None)
            # concat the df to concat
            concat = pd.concat([concat, df], ignore_index=True)
        # save the concat df to the data/processed
        concat_file_name = f"{self.pair}-{self.interval}-{self.start_date}-to-{self.final_date}.csv"
        file_write_path = os.path.join(self.processed_path, concat_file_name)
        concat.to_csv(file_write_path, index=False, header=False)
        return file_write_path
