# DO NOT CHANGE BELOW LINES
##########################################################################################
# Only binance futures, binance spot and bybit futures supported for now
exchanges="binance"
markets="futures"
# For each exchange & market run for below timeframes
timeframes="1h"
# For each time frame run for below dates
start_dates="2024-01-01"
end_dates="2024-04-01"
##########################################################################################


# CHANGE BELOW LINES
##########################################################################################
# DEFINE THE STRATEGY TO BE TESTED
strategies="trima_fib"
# For each exchange & market run for below symbols
symbols=("BTCUSDT")
##########################################################################################

# CHANGE BELOW LINES 
##########################################################################################
# ... you can fix your parameters here
# i.e. model_parameter_1_range = (70)
# then the loop below will only run for model_parameter_1 = 70
# 
# rsi threshold starts from 10 up to 30 with 2 increments
threshold1_range=(50 60 70) # 9
threshold2_range=(336) # 11

# Timeperiod of RSI, MFI
max_open_pos_range=(None 1 5)
# total 11 * 9 * 7 = 693 simulations
stop_loss_range=(None 10 30)
take_profit_range=(None 10 30)
##########################################################################################


# DO NOT CHANGE BELOW LINES
##########################################################################################
python archive.py -y;

total=$((${#threshold1_range[@]} * ${#max_open_pos_range[@]} * ${#stop_loss_range[@]} * ${#take_profit_range[@]} * ${#symbols[@]}))
count=0

echo "Total simulations: $total"
echo "Starting simulations...";
for b in "${!symbols[@]}"; do
    symbol=${symbols[b]}
    for s in "${!threshold1_range[@]}"; do
        for u in "${!max_open_pos_range[@]}"; do
            for sl in "${!stop_loss_range[@]}"; do
                for tp in "${!take_profit_range[@]}"; do

                    # Add more for loops here if you want to test more parameters
                    # i.e. for u in "${!model_parameter_2_range[@]}"; do
                    # then add -mp "model_parameter_2 ${model_parameter_2_range[u]}";
                    ((count++))
                    echo "Running simulation [$count] of [$total]"
                    # Set your parameters here
                    th1=${threshold1_range[s]}
                    th2=${threshold2_range[t]}
                    max_open_pos=${max_open_pos_range[u]}
                    
                    # Stop loss and take profit
                    stop_loss=${stop_loss_range[sl]}
                    take_profit=${take_profit_range[tp]}

                    # Run the script
                    python src/main.py -s ${strategies} -e ${exchanges} -m ${markets} \
                    -t ${timeframes} -b ${start_dates} -ed ${end_dates} -p ${symbol} \
                    -mp "timeperiod ${th1} length ${th2} max_open_pos ${max_open_pos}  stop_loss ${stop_loss} take_profit ${take_profit}" > /dev/null 2>&1;
                done
            done
        done
    done
done | pv -l -s $total > /dev/null
python export.py;
##########################################################################################
