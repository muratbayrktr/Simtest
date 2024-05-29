"""
Main file for the project.

This file is the entry point for the project.
    
"""
# imports
from _regs import handle_strategy_folder_exceptions
# Handle strategy folder exceptions
handle_strategy_folder_exceptions()


# Continue importing
from _logger import init_logger
from _utils import select_strategy, backtest, simulate, open_browser, \
        backtest_benchmark, available_strategies, survivorship_bias, _backtest, select_strategy_with_name
from time import sleep
from argparse import ArgumentParser

import threading
import datetime
import logging
import yaml
import sys
import os

# Argument parser
parser = ArgumentParser()
# All of the arguments are optional, if not given main will be executed
# Strategy
parser.add_argument('-s', '--strategy', help='Specify the strategy to be used. The exact class name of the strategy should be given.')
# Exchange
parser.add_argument('-e', '--exchange', help='Specify the exchange to be used.')
# Market type
parser.add_argument('-m', '--market_type', help='Specify the market type to be used.')
# Time interval
parser.add_argument('-t', '--time_interval', help='Specify the time interval to be used.')
# Beginning date
parser.add_argument('-b', '--beginning_date', help='Specify the beginning date to be used.')
# End date
parser.add_argument('-ed', '--end_date', help='Specify the end date to be used.')
# Pair 
parser.add_argument('-p', '--pair', help='Specify the pair to be used.')
# Temporarily enable an option to pass stop loss to strategy (optional)
parser.add_argument('-mp', '--model_parameters', help='Specify the model parameters to be used.')


# Example usage
# python src/main.py -s FibonacciRetracements -e bybit -m futures -t 1h -b 2023-06-01 -ed 2023-06-07 -p BTCUSDT

