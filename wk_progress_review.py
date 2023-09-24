import requests
import os
import sys
import json
import datetime
import pandas as pd

WK_URL = "https://api.wanikani.com/v2/"
DATETIME_STRING_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
VERBOSE = False if os.environ["VERBOSE"] == "False" else True
REFRESH = False if os.environ["REFRESH_DATA"] == "False" else True

def vprint(string):
    if VERBOSE:
        print(string)


def create_dir(name):
    if name not in os.listdir():
        os.mkdir(name)
        vprint(f"Created {name} Dir")
    else:
        vprint(f"{name} Exists")


def collect_data(endpoint):
    endpoint_path = f"Store/{endpoint}.json"
    check_flag = os.path.exists(endpoint_path)

    if not check_flag or REFRESH:
        vprint(f"Collecting Data: {endpoint}")
        req = requests.get(f"{WK_URL}/{endpoint}", headers=AUTH_HEADER)

        if req.status_code == 200:

            level_data = req.json()

            if level_data['pages']['next_url'] is not None:
                vprint("Next url is present")
                tmp_data = requests.get(level_data['pages']['next_url'], headers=AUTH_HEADER)
                level_data['data'] += tmp_data['data']

                while tmp_data['pages']['next_url'] is not None:
                    tmp_data = requests.get(level_data['pages']['next_url'], headers=AUTH_HEADER)
                    level_data['data'] += tmp_data['data']


            with open(endpoint_path, "w") as f:
                f.write(json.dumps(req.json(),indent=2))

        else:
            print(req)
            print("Error collecting data")
            sys.exit(1)
            
    else:
        vprint(f"Loading File: {endpoint_path}")
        with open(endpoint_path, "r") as f:
            level_data = json.load(f)

    return level_data


def create_level_data():
    level_data = collect_data("level_progressions")

    times = []
    for level in level_data["data"]:
        if level['data']["passed_at"] is not None:
            times.append((datetime.datetime.strptime(level['data']["started_at"], DATETIME_STRING_FORMAT), datetime.datetime.strptime(level['data']["passed_at"], DATETIME_STRING_FORMAT)))
        else:
            times.append((datetime.datetime.strptime(level['data']["started_at"], DATETIME_STRING_FORMAT), datetime.datetime.now()))
    
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
                 "Time_seconds":seconds_diffs}
    time_df = pd.DataFrame(time_data)

    time_df.to_csv("Data/level_data.csv", index=False)

    # _, ax = plot.subplots(figsize=(15,7))
    # bar_plot = sns.barplot(ax=ax, data=time_df, x="Level",y="Time")

    # highest = int(max(seconds_diffs))
    # day = 60*60*24
    # ticks = range(0,highest,day)
    # tick_labels = range(0,len(ticks))
    # bar_plot.set_yticks(ticks)
    # bar_plot.set_yticklabels(tick_labels)

    # plot.show()
    
    # print(len(diffs))
    # print(total_time)
    # print(avg_time)

    # return times
    

def time_collect(assignment_data, key):
    u_data = []
    s_data = []
    p_data = []

    for assignment in assignment_data['data']:
        if assignment['data']['subject_type'] == key:
            u_data.append(assignment['data']['unlocked_at'])
            s_data.append(assignment['data']['started_at'])
            p_data.append(assignment['data']['passed_at'])

    return u_data[:], s_data[:], p_data[:]



def collect_progress_data():

    assignment_data = collect_data("assignments")

    df_list = []

    for lesson_type in ("radical", "kanji", "vocabulary"):

        u_data, s_data, p_data = time_collect(assignment_data, lesson_type)

        df_list.append(pd.DataFrame({"Unlock_times":u_data,
                        "Start_times":s_data,
                        "Passed_times": p_data}))
        
    r_df = df_list[0]
    k_df = df_list[1]
    v_df = df_list[2]

    rows_out = []

    for subject_type, df in zip(("radical","kanji","vocab"),(r_df, k_df, v_df)):
        for column in df.columns:
            df[column] = pd.to_datetime(df[column])

            tmp_df =r_df.groupby([df[column].dt.date]).count()[column]
            tmp_series = tmp_df.cumsum()

            for index, row in tmp_series.items():
                rows_out.append([index,row,column,subject_type])

    out_df = pd.DataFrame(rows_out, columns=['Date','CumSum','Des','Subject'])
    out_df.to_csv("Data/progress_data.csv",index=False)


def main(apikey):

    global AUTH_HEADER
    AUTH_HEADER = {"Authorization":f"Bearer {apikey}"}

    create_dir("Store")
    create_dir("Data")

    create_level_data()

    collect_progress_data()


if __name__ == "__main__":
    pass