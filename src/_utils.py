from _base_strategy import BaseStrategy
from _metrics import TradingMetrics
from _montecarlo import MonteCarlo
from _backtester import Backtester
from _simulator import Simulator
from _orders import OrderBook
from matplotlib import pyplot as plt
from strategy import *
from time import sleep


import logging
import threading
import datetime
import os
import yaml
import json

# Set this file logger name to IPC
logger = logging.getLogger('IPC')

def backtest(strategy: any, base_path: str) -> OrderBook:
    """Backtest a strategy.

    Args:
        strategy (any): strategy to backtest

    Returns:
        OrderBook: order book
    """
    interval, start, final, pair = select_dates()
    M, order_book = _backtest(strategy, base_path, (interval, start, final, pair), verbose=True)
    return order_book

def backtest_benchmark(strategy: any, base_path: str) -> OrderBook:
    """Backtest a strategy.

    Args:
        strategy (any): strategy to backtest

    Returns:
        OrderBook: order book
    """
    benchmark, pair = get_benchmark()
    ob = []
    mlist = []
    for interval, start, final in benchmark:
        M, order_book = _backtest(strategy, base_path, (interval, start, final, pair), verbose=True)
        ob.append(order_book)
        try:
            mlist.append(M["Performance"])
        except:
            mlist.append(0)
    # return mean of the metrics
    performance = sum(mlist)/len(mlist)
    return ob, performance


def simulate(strategy: any, base_path: str) -> tuple:
    """Simulate a strategy.

    Args:
        strategy (any): strategy to simulate

    Returns:
        tuple: order book and cumulative results
    """
    path_list = init_monte_carlo()
    result_list = []
    order_book_list = []
    i = 0
    current_time = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    save_path = ensure_dir(os.path.join(base_path, f"simulation-{current_time}"))
    for sim_type,data_path in path_list:
        i += 1 
        logger.info(f"***********************[{i}]/[{len(path_list)}]***********************")
        return_value = []
        simulator_thread = threading.Thread(target=start_simulator, args=(data_path, return_value))
        strategy_thread = threading.Thread(target=start_strategy, args=(strategy,))
        simulator_thread.start()
        logger.info(f"Simulator started.")
        sleep(2)
        strategy_thread.start()
        logger.info(f"Strategy started.")
        simulator_thread.join()
        strategy_thread.join()
        logger.info(f"Simulator and strategy stopped.")
        logger.info(f"Starting analysis...")
        order_book = return_value[0]
        order_book_list.append(order_book)
        order_book = return_value[0]
        fig_save_path = ensure_dir(os.path.join(save_path,sim_type,f"{i}"))
        analysis(order_book=order_book, cumulative_results=result_list, save_path=fig_save_path,sim_type=sim_type)
        logger.info(f"Analysis finished")
    logger.info(f"******************CumulativeResults******************")
    logger.info(f"Cumulative results: ")
    final_results = cumulative_analysis(result_list)
    for key, value in final_results.items():
        logger.info(f"{key} : {value}")
    # Save cumulative results as json under simtest.../simulation.../cumulative_result.json
    with open(os.path.join(save_path, "cumulative_results.json"), "w") as f:
        json.dump(final_results, f)
    return final_results, order_book_list
    

def live_trade():
    pass

