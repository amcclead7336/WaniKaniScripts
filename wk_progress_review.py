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
# VERBOSE = True
# REFRESH = False

def vprint(string):
    if VERBOSE:
        print(string)


def create_dir(name):
    if name not in os.listdir():
        os.mkdir(name)
        vprint(f"Created {name} Dir")
    else:
        vprint(f"{name} Exists")


def collect_data(endpoint, AUTH_HEADER):
    endpoint_path = f"Store/{endpoint}.json"
    check_flag = os.path.exists(endpoint_path)

    if not check_flag or REFRESH:
        vprint(f"Collecting Data: {WK_URL}{endpoint}")
        req = requests.get(f"{WK_URL}{endpoint}", headers=AUTH_HEADER)

        if req.status_code == 200:

            level_data = req.json()

            if level_data['pages']['next_url'] is not None:
                vprint("Next url is present")
                tmp_data = requests.get(level_data['pages']['next_url'], headers=AUTH_HEADER).json()
                level_data['data'] += tmp_data['data']

                while tmp_data['pages']['next_url'] is not None:
                    tmp_data = requests.get(level_data['pages']['next_url'], headers=AUTH_HEADER)
                    level_data['data'] += tmp_data['data']


            with open(endpoint_path, "w") as f:
                f.write(json.dumps(level_data,indent=2))

        else:
            print(req)
            print("Error collecting data")
            sys.exit(1)
            
    else:
        vprint(f"Loading File: {endpoint_path}")
        with open(endpoint_path, "r") as f:
            level_data = json.load(f)

    return level_data


def collect_level_data(AUTH_HEADER):
    level_data = collect_data("level_progressions", AUTH_HEADER)

    times = []
    for level in level_data["data"]:
        if level['data']["passed_at"] is not None:
            times.append((datetime.datetime.strptime(level['data']["started_at"], DATETIME_STRING_FORMAT), datetime.datetime.strptime(level['data']["passed_at"], DATETIME_STRING_FORMAT)))
        else:
            times.append((datetime.datetime.strptime(level['data']["started_at"], DATETIME_STRING_FORMAT), datetime.datetime.now()))
    
    diffs = [time[1] - time[0] for time in times]

    
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

    return time_df.copy(), avg_time


def collect_progress_data(AUTH_HEADER):

    assignment_data = collect_data("assignments", AUTH_HEADER)

    df_list = []

    for lesson_type in ("radical", "kanji", "vocabulary"):

        df_list.append(pd.DataFrame({"Passed_times": [assignment['data']['passed_at'] for assignment in assignment_data['data'] if assignment['data']['subject_type'] == lesson_type] }))
        
    rows_out = []

    for subject_type, df in zip(("radical","kanji","vocab"), df_list):
        df["Passed_times"] = pd.to_datetime(df["Passed_times"])
        tmp_df = df.groupby([df["Passed_times"].dt.date]).count()["Passed_times"]
        tmp_series = tmp_df.cumsum()
        df_count_cumsum = pd.concat({"count":tmp_df, "cumsum":tmp_series}, axis=1)


        for index, row in df_count_cumsum.iterrows():
            rows_out.append([index,row["count"],row['cumsum'],subject_type])

    out_df = pd.DataFrame(rows_out, columns=['Date','count','CumSum','Subject'])
    out_df["Date"] = pd.to_datetime(out_df["Date"])

    total_series = out_df.sort_values("Date").groupby("Date").sum()["count"].cumsum()

    return out_df.copy(), total_series.copy()


def create_level_lines():

    with open("Store/level_progressions.json") as f:
        level_prgressions = json.load(f)

    vlines=[]
    for _,level in enumerate(level_prgressions['data']):
        if level["data"]["passed_at"] is not None:
            vlines.append({"x": level["data"]["passed_at"], "line_dash":"dot"})
    
    return vlines.copy()


def create_gantt_data(AUTH_HEADER):

    current_time = datetime.datetime.now()
    rad_data = collect_data("assignments?levels=5&subject_types=radical",AUTH_HEADER)
    kanji_data = collect_data("assignments?levels=5&subject_types=kanji",AUTH_HEADER)
    srs_interval_data = collect_data("spaced_repetition_systems?ids=1",AUTH_HEADER)
    subject_data = collect_data("subjects?levels=5&types=radical,kanji",AUTH_HEADER)

    interval_dict = {stage['position']: datetime.timedelta(days=0,seconds=stage['interval']) for stage in srs_interval_data['data'][0]['data']['stages'][1:6]}
    subject_id_slug_dict = {sub['id']: sub['data']['slug'] for sub in subject_data['data']}

    rad_out_list = []
    kanji_out_list = []
    for out_list, data_set in zip([rad_out_list, kanji_out_list],[rad_data,kanji_data]):
        for subject in data_set['data']:
            color = "Blue"
            if not subject['data'].get("passed_at") and subject['data'].get('available_at'):
                available_at_time = datetime.datetime.strptime(subject['data']['available_at'], DATETIME_STRING_FORMAT)
                if available_at_time < current_time:
                    color = "Green"
                    available_at_time = current_time

                subject_id = subject['data']['subject_id']
                subject_name = subject_id_slug_dict[subject_id]
                srs_stage = subject['data']['srs_stage']
                finish_time = available_at_time + interval_dict[srs_stage]

                out_list.append(dict(Task=f"SRS {srs_stage}",Start=available_at_time,Finish=finish_time,Resource=subject_name,Color=color))

                if srs_stage < 4:
                    for i in range(srs_stage+1, 5):
                        available_at_time = finish_time
                        finish_time = available_at_time + interval_dict[i]
                        out_list.append(dict(Task=f"SRS {i}",Start=available_at_time,Finish=finish_time,Resource=subject_name,Color="Blue"))

    r_df = pd.DataFrame(rad_out_list)
    k_df = pd.DataFrame(kanji_out_list)

    r_df = r_df.sort_values("Start", ascending=False)
    k_df = k_df.sort_values("Start", ascending=False)
    return r_df, k_df