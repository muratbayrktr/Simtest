# DO NOT CHANGE BELOW LINES
##########################################################################################
# Only binance futures, binance spot and bybit futures supported for now
exchanges="binance"
markets="futures"

# For each time frame run for below dates
start_dates="2021-10-22"
end_dates="2023-10-22"
##########################################################################################


# CHANGE BELOW LINES
# The number of backtests will be equal to the product of the number of elements in each array
# i.e. for 3 algorithms, 4 timeframes and 3 symbols, the number of backtests will be 3*4*3 = 36
##########################################################################################
# DEFINE THE STRATEGY TO BE TESTED
strategies=("FibonacciRetracements") # ADD MORE HERE If you want
# For each exchange & market run for below timeframes
timeframes=("1h") # ADD MORE HERE If you want
# For each exchange & market run for below symbols
symbols=("XLMUSDT" "UNIUSDT" "SOLUSDT" ) # ADD MORE HERE
##########################################################################################


# DO NOT CHANGE BELOW LINES
##########################################################################################
python archive.py -y;
for s in "${!strategies[@]}"; do
    for t in "${!timeframes[@]}"; do
        for u in "${!symbols[@]}"; do
            # Add more for loops here if you want to test more parameters
            # i.e. for u in "${!model_parameter_2_range[@]}"; do
            # then add -mp "model_parameter_2 ${model_parameter_2_range[u]}";

            # Set your parameters here
            strategy = strategies[s];
            timeframe = timeframes[t]; 
            symbol = symbols[u];

            # Run the script
            python src/main.py -s ${strategy} -e ${exchanges} -m ${markets} \
                -t ${timeframe} -b ${start_dates} -ed ${end_dates} -p ${symbol};
        done
    done
done
python export_csv.py;
##########################################################################################