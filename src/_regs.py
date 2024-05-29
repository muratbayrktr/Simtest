import os
import logging

def create_template(strategy_name):
    template = \
f"""
import os
import sys
src_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
__path__ = [src_dir]
sys.path += __path__

from _base_strategy import BaseStrategy
from _orders import OpenLong, OpenShort, CloseLong, CloseShort, NoOrder
import os

class {strategy_name}(BaseStrategy):
    def __init__(self):
        super().__init__()
        # Add your variables here

    def on_receive(self, data):
        # Order list for your orders
        orders = []


        # Add your strategy here
        # data is a dictionary with the following keys:
        # tick, time, price, data (which is a dictionary of the row in the dataset)

        # Example:
        # if data['price'] > 100:
        #     self.send(OpenLong(self.id, data['time'], data['price'], 0.1).to_dict())
        #     self.id += 1
        #     self.in_long = True
        # 
        # 
        # Even if you don't send any orders, you SimTest automatically detects it 
        # and sends NoOrder() to the exchange.

        # If you want to send multiple orders, you can send a list of orders
        payload = {{'message': 'ORDERLIST', 'data': orders}}
        self.send(payload)
"""
    return template

def register_init(available_strategies):
    template = \
f"""
__all__ = {available_strategies}
"""
    with open("src/strategy/__init__.py", "w") as f:
        f.write(template)
    f.close()
    
def register(strategy_name):
    # Create the file src/strategy/strategy_name.py
    with open(os.path.join("src", "strategy", f"{strategy_name}.py"), "w") as f:
        f.write(create_template(strategy_name))
    f.close()
    # Print with color
    available_strategies = os.listdir(os.path.join("src", "strategy"))
    filtered_strategies = []
    for strategy in available_strategies:
        if strategy == ".DS_Store":
            continue
        strategy = strategy.split(".py")[0]
        if strategy != "" and strategy[0] != "." and strategy[0] != "_":
            filtered_strategies.append(strategy)
    register_init(filtered_strategies)
    print("\033[92m" + f"Successfully registered {strategy_name} strategy." + "\033[0m")

STRATEGY_DIR = "strategy"

def check_all_list():
    strategy_path = os.path.join(os.path.dirname(__file__), STRATEGY_DIR)
    init_path = os.path.join(strategy_path, "__init__.py")
    with open(init_path, "r") as f:
        lines = f.readlines()
    all_list = None
    for line in lines:
        if line.startswith("__all__"):
            all_list = line.strip().split("=")[1].strip("[] \n")
            break
    if all_list:
        all_list = [s.strip("'\"") for s in all_list.split(",")]
        all_list = [s.replace("'","").strip() for s in all_list if s]
        with open(init_path, "w") as f:
            for line in lines:
                if line.startswith("__all__"):
                    line = f"__all__ = {str(all_list)}\n"
                f.write(line)

def handle_strategy_folder_exceptions():
    logger = logging.getLogger('Register Manager')
    # 1. Check if strategy folder exists
    if not os.path.exists(os.path.join(os.path.dirname(__file__), "strategy")):
        print("Strategy folder does not exist. Creating one...")
        os.makedirs(os.path.join(os.path.dirname(__file__), "strategy"))

    # 2. Check if __init__.py exists
    if not os.path.exists(os.path.join(os.path.dirname(__file__), "strategy", "__init__.py")):
        logger.error("__init__.py does not exist. Creating one...")
        with open(os.path.join(os.path.dirname(__file__), "strategy", "__init__.py"), "w") as f:
            f.write("")

    # 3. Check if __all__ = [] exists and contains the file under the strategy/ folder
    with open(os.path.join(os.path.dirname(__file__), "strategy", "__init__.py"), "r") as f:
        content = f.read()
        if "__all__" not in content:
            print("__all__ = [] does not exist. Creating one...")
        # 4.2 THIS CODE BLOCK HANDLES THE CASE WHEN THE FILE IS IN THE FOLDER BUT NOT IN __all__
            unregistered_strategies = []
            for strategy in os.listdir(os.path.join(os.path.dirname(__file__), "strategy")):
                strategy = strategy.split(".py")[0]
                if strategy != "" and strategy[0] != "." and strategy[0] != "_":
                    # print with green color to emphasize registration
                    print("\033[92m" + f"Successfully registered {strategy} strategy." + "\033[0m")
                    unregistered_strategies.append(strategy.split(".")[0])

            with open(os.path.join(os.path.dirname(__file__), "strategy", "__init__.py"), "w") as f:
                f.write("__all__ = {}".format(unregistered_strategies))
        else:
        # 4.1 THIS CODE BLOCK HANDLES THE CASE WHEN THE FILE IS IN __all__ BUT NOT IN THE FOLDER
            uncreated_strategies = []
            all_content = content.split("=")[1].split("[")[1].split("]")[0].split(",") if eval(content.split("=")[1]) != [] else []
            all_content = [strategy.strip() for strategy in all_content]
            all_content = [strategy.replace("'", "") for strategy in all_content]
            for strategy in all_content:
                if strategy != "":
                    if not os.path.exists(os.path.join(os.path.dirname(__file__), "strategy", f"{strategy}.py")):
                        # Print with green
                        uncreated_strategies.append(strategy)
            # Register those strategies
            if len(uncreated_strategies) > 0:
                print(f"{uncreated_strategies} are not created. Creating templates...")
                for strategy in uncreated_strategies:
                    with open(os.path.join(os.path.dirname(__file__), "strategy", f"{strategy}.py"), "w") as f:
                        print("\033[92m" + f"Successfully template created {strategy} strategy." + "\033[0m")
                        f.write(create_template(strategy))
        # 4.2 THIS CODE BLOCK HANDLES THE CASE WHEN THE FILE IS IN THE FOLDER BUT NOT IN __all__
            unregistered_strategies = []
            for strategy in os.listdir(os.path.join(os.path.dirname(__file__), "strategy")):
                if strategy == ".DS_Store":
                    continue
                strategy = strategy.split(".py")[0]
                if strategy != "" and strategy[0] != "." and strategy[0] != "_" and strategy.split(".")[0] not in all_content and strategy.isidentifier():
                    # print with green color to emphasize registration
                    print("\033[92m" + f"Successfully registered {strategy} strategy." + "\033[0m")
                    unregistered_strategies.append(strategy.split(".")[0])
            # Get all the strategies
            total_strategies = os.listdir(os.path.join(os.path.dirname(__file__), "strategy"))
            total_strategies = [strategy.split(".")[0] for strategy in total_strategies if strategy[0] != "_"]
            # Register those strategies
            if len(unregistered_strategies) > 0:
                logger.error(f"{unregistered_strategies} are not registered. Registering...")
                register_init(total_strategies)
                logger.info(f"{unregistered_strategies} are registered.")

    check_all_list()


