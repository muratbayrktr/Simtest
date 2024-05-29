#!/bin/bash


# Empty results folder
python archive.py -y

# Usage 1: Basic usage
python src/main.py -s roc_rsi -e binance -m futures -t 30m -b 2021-10-22 -ed 2023-10-22 -p LTCUSDT -mp "th1 35 th2 53 max_open_pos 1 stop_loss 6 take_profit 12.5";
python src/main.py -s roc_rsi -e binance -m futures -t 30m -b 2021-10-22 -ed 2023-10-22 -p LTCUSDT -mp "th1 35 th2 53 max_open_pos 1 stop_loss 7 take_profit 12.5";
python src/main.py -s roc_rsi -e binance -m futures -t 30m -b 2021-10-22 -ed 2023-10-22 -p LTCUSDT -mp "th1 35 th2 53 max_open_pos 30 stop_loss 6 take_profit 12.5";
python src/main.py -s roc_rsi -e binance -m futures -t 30m -b 2021-10-22 -ed 2023-10-22 -p LTCUSDT -mp "th1 35 th2 53 max_open_pos 30 stop_loss 7 take_profit 12.5";
python export.py;

# RSI ROC BTCUSDT
python archive.py -y;
python src/main.py -s roc_rsi -e binance -m futures -t 1h -b 2021-10-22 -ed 2023-10-22 -p BTCUSDT -mp "th1 35 th2 53 max_open_pos 1 stop_loss 6 take_profit 12.5";
python src/main.py -s roc_rsi -e binance -m futures -t 1h -b 2021-10-22 -ed 2023-10-22 -p BTCUSDT -mp "th1 35 th2 53 max_open_pos 1 stop_loss 7 take_profit 12.5";
python src/main.py -s roc_rsi -e binance -m futures -t 1h -b 2021-10-22 -ed 2023-10-22 -p BTCUSDT -mp "th1 35 th2 53 max_open_pos 30 stop_loss 6 take_profit 12.5";
python src/main.py -s roc_rsi -e binance -m futures -t 1h -b 2021-10-22 -ed 2023-10-22 -p BTCUSDT -mp "th1 35 th2 53 max_open_pos 30 stop_loss 7 take_profit 12.5";
python export.py;