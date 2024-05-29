import os 
import json 
import re
from datetime import datetime
# Sample paths: SimTest/results/BinanceFutures/FibonacciRetracements/*/*/results.json
#               SimTest/results/BinanceFutures/*
REGEX_PATTERN = ".* Saving results to .*\/simtest-(.*)\/"

def fetch_logs():
    logs = {}
    for root, dirs, files in os.walk("log"):
        for file in files:
            if file.endswith(".log"):
                with open(os.path.join(root, file), "r") as f:
                    # Read first line
                    lines = f.readlines()
                    log_line = lines[1]
                    if "Model kwargs: " not in log_line:
                        print("Model kwargs not found in log file")
                    model_kwargs = log_line.split("Model kwargs: ")[-1]
                    alg_name = file.split("-")[0]
                    # Get date from log file
                    date = None    
                    for line in lines:
                        if "Saving results to" in line:
                            date = re.match(REGEX_PATTERN, line).group(1)
                            break
                    # print(date)
                    logs[date] = model_kwargs.replace("\n", "").replace(",", ' ')
    return logs


def get_csv_paths():
    csv_paths = []
    for root, dirs, files in os.walk("results"):
        for file in files:
            if file.endswith(".json"):
                csv_paths.append(os.path.join(root, file))
    return csv_paths

def generate_csv(csv_paths):
    data_list = []
    logs = fetch_logs()
    for csv_path in csv_paths:
        with open(csv_path, "r") as f:
            data = json.load(f)
            # path_spl = csv_path.split("/")
            # pair = path_spl[-2].split("_")[2]
            alg_name = csv_path.split("/")[-4]
            # time_stamp = path_spl[-2].split(f"{pair}_")[-1]
            simtest_date = csv_path.split("/")[-3].split("simtest-")[-1]
            # print(logs[simtest_date])
            data["name"] = alg_name
            kwargs = logs[simtest_date]
            # for key, value in kwargs.items():
            #     data[key] = value)
            data["kwargs"] = kwargs
            data["full_path"] = csv_path
            data_list.append(data)

    return data_list

def get_csv_row(data):
    values = []
    keys = list(data.keys())
    keys.insert(0, "name")
    for key, value in data.items():
        if type(value) not in [int, float, str]:
            values.append(str(value))
        elif type(value) == float:
            values.append(str(round(value, 5)))
        else:
            values.append(str(value))
    values.insert(0, data["name"])
    return keys, values

def main():
    csv_paths = get_csv_paths()
    data_list = generate_csv(csv_paths)
    keys_written = False
    date = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    # For each record, write values comma seperated
    save_path = os.path.join("csv", f"results-{date}.csv")
    if not os.path.exists("csv"):
        os.mkdir("csv")
    print("Results saved to: ", save_path)
    with open(save_path, "w") as f:
        for data in data_list:
            keys, values = get_csv_row(data)
            if not keys_written:
                keys_written = True
                f.write(",".join(keys))
                f.write("\n")
                # print(",".join(keys))
            f.write(",".join(values))
            f.write("\n")
            # print(values)
            # print(",".join(values))
    return save_path


if __name__ == "__main__":
    main()