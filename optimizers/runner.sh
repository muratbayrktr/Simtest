#!/bin/bash

# Example usage of the given command with various types and shell tricks

# Empty results folder
python archive.py -y

# Usage 1: Basic usage
python src/main.py -s FibonacciRetracements -e binance -m futures -t 1h -b 2021-10-22 -ed 2023-10-22 -p BTCUSDT -sl 100;
python src/main.py -s FibonacciRetracements -e binance -m futures -t 1h -b 2021-10-22 -ed 2023-10-22 -p BTCUSDT -sl 0.1;
python src/main.py -s FibonacciRetracements -e binance -m futures -t 1h -b 2021-10-22 -ed 2023-10-22 -p BTCUSDT -sl 0.3;
python src/main.py -s FibonacciRetracements -e binance -m futures -t 1h -b 2021-10-22 -ed 2023-10-22 -p BTCUSDT -sl 0.5;
python src/main.py -s FibonacciRetracements -e binance -m futures -t 1h -b 2021-10-22 -ed 2023-10-22 -p BTCUSDT -sl 0.7;
python src/main.py -s FibonacciRetracements -e binance -m futures -t 1h -b 2021-10-22 -ed 2023-10-22 -p BTCUSDT -sl 1;
python src/main.py -s FibonacciRetracements -e binance -m futures -t 1h -b 2021-10-22 -ed 2023-10-22 -p BTCUSDT -sl 3;
python src/main.py -s FibonacciRetracements -e binance -m futures -t 1h -b 2021-10-22 -ed 2023-10-22 -p BTCUSDT -sl 5;
python src/main.py -s FibonacciRetracements -e binance -m futures -t 1h -b 2021-10-22 -ed 2023-10-22 -p BTCUSDT -sl 6;
python src/main.py -s FibonacciRetracements -e binance -m futures -t 1h -b 2021-10-22 -ed 2023-10-22 -p BTCUSDT -sl 7;
python src/main.py -s FibonacciRetracements -e binance -m futures -t 1h -b 2021-10-22 -ed 2023-10-22 -p BTCUSDT -sl 8;
python src/main.py -s FibonacciRetracements -e binance -m futures -t 1h -b 2021-10-22 -ed 2023-10-22 -p BTCUSDT -sl 9;
python src/main.py -s FibonacciRetracements -e binance -m futures -t 1h -b 2021-10-22 -ed 2023-10-22 -p BTCUSDT -sl 10;
python src/main.py -s FibonacciRetracements -e binance -m futures -t 1h -b 2021-10-22 -ed 2023-10-22 -p BTCUSDT -sl 12.5;
python src/main.py -s FibonacciRetracements -e binance -m futures -t 1h -b 2021-10-22 -ed 2023-10-22 -p BTCUSDT -sl 15;
python export.py;

# Make sure results empty before running these commands
# python export_csv.py;
# python src/main.py -s RSI -e binance -m futures -t 1m -b 2021-10-22 -ed 2023-10-22 -p BTCUSDT -sl 100;
# python src/main.py -s RSI -e binance -m futures -t 1m -b 2021-10-22 -ed 2023-10-22 -p BTCUSDT -sl 0.1;
# python src/main.py -s RSI -e binance -m futures -t 1m -b 2021-10-22 -ed 2023-10-22 -p BTCUSDT -sl 0.3;
# python src/main.py -s RSI -e binance -m futures -t 1m -b 2021-10-22 -ed 2023-10-22 -p BTCUSDT -sl 0.5;
# python src/main.py -s RSI -e binance -m futures -t 1m -b 2021-10-22 -ed 2023-10-22 -p BTCUSDT -sl 0.7;
# python src/main.py -s RSI -e binance -m futures -t 1m -b 2021-10-22 -ed 2023-10-22 -p BTCUSDT -sl 1;
# python src/main.py -s RSI -e binance -m futures -t 1m -b 2021-10-22 -ed 2023-10-22 -p BTCUSDT -sl 3;
# python src/main.py -s RSI -e binance -m futures -t 1m -b 2021-10-22 -ed 2023-10-22 -p BTCUSDT -sl 5;
# python src/main.py -s RSI -e binance -m futures -t 1m -b 2021-10-22 -ed 2023-10-22 -p BTCUSDT -sl 6;
# python src/main.py -s RSI -e binance -m futures -t 1m -b 2021-10-22 -ed 2023-10-22 -p BTCUSDT -sl 7;
# python src/main.py -s RSI -e binance -m futures -t 1m -b 2021-10-22 -ed 2023-10-22 -p BTCUSDT -sl 8;
# python src/main.py -s RSI -e binance -m futures -t 1m -b 2021-10-22 -ed 2023-10-22 -p BTCUSDT -sl 9;
# python src/main.py -s RSI -e binance -m futures -t 1m -b 2021-10-22 -ed 2023-10-22 -p BTCUSDT -sl 10;
# python src/main.py -s RSI -e binance -m futures -t 1m -b 2021-10-22 -ed 2023-10-22 -p BTCUSDT -sl 12.5;
# python src/main.py -s RSI -e binance -m futures -t 1m -b 2021-10-22 -ed 2023-10-22 -p BTCUSDT -sl 15;
# python export_csv.py;


# Usage 2: Using variables for arguments
# symbol="BTCUSDT"
# strategy="FibonacciRetracements"
# exchange="binance"
# market="futures"
# timeframe="1h"
# start_date="2023-06-01"
# end_date="2023-06-07"
# python src/main.py -s $strategy -e $exchange -m $market -t $timeframe -b $start_date -ed $end_date -p $symbol

# # Usage 3: Example usage for iterating over parameters with for loops, predefine possible values in arrays EQUAL LENGTH ARRAYS
# symbols=("BTCUSDT" "ETHUSDT" "BNBUSDT")
# strategies=("FibonacciRetracements" "FibonacciRetracements" "FibonacciRetracements")
# # Only binance futures, binance spot and bybit futures supported for now
# exchanges=("binance" "binance" "bybit")
# markets=("futures" "spot" "futures")
# timeframes=("1h" "1h" "1h")
# start_dates=("2023-06-01" "2023-06-01" "2023-06-01")
# end_dates=("2023-06-07" "2023-06-07" "2023-06-07")
# for i in "${!symbols[@]}"; do
#     python src/main.py -s ${strategies[$i]} -e ${exchanges[$i]} -m ${markets[$i]} -t ${timeframes[$i]} -b ${start_dates[$i]} -ed ${end_dates[$i]} -p ${symbols[$i]}
# done

# # Usage 4: Example usage for iterating over nested parameters with for loops, predefine possible values in arrays 

# symbols=("BTCUSDT" "ETHUSDT" "BNBUSDT")

# # 5 nested loops: symbols, strategies, exchange & markets, timeframes, start & end dates
# for i in "${!symbols[@]}"; do
#     for j in "${!strategies[@]}"; do
#         for k in "${!exchanges[@]}"; do
#             for l in "${!timeframes[@]}"; do
#                 for m in "${!start_dates[@]}"; do
#                     python src/main.py -s ${strategies[$j]} -e ${exchanges[$k]} -m ${markets[$k]} -t ${timeframes[$l]} -b ${start_dates[$m]} -ed ${end_dates[$m]} -p ${symbols[$i]}
#                 done
#             done
#         done
#     done
# done
# ```
