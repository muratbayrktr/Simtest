# SimTest

## Project Overview


![Dashboard](./src/assets/dashboard.png?raw=true "An Example of the Dashboard")

SimTest is a Python-based simulation and testing interface designed for Algo-Research Projects (ARPs) in the field of trading strategies. The objective of this project is to create a comprehensive testing environment for ARPs, enabling thorough evaluation and analysis under various market conditions. SimTest provides simulation capabilities, backtesting functionalities, and a suite of metrics to assess the performance and effectiveness of trading strategies.   
 
![Dashboard](./src/assets/sample_run.png?raw=true "An Example Strategy SimTest")

SimTest contains a very nice module for calculating metrics for the tested strategy. TradingMetrics module enables test various results of the strategy. The module also makes suggestions on leverage and stop loss along with useful information like Maximum Unrealized Loss and Dynamic Maximum Loss Percentage calculation depending on the risk-reward-ratio of the strategy.    

![Dashboard](./src/assets/tradingmetrics.png?raw=true "TradingMetrics")


When registering a strategy, you can run *register* code to register your strategy with a template. This is strongly suggested because it registers your strategy with the default parameters. You can also register your strategy without the template. In this case, you have to provide the parameters for your strategy. Run register.py:
   
   ```bash
   python3 register.py
   ```

![Dashboard](./src/assets/register_code.png?raw=true "Register")

You will be prompted to enter the name of your strategy. Then if name is suitable your code will be generated and will be integrated such that it can be readable by the _SimTest_.

![Dashboard](./src/assets/template_strategy.png?raw=true "Template")


## Project Hierarchy

```
SimTest/
├── data/
│   ├── raw/
│   ├── generated/
│   └── processed/
src
    ├── assets
    │   └── style.css
    ├── _backtester.py
    ├── _base_socket.py
    ├── _base_strategy.py
    ├── _callbacks.py
    ├── data_ingestion
    │   ├── binance.py
    │   ├── coinglass.py
    │   └── okx.py
    ├── _logger.py
    ├── main.py
    ├── _metrics.py
    ├── _montecarlo.py
    ├── _orders.py
    ├── report.py
    ├── _reports.py
    ├── _scenario.py
    ├── _simulator.py
    ├── strategy
    │   ├── bol.py
    │   ├── ema_enhanced.py
    │   ├── ema.py
    │   ├── __init__.py
    │   ├── supertrend.py
    │   ├── volaware.py
    │   ├── yrsi.py
    │   ├── yrsi_v2.py
    │   ├── yrsi_v3.py
    │   └── yrsi_v4.py
    ├── testing_and_qa
    │   ├── ipc_simulator_unit_test.py
    │   ├── ipc_unit_test.py
    │   ├── lev_unit_test.py
    │   ├── metrics_unit_test.ipynb
    │   ├── _montecarlo.py
    │   └── simulation_unit_test.ipynb
    └── _utils.py
└── README.md
```

## Project Structure

The project directory is structured as follows:

- **data/**: This directory contains subdirectories for raw, generated, and processed data used in the simulation and testing process.  

  - **raw/**: This directory contains the raw data used in the simulation and testing process.  

  - **generated/**: This directory contains the generated data used in the simulation and testing process.   

  - **processed/**: This directory contains the processed data used in the simulation and testing process.  

- **results/**: This directory contains the results of the simulation and testing process, including reports, metrics, and other relevant data.  

- **logs/**: This directory contains the log files generated during the simulation and testing process.  

- **archive/**: This directory contains the archived files of the project.   

- **src/**: The source directory contains the core implementation of the SimTest project. It is organized into various modules and subdirectories, including data ingestion, socket programming, interprocess communication, metrics library, backtesting, simulation, data generation, scenario implementations, report generation, and testing/quality assurance.  

- **README.md**: This file serves as the main project readme, providing an overview of the project and its structure.  

## Getting Started

To get started with SimTest, follow the instructions below:

1. Clone the project repository from GitHub: [repository URL]

2. Install the required dependencies and libraries listed in the project documentation. It is STRONGLY recommended to use a virtual environment for this purpose. Make sure conda is installed on your system. Then, create a new virtual environment using the following command:  

   ```bash
   conda env create --file environment.yml
   ```

   Activate the virtual environment using the following command:  

   ```bash
   conda activate simtest
   ```

   Install the required dependencies that should be downloaded from pypi using the following command:  

   ```bash
   pip install dash wget
   ```

3. Make sure you have the required packages and libraries installed. You can check the required packages and libraries from the spec-file.txt file.

4. Customize the project to meet your specific requirements, such as integrating your own trading strategies or adjusting simulation parameters. You have to register your strategies under the strategies/ folder. First, create a python script for your strategy. Then, import the strategy class from the base_strategy.py file and inherit from it. Finally, implement the required methods for your strategy. You can refer to the existing strategies for examples. To register your strategy, you have the append this strategy to the all strategies list in the strategies/__init__.py file by simply omitting the .py extension.  

5. Run the main script to start the simulation and testing process. The main script is located in the src/ directory. You can run the script using the following command while under the SimTest directory:  

   ```bash
   python3 src/main.py
   ```

6. SimTest Dashboard: To be able see the results under the results/ folder you have to run the dashboard. The dashboard is a web application that is built using Dash. To run the dashboard, you have to run the following command while under the SimTest directory:  

   ```bash
   python3 src/report.py
   ```

   This will open the server for the dashboard. You can either visit the dashboard by visiting the following URL: http://127.0.0.1:8050/ or by clicking on the link that will be printed in the terminal. OR you can run the main.py script on a separate terminal and the dashboard on a separate terminal. This will allow you to see the results in real-time.  
 
 

7. Refer to the project documentation for detailed information on how to run the simulations, perform backtesting, generate reports, and interpret the results.  


## Contribution Guidelines
  
Contributions to SimTest are welcome! If you would like to contribute to the project, please follow these guidelines:

- Fork the repository and create a new branch for your feature or bug fix.

- Ensure your code adheres to the project's coding style and best practices.

- Write unit tests for your code, covering major functionalities and edge cases.

- Submit a pull request to the main repository, clearly describing the changes you have made.

- Your pull request will be reviewed by the project maintainers, and any necessary feedback or adjustments will be provided.


## License

SimTest is licensed under the

 [GNU Public License](LICENSE), allowing free usage, modification, and distribution of the codebase. Please review the license file for complete details.

## Contact

If you have any questions, suggestions, or feedback regarding SimTest, please contact the project team. We appreciate your interest in the project and look forward to hearing from you.

**Disclaimer**: SimTest is a research and testing tool, and its results should not be considered as financial advice. Always exercise caution and conduct thorough analysis before making any trading or investment decisions.