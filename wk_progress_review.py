import requests
import os
import sys
import json
import datetime
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plot
from pprint import pprint

WK_URL = "https://api.wanikani.com/v2/"
AK_FILENAME = "wk_apikey.txt"
datetime_string_format = "%Y-%m-%dT%H:%M:%S.%fZ"
VERBOSE = True
REFRESH = False

def vprint(string):
    if VERBOSE:
        print(string)


def create_store():
    if "Store" not in os.listdir():
        os.mkdir("Store")
        vprint("Created Store Dir")
    else:
        vprint("Store Exists")


def collect_data(endpoint):
    endpoint_path = f"Store/{endpoint}.json"
    check_flag = os.path.exists(endpoint_path)

    if not check_flag or REFRESH:
        vprint(f"Collecting Data: {endpoint}")
        req = requests.get(f"{WK_URL}/{endpoint}", headers=AUTH_HEADER)
        if req.status_code == 200:
            with open(endpoint_path, "w") as f:
                f.write(json.dumps(req.json(),indent=2))

            level_data = req.json()
        else:
            print(req)
            print("Error collecting data")
            sys.exit(1)
            
    else:
        vprint(f"Loading File: {endpoint_path}")
        with open(endpoint_path, "r") as f:
            level_data = json.load(f)

    return level_data


def create_level_graph():
    level_data = collect_data("level_progressions")

    times = []
    for level in level_data["data"]:
        if level['data']["passed_at"] is not None:
            times.append((datetime.datetime.strptime(level['data']["started_at"], datetime_string_format), datetime.datetime.strptime(level['data']["passed_at"], datetime_string_format)))
        else:
            times.append((datetime.datetime.strptime(level['data']["started_at"], datetime_string_format), datetime.datetime.now()))
    
    diffs = [time[1] - time[0] for time in times]
    print(diffs)
    
    total_time = 0
    for i,diff in enumerate(diffs):
        if i == 0:
            total_time = diff
        else:
            total_time += diff
    avg_time = total_time/len(diffs)
    for _ in range(len(diffs),60):
        diffs.append(datetime.timedelta(seconds=0))

    
    seconds_diffs = [diff.total_seconds() for diff in diffs]

    time_data = {"Level":range(1,61),
                 "Time":seconds_diffs}
    time_df = pd.DataFrame(time_data)

    fig, ax = plot.subplots(figsize=(15,7))
    bar_plot = sns.barplot(ax=ax, data=time_df, x="Level",y="Time")

    highest = int(max(seconds_diffs))
    day = 60*60*24
    ticks = range(0,highest,day)
    tick_labels = range(0,len(ticks))
    bar_plot.set_yticks(ticks)
    bar_plot.set_yticklabels(tick_labels)

    plot.show()
    
    print(len(diffs))
    print(total_time)
    print(avg_time)

    return times
    

def main():

    with open(AK_FILENAME, "r") as f:
        apikey = f.read().strip()

    global AUTH_HEADER
    AUTH_HEADER = {"Authorization":f"Bearer {apikey}"}

    create_store()

    create_level_graph()


if __name__ == "__main__":
    main()