def get_benchmark():
    # benchmark measure 12-9-6-3-1 months, 2 weeks and last 3 days
    
    # get current date YYYY-MM-DD
    cur = datetime.datetime.now() - datetime.timedelta(days=1)
    cur = cur.strftime("%Y-%m-%d")
    # get 12 months ago
    start = datetime.datetime.strptime(cur, "%Y-%m-%d") - datetime.timedelta(days=365)
    start = start.strftime("%Y-%m-%d")
    # get 9 months ago
    start2 = datetime.datetime.strptime(cur, "%Y-%m-%d") - datetime.timedelta(days=270)
    start2 = start2.strftime("%Y-%m-%d")
    # get 6 months ago
    start3 = datetime.datetime.strptime(cur, "%Y-%m-%d") - datetime.timedelta(days=180)
    start3 = start3.strftime("%Y-%m-%d")
    # get 3 months ago
    start4 = datetime.datetime.strptime(cur, "%Y-%m-%d") - datetime.timedelta(days=90)
    start4 = start4.strftime("%Y-%m-%d")
    # get 1 month ago
    start5 = datetime.datetime.strptime(cur, "%Y-%m-%d") - datetime.timedelta(days=30)
    start5 = start5.strftime("%Y-%m-%d")
    # get 2 weeks ago
    start6 = datetime.datetime.strptime(cur, "%Y-%m-%d") - datetime.timedelta(days=14)
    start6 = start6.strftime("%Y-%m-%d")
    # get 3 days ago
    start7 = datetime.datetime.strptime(cur, "%Y-%m-%d") - datetime.timedelta(days=3)
    start7 = start7.strftime("%Y-%m-%d")

    trios = []
    # Ask user the interval to backtest
    interval = input("Interval(1m/1h/15m etc.): ").lower()
    # check if the interval is valid
    avail_intervals = ["12h", "15m", "1d", "1h", "1m", "2h", "30m", "3m", "4h", "5m", "6h", "8h"]
    while interval not in avail_intervals:
        logger.warning(f"Interval must be one of {avail_intervals}")
        interval = input("Interval(1m/1h/15m etc.): ").lower()

    pair = input("Pair(Press enter for BTCUSDT): ")
    if pair == "":
        pair = "BTCUSDT"
        
    trios.append((interval, start, cur))
    trios.append((interval, start2, cur))
    trios.append((interval, start3, cur))
    trios.append((interval, start4, cur))
    trios.append((interval, start5, cur))
    trios.append((interval, start6, cur))
    trios.append((interval, start7, cur))
    return trios, pair



def open_browser(host, port):
    import webbrowser
    sleep(5)
    webbrowser.open_new_tab(f"http://{host}:{port}")
        


def start_backtester(interval:any, start_date:str, final_date:str, pair:str, return_value:list, ready:list):
    """Start the backtester. This function is called by a thread

    Args:
        interval (any): interval of the data
        start_date (str): start date of the data
        final_date (str): final date of the data
        return_value (list): list to store the order book

    Returns:
        list: order book
    """
    backtester = Backtester(interval=interval, start_date=start_date, final_date=final_date, pair=pair)
    loaded = backtester.load_data()
    ready.append(loaded)
    ready.append(backtester.port)
    backtester.start()
    order_book = backtester.disconnect()
    return_value.append(order_book)
    logger.info("Backtester stopped")


def start_simulator(data_path: str, return_value:list) -> None:
    """Start the simulator

    Args:
        data_path (str): path to the data
        return_value (list): list to store the order book

    Returns:
        list: order book
    """
    simulator = Simulator(data_path=data_path)
    simulator.load_data()
    simulator.start()
    order_book = simulator.disconnect()
    logger.info("Simulator stopped")
    return_value.append(order_book)

