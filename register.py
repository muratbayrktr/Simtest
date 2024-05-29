# This code is for setting up the folder src/strategy/ folder and the file src/strategy/__init__.py
import os 
from src._regs import register_init, create_template, register



if __name__ == "__main__":
    # Ask user if they want to register a strategy
    # if yes, then register
    # if no, then exit
    # Use green color to emphasize warning
    print("\033[92m" + "WARNING: This will register a new strategy for the SimTest" + "\033[0m")
    print("Do you want to continue? (y/n)")
    answer = input()
    if answer.lower() == 'y':
        # Ask user the name of the strategy
        strategy_name = input("Enter the name of the strategy: ")

        # Check if the strategy already exists
        if os.path.exists(os.path.join("src", "strategy", f"{strategy_name}.py")): # os.path.exists(f"src/strategy/{strategy_name}.py")
            print("\033[91m" + f"Strategy {strategy_name} already exists." + "\033[0m")
            exit()

        # Check if the strategy name is valid
        if not strategy_name.isidentifier():
            print("\033[91m" + f"Strategy name {strategy_name} is not valid." + "\033[0m")
            exit()
        register(strategy_name=strategy_name)
    else:
        exit()

