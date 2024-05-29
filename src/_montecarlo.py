from _scenario import Scenario
import numpy as np
import pandas as pd
from tqdm import tqdm
from time import time
import os
from random import randint
from datetime import datetime
import requests
import random


class MonteCarlo:
    def __init__(self) -> None:
        self.min_in_day = 1440
        self.save_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'SimTest', 'data', 'generated')


    def set_params(self, config):
        """
        - sets the parameters for the monte carlo simulation
        """
        self.params = config

    def format_time(self, t):
        datetime.fromtimestamp(int(time()/100)*100), int(time()/100)*100
        init_time = int(time()/100)*100
        date = [ init_time + i*100 for i in t]
        return date

    def get_init_price(self, pair="BTCUSDT") -> any:
        """
        - returns the initial price of the scenario
        """
        bybit_key = lambda x: f"http://api-testnet.bybit.com/v5/market/tickers?category=inverse&symbol={x}"
        data = requests.get(bybit_key(pair))
        data = data.json()
        price = data["result"]["list"][0]["indexPrice"]
        return float(price)
    
    def generate_k(self) -> list:
        path_list = []
        # generate long scenarios
        for i in tqdm(range(self.params['long_sim_count']), desc='Generating long scenarios'):
            day = randint(self.params['min_day'], self.params['max_day'])
            strength = randint(1, 10)
            ts = day*self.min_in_day            
            df = self.generate_long(timestep=ts, strength=strength)
            path = os.path.join(self.save_path, 'long',f'long_{i}.csv')
            if not os.path.exists(os.path.join(self.save_path, 'long')):
                os.makedirs(os.path.join(self.save_path, 'long'))
            df.to_csv(path, index=False, header=False)
            path_list.append(('long', path))

        # generate short scenarios
        for i in tqdm(range(self.params['short_sim_count']), desc='Generating short scenarios'):
            day = randint(self.params['min_day'], self.params['max_day'])
            strength = randint(1, 10)
            ts = day*self.min_in_day            
            df = self.generate_short(timestep=ts, strength=strength)
            path = os.path.join(self.save_path, 'short',f'short_{i}.csv')
            if not os.path.exists(os.path.join(self.save_path, 'short')):
                os.makedirs(os.path.join(self.save_path, 'short'))
            df.to_csv(path, index=False, header=False)
            path_list.append(('short', path))

        # generate random scenarios
        for i in tqdm(range(self.params['random_sim_count']), desc='Generating idle scenarios'):
            day = randint(self.params['min_day'], self.params['max_day'])
            strength = randint(1, 10)
            ts = day*self.min_in_day            
            df = self.generate_random(timestep=ts, strength=strength, num_of_days=day)
            path = os.path.join(self.save_path, 'random',f'random_{i}.csv')
            if not os.path.exists(os.path.join(self.save_path, 'random')):
                os.makedirs(os.path.join(self.save_path, 'random'))
            df.to_csv(path, index=False, header=False)
            path_list.append(('random', path))

        return path_list

    def generate_long(self,timestep:int, strength: int) -> pd.DataFrame:
        """
        - generates a long scenario based on the given timestep and volatility

        Args:
            timestep (int): Timestep of the scenario
            volatility (int): A range from 1 to 10, 1 being the least volatile and 10 being the most volatile
            strength (int): A range from 1 to 10, 1 being the weakest and 10 being the strongest
        """
        t = np.array(list(range(1, timestep + 1, 1)))
        xt = np.zeros(timestep)
        for i in range(1, timestep + 1):
            xt[i - 1] =  0.8 * xt[i - 2] + np.random.normal(-1, np.sqrt(100))

        et = np.zeros(timestep)
        for i in range(1, timestep + 1):
            et[i - 1] = 1 * et[i - 2] + np.random.normal(2, np.sqrt(1000))

        yt = np.zeros(timestep)
        yt = self.get_init_price() + np.exp(0.06 * xt) + et + xt

        date = self.format_time(t)
        df = pd.DataFrame({"date": date, "close": yt})

        return df

    def generate_short(self, timestep:int, strength: int) -> pd.DataFrame:
        """
        - generates a short scenario based on the given timestep and volatility

        Args:
            timestep (int): _description_
            volatility (int): _description_
        """
        t = np.array(list(range(1, timestep + 1, 1)))
        xt = np.zeros(timestep)
        for i in range(1, timestep + 1):
            xt[i - 1] =  0.8 * xt[i - 2] + np.random.normal(0, np.sqrt(1000))

        et = np.zeros(timestep)
        for i in range(1, timestep + 1):
            et[i - 1] = 1 * et[i - 2] + np.random.normal(-2, np.sqrt(1000))

        dt = np.zeros(timestep)
        dt = self.get_init_price() - np.exp(0.00001 * (-xt)) + et - xt

        date = self.format_time(t)
        df = pd.DataFrame({"date": date, "close": dt})

        return df

    def generate_idle(self, timestep:int, volatility: int) -> pd.DataFrame:
        """
        - generates a idle scenario based on the given timestep and volatility

        Args:
            timestep (int): _description_
            volatility (int): _description_
        """
        pass

    def generate_random(self, timestep:int, strength: int, num_of_days: int) -> pd.DataFrame:
        """ 
        - generates a random scenario based on the given timestep and volatility

        Args:
            timestep (int): _description_
            volatility (int): _description_
            num_of_days (int): Number of days to specify the length of the random trend
        """
        timestep = num_of_days * 1440
        concatenated_array = np.empty(shape=(1))
        last_choice = "sideways"    # to avoid starting with a sideways trend
        sideways_counter = 0
        first_price = self.get_init_price()
        total_day = 0

        while total_day < 30:
            choice = ""
            if last_choice != "sideways" and sideways_counter < 3:
                choice = random.choice(["uptrend", "downtrend", "sideways"])
            else:
                choice = random.choice(["uptrend", "downtrend"])

            last_choice = choice
            
            if choice == "sideways":
                trend_day = 1
                sideways_counter += 1
            else:
                trend_day = randint(1,5)
            total_day += trend_day

            if total_day > 30:
                surplus = total_day - 30
                trend_day -= surplus
                total_day -= surplus

            if choice == "uptrend":
                exp_t = np.array(list(range(1, timestep + 1, 1)))
                exp_xt = np.zeros(timestep)
                for i in range(1, timestep + 1):
                    exp_xt[i - 1] =  0.8 * exp_xt[i - 2] + np.random.normal(0, np.sqrt(1000))
                exp_et = np.zeros(timestep)
                for i in range(1, timestep + 1):
                    exp_et[i - 1] = 1 * exp_et[i - 2] + np.random.normal(0, np.sqrt(100))
                random_trend_array = np.zeros(timestep)
                random_trend_array = first_price + np.exp(0.01 * exp_xt) + exp_et

            elif choice == "downtrend":
                exp_t = np.array(list(range(1, timestep + 1, 1)))
                exp_xt = np.zeros(timestep)
                for i in range(1, timestep + 1):
                    exp_xt[i - 1] =  0.8 * exp_xt[i - 2] + np.random.normal(0, np.sqrt(1000))
                exp_et = np.zeros(timestep)
                for i in range(1, timestep + 1):
                    exp_et[i - 1] = 1 * exp_et[i - 2] + np.random.normal(0, np.sqrt(100))
                random_trend_array = np.zeros(timestep)
                random_trend_array = first_price - np.exp(0.01 * (-exp_xt)) + exp_et

            elif choice == "sideways":
                t = np.array(list(range(1, timestep + 1, 1)))
                xt = np.zeros(timestep)
                for i in range(1, timestep + 1):
                    xt[i - 1] = 0.8 * xt[i - 2] + np.random.normal(0, np.sqrt(100))

                et = np.zeros(timestep)
                for i in range(1, timestep + 1):
                    et[i - 1] = 0.8 * et[i - 2] + np.random.normal(0, np.sqrt(1))

                random_trend_array = np.zeros(timestep)
                random_trend_array = first_price - 0.01 * t + et + xt / 4

            first_price = random_trend_array[-1]
            concatenated_array = np.concatenate([concatenated_array, random_trend_array])

            t = range(concatenated_array.shape[0])
            date = self.format_time(t)
            
            df = pd.DataFrame({"date": date, "close": concatenated_array})
            df.drop(index=0, inplace=True)
            
            return df

    def generate_scenario(self, scenario: Scenario) -> pd.DataFrame:
        """
        - generates dataset of a scenario based on the given scenario object
        
        Args:
            scenario (Scenario): _description_
            """
        pass