import requests
apikey_filename = "wk_apikey.txt"

with open(apikey_filename, "r") as f:
    apikey = f.read().strip()

print(apikey)