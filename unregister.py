# This code serves for unregistering a strategy

import os
import shutil
import datetime
from src._regs import register_init 

def unregister(strategy_names:list, available_strategies:list) -> None:
    """Unregister a strategy

    Args:
        strategy_name (str): name of the strategy
    """
    # Alter __init__ with available_strategies excluded strategy_names
    available_strategies = [strategy for strategy in available_strategies if strategy not in strategy_names]
    filtered_strategies = []
    for strategy in available_strategies:
        if strategy == ".DS_Store":
            continue
        strategy = strategy.split(".py")[0]
        if strategy != "" and strategy[0] != "." and strategy[0] != "_":
            filtered_strategies.append(strategy)
    register_init(filtered_strategies)

    # Remove the strategy file
    for strategy_name in strategy_names:
        # Check if the strategy exists
        if not os.path.exists(os.path.join("src", "strategy", f"{strategy_name}.py")):
            print(f"Strategy {strategy_name} does not exist.")
            continue
        # Archive the strategy file under the strategy archive folder
        current_time = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

        # Create archive
        if not os.path.exists("archive_strategy"):
            os.mkdir("archive_strategy")

        shutil.move(os.path.join("src", "strategy", f"{strategy_name}.py"), os.path.join("archive_strategy", f"{strategy_name}_{current_time}.py"))
        # print with green
        print("\033[92m" + f"Successfully unregistered {strategy_name} strategy." + "\033[0m")

if __name__ == "__main__":
    # Ask user if they want to unregister a strategy
    # if yes, then unregister
    # if no, then exit
    # Use green color to emphasize warning
    print("\033[92m" + "WARNING: This will unregister a strategy for the SimTest and archive the code." + "\033[0m")
    print("Do you want to continue? (y/n)")
    answer = input()
    if answer.lower() == 'y':
        # List strategies
        available_strategies = os.listdir(os.path.join("src", "strategy"))
        available_strategies = [strategy.split(".")[0] for strategy in available_strategies if strategy[0] != "_"]
        available_strategies = [strategy for strategy in available_strategies if strategy != ""]
	# Sort by the name
        available_strategies.sort()
        
        # Print with color
        print("\033[1;32;40mStrategies:\033[0m")
        # List strategies with color
        for i, strategy in enumerate(available_strategies):
            print(f"\t{i+1}. \033[1;32;40m{strategy}\033[0m")

        # Ask user the numbers of the strategies to unregister
        print("To specify strategies to unregister, enter the numbers of the strategies separated by whitespace.")
        print("Example: ")
        print("\t>1 2 3\t\t# unregister strategies 1, 2, 3")
        print("\t>7\t\t# unregister strategy 7")
        strategy_numbers = input("Enter strategies to unregister: ")
        strategy_numbers = strategy_numbers.split(" ")
        strategy_numbers = [int(strategy_number) for strategy_number in strategy_numbers]
        strategy_names = [available_strategies[strategy_number-1] for strategy_number in strategy_numbers]
        unregister(strategy_names=strategy_names, available_strategies=available_strategies)
    else:
        exit()