def get_delisted_configs() -> list:
    """Get the delisted quads from the config.yaml file

    Returns:
        list: list of quads(Interval, start, end, pair)
    """
    # Define the path to your config.yaml file
    config_file_path = 'config.yaml'

    # Read the YAML file
    with open(config_file_path, 'r') as file:
        config_data = yaml.safe_load(file)

    # Access the survivorship_bias information
    survivorship_bias_info = config_data.get('survivorship_bias', [])


    delist_configs = []

    # Iterate over each delist event
    for event in survivorship_bias_info:
        delist_date = event.get('delist_date', '')
        news_date = event.get('news_date', '')
        pairs = event.get('pair', [])
        announcement_url = event.get('announcement_url', '')

        run_config = {"ref": None, "quads": []}

        # Compute 1 week before delist date
        # delist_week_start = datetime.datetime.strptime(delist_date, "%Y-%m-%d") - datetime.timedelta(days=7)
        # delist_week_start = delist_week_start.strftime("%Y-%m-%d")
        # delist_week_end = datetime.datetime.strptime(delist_date, "%Y-%m-%d") - datetime.timedelta(days=1)
        # delist_week_end = delist_week_end.strftime("%Y-%m-%d")

        # Compute 1 month before delist date
        delist_month_start = datetime.datetime.strptime(delist_date, "%Y-%m-%d") - datetime.timedelta(days=30)
        delist_month_start = delist_month_start.strftime("%Y-%m-%d")
        delist_month_end = datetime.datetime.strptime(delist_date, "%Y-%m-%d") - datetime.timedelta(days=1)
        delist_month_end = delist_month_end.strftime("%Y-%m-%d")

        # quads.append(('1h', delist_week_start, delist_week_end, "BTCUSDT"))
        run_config["ref"] = ('1h', delist_month_start, delist_month_end, "BTCUSDT")

        # Iterate over each pair
        for pair in pairs:
        # append interval, start, end
            # Delist week
            # Append to quads
            # quads.append(('1h', delist_week_start, delist_week_end, pair))

            # Delist Month
            # Append to quads
            run_config["quads"].append(('1h', delist_month_start, delist_month_end, pair))

        delist_configs.append(run_config)
    return delist_configs


def generate_survivorship_bias_report(base_path: str, results: dict) -> None:
    """ According to the results of the survivorship bias analysis, generate a report.

    Args:
        base_path (str): path to the base directory
        results (dict): raw results obtained from the backtests
    """
    pass


def _backtest(strategy: any, base_path: str, quad: tuple, verbose:bool = False, model_kwargs:dict = {}) -> dict:
    interval, start, end, pair = quad
    return_value = []
    ready_value = []
    backtester_thread = threading.Thread(target=start_backtester, args=(interval, start, end, pair, return_value, ready_value))
    kwargs = {"strategy": strategy, "model_kwargs": model_kwargs}
    strategy_thread = threading.Thread(target=start_strategy, kwargs=kwargs)
    backtester_thread.start()

    while len(ready_value) == 0:
        try:
            if ready_value != [] and ready_value[0]:
                break
        except:
            sleep(1)
    sleep(2)
    strategy_thread.start()
    backtester_thread.join()
    strategy_thread.join()
    order_book = return_value[0]
    order_book.set_stop_loss(model_kwargs["stop_loss"] if "stop_loss" in model_kwargs and model_kwargs["stop_loss"] else 0.0)
    fig_save_path = ensure_dir(os.path.join(base_path, "backtest_{}_{}_{}_{}".format(interval, pair, start, end)))
    M = analysis(order_book=order_book, cumulative_results=None, save_path=fig_save_path, verbose=verbose)
    return M, order_book

def get_cumulative_results(M: dict) -> dict:
    # Filter those that are not float values
    M = {k: v for k, v in M.items() if isinstance(v, float)}
    # Filter those that are not cumulative values
    # M = {k: v for k, v in M.items() if "cumulative" in k}
    return M

def generate_report(base_path: str, quad: tuple, results: dict) -> None:
    """Generate a report for the given quad

    Args:
        base_path (str): path to the base directory
        quad (tuple): quad to generate the report
        results (dict): results of the backtest
    """
    interval, start, end, pair = quad
    # Create a directory to store the report
    report_path = ensure_dir(os.path.join(base_path, "report_{}_{}_{}_{}".format(interval, pair, start, end)))
    # Save the results as json
    with open(os.path.join(report_path, "results.json"), "w") as f:
        json.dump(results, f)
    # Save the results as csv
    with open(os.path.join(report_path, "results.csv"), "w") as f:
        for key, value in results.items():
            f.write(f"{key},{value}\n")
    # Save the results as txt
    with open(os.path.join(report_path, "results.txt"), "w") as f:
        for key, value in results.items():
            f.write(f"{key}: {value}\n")
    # Save the plot
    fig = plt.figure(figsize=(20, 10))
    plt.plot(results.keys(), results.values())
    plt.title(f"Backtest results for {pair} from {start} to {end} with {interval} interval")
    plt.xlabel("Metrics")
    plt.ylabel("Values")
    plt.xticks(rotation=90)
    plt.savefig(os.path.join(report_path, "results.png"))
    plt.close(fig)

