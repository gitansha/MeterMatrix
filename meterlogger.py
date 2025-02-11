import requests
import json

filepath = "meter_data/readings-feb-08-0031.json"
APIURL = "http://localhost:5000/meter"

with open(filepath) as f:
    jsonfile = json.load(f)
    reading_list = jsonfile["readings"]
    for packet in reading_list:
        response = requests.post(APIURL, json = packet)
        print(response.text, "| Status Code:", response.status_code)