def parse_args():
    # Parse arguments
    args = parser.parse_args()


    # If strategy is given, check if it is available
    if args.strategy:
        avails = available_strategies()
        avails = [x.__name__ for x in avails]
        if args.strategy not in avails:
            print(f"\033[1;31;38m{args.strategy} is not available. Please check the strategy folder.\033[0m")
            # Print available strategies
            print("\033[1;32;38mAvailable strategies:\033[0m")
            for strategy in avails:
                if strategy != '__pycache__' and strategy != '__init__.py' and strategy != '.DS_Store' and strategy != '':
                    print(f"\033[1;33;38m\t{strategy}\033[0m")
            sys.exit(0)

    # If exchange is given, check if it is available
    if args.exchange:
        if args.exchange not in ['bybit', 'binance']:
            print(f"\033[1;31;38m{args.exchange} is not available. Please check the exchange folder.\033[0m")
            sys.exit(0)

    # If market type is given, check if it is available
    if args.market_type:
        if args.market_type not in ['spot', 'futures']:
            print(f"\033[1;31;38m{args.market_type} is not available. Please check the market_type folder.\033[0m")
            sys.exit(0)

    # If time interval is given, check if it is available
    if args.time_interval:
        if args.time_interval not in ['1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '12h', '1d']:
            print(f"\033[1;31;38m{args.time_interval} is not available. Please check the time_interval folder.\033[0m")
            sys.exit(0)

    # If beginning date is given, check if it is in the correct format
    if args.beginning_date:
        try:
            datetime.datetime.strptime(args.beginning_date, '%Y-%m-%d')
        except ValueError:
            print(f"\033[1;31;38m{args.beginning_date} is not in the correct format. Please check the beginning_date folder.\033[0m")
            sys.exit(0)

    # If end date is given, check if it is in the correct format
    if args.end_date:
        try:
            datetime.datetime.strptime(args.end_date, '%Y-%m-%d')
        except ValueError:
            print(f"\033[1;31;38m{args.end_date} is not in the correct format. Please check the end_date folder.\033[0m")
            sys.exit(0)


    # If an argument is given, all of them should be given
    if args.strategy or args.exchange or args.market_type or args.time_interval or args.beginning_date or args.end_date or args.pair:
        if not args.strategy or not args.exchange or not args.market_type or not args.time_interval or not args.beginning_date or not args.end_date or not args.pair:
            print("\033[1;31;38mIf an argument is given, all of them should be given.\033[0m")
            sys.exit(0)
        else:
            # If all of the arguments are given, backtest will be executed
            strategy_name = args.strategy
            exchange = args.exchange
            market_type = args.market_type
            time_interval = args.time_interval
            beginning_date = args.beginning_date
            end_date = args.end_date
            pair = args.pair
            current_time = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            base_path = None
            strategy_selected = True
            config = {
                'strategy' : strategy_name,
                'state': 'info'}
            # initialize logger
            logger = init_logger(config=config)
            logger = logging.getLogger('IPC')
            logger.info("Backtesting...")
            # Open config.yaml file and change the parameters
            with open("config.yaml", 'r') as stream:
                content = stream.readlines()
            for i in range(len(content)):
                if "exchange" in content[i]:
                    content[i] = f"exchange: \"{exchange}\"\n"

                if "market_type" in content[i]:
                    content[i] = f"market_type: \"{market_type}\"\n"


            with open("config.yaml", 'w') as stream:
                stream.writelines(content)

            base_path = os.path.join("results", exchange.capitalize() + "_" + market_type.capitalize() ,f"{strategy_name}", f"simtest-{current_time}")
            strategy = select_strategy_with_name(strategy_name)
            # usage is: -mp param1 value1 param2 value2 ... paramN valueN
            model_kwargs = {}
            if args.model_parameters:
                model_kwargs = {}
                args.model_parameters = args.model_parameters.split()
                for i in range(0,len(args.model_parameters),2):
                    model_kwargs[args.model_parameters[i]] = eval(args.model_parameters[i+1])

            logger.info(f"Model kwargs: {model_kwargs}")
            if strategy:
                order_book = _backtest(strategy=strategy, base_path=base_path, 
                                    quad=(time_interval, beginning_date, end_date, pair), 
                                    verbose=True, model_kwargs=model_kwargs)
            else:
                raise Exception("Strategy is not found.")
            sys.exit(0)
    else:
        # If no argument is given, main will be executed
        return 



# main function
def main():
    # Set path to SimTest
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    # initialize logger
    strategy_selected = False
    logger = logging.getLogger('IPC')
    current_time = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    base_path = None 
    # main loop
    # Open config.yaml file 
    with open("config.yaml", 'r') as stream:
        try:
            config = yaml.safe_load(stream)
            exchange = config['exchange']
            market_type = config['market_type']
        except yaml.YAMLError as exc:
            print(exc)

    while True:
        # Print main menu as colorized
        print("\033[1;32;38mMain menu:\033[0m")
        print("\033[1;33;38m\t1. Backtest\033[0m")
        print("\033[1;32;38m\t2. Simulate\033[0m")
        print("\033[1;35;38m\t3. Benchmark Backtest\033[0m")
        print("\033[1;32;38m\t4. Survivorship Bias\033[0m")
        print("\033[1;37;38m\t5. Exit\033[0m")
        print("\033[1;38;38m\t6. Help\033[0m")
        print("\033[1;39;38m\t7. About\033[0m")
        print("\033[1;34;38m\t8. Select Strategy\033[0m")
        print("\033[1;31;38m\t9. Full Backtest\033[0m")
        print("\033[1;36;38m\t10. Open Dashboard\033[0m")
        # Background color none

        choice = input("Choose an option: ")

        if choice == '1':
            if not strategy_selected:
                logger.info("Selecting strategy")
                strategy = select_strategy()
                config = {
                    'strategy' : strategy.__name__,
                    'state': 'info'}
                # initialize logger
                logger = init_logger(config=config)
                logger = logging.getLogger('IPC')
                base_path = os.path.join("results", exchange.capitalize() + "_" + market_type.capitalize(),f"{strategy.__name__}", f"simtest-{current_time}")
                
                strategy_selected = True
            logger.info("Backtesting...")
            order_book = backtest(strategy=strategy, base_path=base_path)
        elif choice == '2':
            if not strategy_selected:
                logger.info("Selecting strategy")
                strategy = select_strategy()
                config = {
                    'strategy' : strategy.__name__,
                    'state': 'info'}
                # initialize logger
                logger = init_logger(config=config)
                logger = logging.getLogger('IPC')
                base_path = os.path.join("results", exchange.capitalize() + "_" + market_type.capitalize(),f"{strategy.__name__}", f"simtest-{current_time}")
                strategy_selected = True
            logger.info("Simulating...")
            order_book_list = simulate(strategy=strategy, base_path=base_path)
        elif choice == '3':
            if not strategy_selected:
                logger.info("Selecting strategy")
                strategy = select_strategy()
                config = {
                    'strategy' : strategy.__name__,
                    'state': 'info'}
                # initialize logger
                logger = init_logger(config=config)
                logger = logging.getLogger('IPC')
                base_path = os.path.join("results", exchange.capitalize() + "_" + market_type.capitalize(),f"{strategy.__name__}", f"simtest-{current_time}")
                strategy_selected = True
            logger.info("BENCHMARK SETTINGS: [12-9-6-3-1 Months, 2 weeks and 3 days] periods, with the specified time interval i.e [1m, 15m, 30m, 1h...]:")
            order_book_list, metrics = backtest_benchmark(strategy=strategy, base_path=base_path)
        elif choice == '4':
            if not strategy_selected:
                logger.info("Selecting strategy")
                strategy = select_strategy()
                config = {
                    'strategy' : strategy.__name__,
                    'state': 'info'}
                # initialize logger
                logger = init_logger(config=config)
                logger = logging.getLogger('IPC')
                base_path = os.path.join("results", exchange.capitalize() + "_" + market_type.capitalize(),f"{strategy.__name__}", f"simtest-{current_time}")
                strategy_selected = True
            logger.warning("Survivorship Bias is selected. The performance of the strategy on the delisted coins will be checked.") 
            logger.warning("The config EXCHANGE & MARKET will be overwritten by the SimTest. Please change it later if you are going to use the strategy again.")
            # Required for restoring the config.yaml file
            stored_exchange, stored_market_type = None, None
            content = None
            # Alter the config.yaml file
            with open("config.yaml", 'r') as stream:
                content = stream.readlines()

                for i in range(len(content)):
                    if "exchange" in content[i]:
                        stored_exchange = content[i]
                        content[i] = f"exchange: \"binance\"\n"

                    if "market_type" in content[i]:
                        stored_market_type = content[i]
                        content[i] = f"market_type: \"spot\"\n"

            with open("config.yaml", 'w') as stream:
                stream.writelines(content)

            # Run survivorship bias
            survivorship_bias(strategy=strategy, base_path=base_path)

            # Restore the config.yaml file
            with open("config.yaml", 'r') as stream:
                content = stream.readlines()

                for i in range(len(content)):
                    if "exchange" in content[i]:
                        content[i] = stored_exchange

                    if "market_type" in content[i]:
                        content[i] = stored_market_type

            with open("config.yaml", 'w') as stream:
                stream.writelines(content)
        elif choice == '5':
            break
        elif choice == '6':
            print(\
"""
Help:

1. Backtest: Backtests the strategy with the specified time interval and period.
2. Simulate: Simulates the strategy with the specified time interval and period.
3. Benchmark Backtest: Backtests the strategy with the set of predefined 
    specified time interval and period.
4. Open Dashboard: Opens the dashboard for the strategy. (Only works if the
    report.py is invoked by "python src/report.py" in parallel.)
5. Exit: Exits the program.
6. Help: Prints this help message.
7. About: Prints the about message.
8. Select Strategy: Selects the strategy to be used.
9. Full Backtest: Backtests all the strategies available.
10. Survivorship Bias: Runs survivorship bias on the strategies. Checks the
    performance of the strategies on the delisted coins and prints the performance
    of the strategies.

Example usage:

    \033[1;33;38m python src/main.py -s cb001 -e binance -m futures -t 1h -b 2023-06-01 -ed 2023-06-07 -p BTCUSDT -mp param1 value1... paramN valueN\033[0m
    
""")
            sleep(1)
        elif choice == '7':
            print(\
"""
About:
SimTest is a backtesting and simulation tool for crypto trading strategies.
It is developed in a parallel and distributed way, only thing a user should do 
is to obey the rules of the framework and implement the strategy in a proper way.
The menu is self-explanatory, but if you need more information about the framework
you can check the README.md file on the GitHub repository.
""")
            sleep(1)
        elif choice == '8':
            strategy_selected = False
            current_time = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            base_path = None 
            strategy = select_strategy()
            config = {
                'strategy' : strategy.__name__,
                'state': 'info'}
            # initialize logger
            logger = init_logger(config=config)
            logger = logging.getLogger('IPC')
            base_path = os.path.join("results", exchange.capitalize() + "_" + market_type.capitalize(),f"{strategy.__name__}", f"simtest-{current_time}")
            strategy_selected = True
        elif choice == '9':
            # print in red "Warning: This will benchmark backtest all the strategies available. Would you like to continue?"
            print("\033[1;31;38mWarning: This will benchmark backtest all the strategies available. Would you like to continue? (y,n)\033[0m")
            ans = input().lower().strip()
            best_performing_strategies = []
            if ans == 'y':
                logger.info("************* Benchmark backtesting all the strategies *************")
                avail_strats = available_strategies()
                for strategy in avail_strats:
                    print(f"\033[1;31;38m************* Backtesting {strategy.__name__} *************\033[0m")
                    if strategy != '__pycache__' and strategy != '__init__.py':
                        strategy_selected = False
                        current_time = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
                        base_path = None 
                        config = {
                            'strategy' : strategy.__name__,
                            'state': 'info'}
                        # initialize logger
                        logger = init_logger(config=config)
                        logger = logging.getLogger('IPC')
                        base_path = os.path.join("results", exchange.capitalize() + "_" + market_type.capitalize(),f"{strategy.__name__}", f"simtest-{current_time}")
                        strategy_selected = True
                        logger.info("BENCHMARK SETTINGS: [12-9-6-3-1 Months, 2 weeks and 3 days] periods, with the specified time interval i.e [1m, 15m, 30m, 1h...]:")
                        order_book_list,performance = backtest_benchmark(strategy=strategy, base_path=base_path)
                        try:
                            if performance >= 60:
                                best_performing_strategies.append((strategy.__name__,performance))
                        except Exception as e:
                            print(e)
        elif choice == '10':
            print("\033[1;31;38mSimTest will try to open the dasboard, but this won't work unless you run the report.py file in parallel.\033[0m")
            logger.info("Opening browser...")
            host = '127.0.0.1'
            port = 8050
            browser = threading.Thread(target=open_browser, args=(host,port))
            browser.start()
            browser.join()
            sleep(1)

        else:
            logger.info("Invalid choice.")
            sleep(1)
    
    logger.info("SimTest is done. Exiting.")
    sys.exit(0)


if __name__ == "__main__":
    # Parse arguments
    parse_args()
    # main entry point
    main()