def survivorship_bias(strategy: any, base_path: str) -> None:
    """Starts the survirship bias analysis and generates a report.
    Main purpose is to show the user how the algorithm performs on the delisted coins.
    """
    delist_configs = get_delisted_configs()

    results = {}

    # Iterate over each delist config
    # Delist configs will have "ref" AND "pairs"
    for config in delist_configs:
        reference_quad = config["ref"]
        ref_M, _ = _backtest(strategy, base_path, reference_quad, verbose=False)
        for quad in config["quads"]:
            pair_M, _ = _backtest(strategy, base_path, quad, verbose=False)

            import numpy as np
            from scipy.stats import pearsonr

            for quad in config["quads"]:
                pair_M, _ = _backtest(strategy, base_path, quad, verbose=False)
                # compare the ref_M and the pair_M to store the values for the pair
                pair_results = get_cumulative_results(pair_M)
                ref_results = get_cumulative_results(ref_M)
                pair_values = np.array(list(pair_results.values()))
                ref_values = np.array(list(ref_results.values()))
                # calculate mean and standard deviation
                pair_mean = np.mean(pair_values)
                ref_mean = np.mean(ref_values)
                pair_std = np.std(pair_values)
                ref_std = np.std(ref_values)
                # calculate correlation coefficient
                corr_coef, _ = pearsonr(pair_values, ref_values)
                # store the values for the pair
                results[quad] = {
                    "pair_mean": pair_mean,
                    "ref_mean": ref_mean,
                    "pair_std": pair_std,
                    "ref_std": ref_std,
                    "corr_coef": corr_coef
                }
                # use these values with generate_report to create a report for the pair
                generate_report(base_path, quad, results[quad])
    try:
        # Save results as json under simtest.../survivorship_bias.json
        with open(os.path.join(base_path, "survivorship_bias.json"), "w") as f:
            json.dump(results, f)
    except:
        logger.warning("Could not save the results as json file.")
        exit()

    logger.info("Backtesting on delisted tokens finished. Initializing analysis over collected data.")

    try:
        generate_survivorship_bias_report(base_path, results)
    except Exception as e:
        logger.warning("Could not generate the report.")
        logger.warning(e)
        exit()

def available_strategies() -> list:
    strategies = BaseStrategy.__subclasses__()
    strategies = sorted(strategies, key=lambda x: x.__name__)
    return strategies

def select_strategy_with_name(name: str) -> any:
    strategies = available_strategies()
    for strategy in strategies:
        if strategy.__name__ == name:
            return strategy
    return None

def select_strategy() -> any:
    # get all the strategies imported as "from strategy import *"
    strategies = BaseStrategy.__subclasses__()
    # sort by the name
    strategies = sorted(strategies, key=lambda x: x.__name__)
    # list strategies for user
    # Uncolored format
    # print("Strategies:")
    # Colored format
    print("\033[1;32;40mStrategies:\033[0m")
    # List strategies with color
    for i, strategy in enumerate(strategies):
        # Uncolored format
        # print(f"{i+1}. {strategy.__name__}")
        # Colored format
        print(f"\t{i+1}. \033[1;32;40m{strategy.__name__}\033[0m")
    # ask user to choose a strategy
    choice = int(input("Choose a strategy: "))
    # check if choice is valid
    while choice < 1 or choice > len(strategies):
        logger.warning("Invalid choice.")
        choice = int(input("Choose a strategy: "))
    # return the strategy
    strategy = strategies[choice-1]
    return strategy


