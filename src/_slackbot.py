import slack
from .slack_config import optimization_bot_token

class SlackOptimizationReportBot:
    def __init__(self, strategy_names:list, symbols:list, pdf_path:str,csv_path:str=None, channel_name:str='#optimization') -> None:
        '''
        :param strategy_name (str): name of the strategy to be reported. The parameter will be used when creating file's title.
        :param symbols (list): takes backtested symbols as a list to use them when creating file's title.
        :param file_path (str): path of the file that will be send to the channel
        '''
        self.strategy_names = strategy_names
        self.symbols = symbols
        self.slack_bot_token = optimization_bot_token
        self.channel_name = channel_name
        self.file_path = pdf_path
        self.csv_path = csv_path
        self.client = slack.WebClient(token=self.slack_bot_token)

    def send_optimization_report(self):
        message = f'📊 {", ".join(self.strategy_names)} adlı stratejilerin optimizasyonu tamamlandı. 🙌🏻 Stratejiler {[x for x in self.symbols]} için backtest edildi. 🔥 Optimizasyon sonucunda en iyi performans gösteren backtest sonuçlarından bir hot list oluşturuldu. Oluşturulan hot list ektedir. 🧐'
        title = f'Optimization Report of {[x for x in self.strategy_names]}{[x for x in self.symbols]}'
        self.client.files_upload(channels=self.channel_name, file=self.file_path, filename=self.file_path, initial_comment=message, title=title)
        self.send_csv_file()

    def send_csv_file(self):
        if self.csv_path is not None:
            message = f'📊 {", ".join(self.strategy_names)} adlı stratejilerin bütün optimizasyon sonuçları {[x for x in self.symbols]} için ekte gönderildi. 🔥'
            title = f'Total Results of {[x for x in self.strategy_names]}{[x for x in self.symbols]}'
            self.client.files_upload(channels=self.channel_name, file=self.csv_path, filename=self.csv_path, initial_comment=message, title=title)
    
    def send_error_message(self):
        message = f'{[x for x in self.strategy_names]}{[x for x in self.symbols]} adlı stratejinin optimizasyonu yapılırken hata oluştu.'
        self.client.chat_postMessage(channel=self.channel_name, text=message)



if __name__ == '__main__':
    slack = SlackOptimizationReportBot(strategy_name='Takuri Fibonacci', symbols=['BNB', 'DOGE'], file_path='testler/sonuclar.xlsx')
    slack.send_optimization_report()
