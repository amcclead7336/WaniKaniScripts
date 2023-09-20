import requests
import os
import sys
import json
import datetime
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


def collect_data(endpoint, AUTH_HEADER):
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


def main():

    with open(AK_FILENAME, "r") as f:
        apikey = f.read().strip()

    AUTH_HEADER = {"Authorization":f"Bearer {apikey}"}

    create_store()

    level_data = collect_data("level_progressions", AUTH_HEADER)
    
    # vprint(req)
    pprint(level_data)


if __name__ == "__main__":
    main()