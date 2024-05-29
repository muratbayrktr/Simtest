# DO NOT CHANGE BELOW LINES
##########################################################################################

# Print working directory
pwd;
# Only binance futures, binance spot and bybit futures supported for now
exchanges="binance"
markets="futures"
# For each exchange & market run for below timeframes
timeframes="5m"
# For each time frame run for below dates
start_dates="2021-10-22"
end_dates="2023-10-22"
##########################################################################################
# CHANGE BELOW LINES
##########################################################################################
# DEFINE THE STRATEGY TO BE TESTED
strategies="rsi_fib_short"
# For each exchange & market run for below symbols
symbols=("HBARUSDT" "BTCUSDT")
##########################################################################################
position_sizes=(1 0.001)
# CHANGE BELOW LINES 
##########################################################################################
# Range from 70 to 90 with 1 increments
stop_loss_range=(None  10 11 12 13 14 15 16 17 18 19 20 )
take_profit_range=(None 5 6 7 8 9 10 11 12.5 14 15 17 20 30)
##########################################################################################
# ... you can fix your parameters here
# i.e. model_parameter_1_range = (70)
# then the loop below will only run for model_parameter_1 = 70
# 
##########################################################################################


# DO NOT CHANGE BELOW LINES
##########################################################################################
python archive.py -y;

total=$((${#stop_loss_range[@]} * ${#take_profit_range[@]} * ${#symbols[@]}))
count=0

for i in "${!symbols[@]}"; do
    symbol=${symbols[i]}
    for s in "${!stop_loss_range[@]}"; do
        for t in "${!take_profit_range[@]}"; do
            # Add more for loops here if you want to test more parameters
            # i.e. for u in "${!model_parameter_2_range[@]}"; do
            # then add -mp "model_parameter_2 ${model_parameter_2_range[u]}";
            ((count++))
            echo "Running simulation [$count] of [$total]"
            # Stop loss and take profit
            stop_loss=${stop_loss_range[s]}
            take_profit=${take_profit_range[t]}
            pos_size=${position_sizes[i]}
            

            # Run the script
            python src/main.py -s ${strategies} -e ${exchanges} -m ${markets} \
                -t ${timeframes} -b ${start_dates} -ed ${end_dates} -p ${symbol} \
                -mp "stop_loss ${stop_loss} take_profit ${take_profit} position_size ${pos_size}" > /dev/null 2>&1;
        done
    done
done | pv -l -s $total > /dev/null
python export.py;
##########################################################################################