def start_strategy(**kwargs):
    """Start the strategy
    
    Args:
        None

    Returns:
        None
    """
    # unpack the arguments
    strategy = kwargs["strategy"]
    model_kwargs = kwargs["model_kwargs"]
    # create an instance of the strategy
    st = strategy(**model_kwargs)
    # start the strategy
    st.connect()
    st.disconnect()

def is_valid_date(date: str) -> bool:
    """Check if the date is valid

    Args:
        date (str): date to check

    Returns:
        bool: True if the date is valid, False otherwise
    """
    try:
        datetime.datetime.strptime(date, "%Y-%m-%d")
        # check if the date is in the past
        if datetime.datetime.strptime(date, "%Y-%m-%d") > datetime.datetime.now():
            return False
        return True
    except ValueError:
        return False

def select_dates() -> tuple:
    """Select the dates for the backtest

    Args:
        None

    Returns:
        tuple: interval, start date, final date
    """
    pair = input("Pair(Press enter for BTCUSDT): ")
    if pair == "":
        pair = "BTCUSDT"

    avail_intervals = ["12h", "15m", "1d", "1h", "1m", "2h", "30m", "3m", "4h", "5m", "6h", "8h"]
    interval = input("Interval(1m/1h/15m etc.): ").lower()
    # check if the interval is valid
    while interval not in avail_intervals:
        logger.warning(f"Interval must be one of {avail_intervals}")
        interval = input("Interval(1m/1h/15m etc.): ").lower()

    start_date = input("Start Date(ex: YYYY-MM-DD): ")
    # check if the date is valid
    while not is_valid_date(start_date):
        logger.warning("Invalid date")
        start_date = input("Start Date(ex: YYYY-MM-DD): ")


    final_date = input("Final Date(ex: YYYY-MM-DD): ")
    # check if the date is valid
    while not is_valid_date(final_date) and final_date < start_date:
        logger.warning("Invalid date")
        final_date = input("Final Date(ex: YYYY-MM-DD): ")

    # Zero-fill month and day
    start_date = start_date.split("-")
    start_date = "-".join([start_date[0], start_date[1].zfill(2), start_date[2].zfill(2)])
    final_date = final_date.split("-")
    final_date = "-".join([final_date[0], final_date[1].zfill(2), final_date[2].zfill(2)])

    return interval, start_date, final_date, pair

def init_monte_carlo() -> list:
    """
    Initialize the Monte Carlo object and generate k paths

    Args:
        None

    Returns:
        list: list of paths
    """
    # load config.yaml 
    # path of the
    with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.yaml')) as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    # init MC object
    mc = MonteCarlo()
    mc.set_params(config)
    path_list = mc.generate_k()
    return path_list

def analysis(order_book,save_path, cumulative_results=None,sim_type=None,verbose=True):
    M = TradingMetrics(order_book, verbose=verbose)
    M = M.calculate_metrics(save_path=save_path)
    if cumulative_results is not None and sim_type is not None:
        cumulative_results.append((M, sim_type))
    return M

def cumulative_analysis(cumulative_results):
    final_results = {}
    for result, sim_type in cumulative_results:
        if sim_type not in final_results.keys():
            final_results[sim_type] = {}
            for key, value in result.items():
                final_results[sim_type][key] = []
        for key, value in result.items():
            final_results[sim_type][key].append(value)

    for sim_type, result  in final_results.items():
        for key, value in result.items():
            final_results[sim_type][key] = sum(value)/len(value)

    return final_results


def get_local_time():
    r"""Get current time

    Returns:
        str: current time
    """
    cur = datetime.datetime.now()
    cur = cur.strftime("%b-%d-%Y_%H-%M-%S")

    return cur


def ensure_dir(dir_path):
    r"""Make sure the directory exists, if it does not exist, create it

    Args:
        dir_path (str): directory path

    """
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    return dir_path

def get_config():
    with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.yaml')) as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    return config