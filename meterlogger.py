import requests
import json
from concurrent.futures import ThreadPoolExecutor
import time
from pathlib import Path
import random

# filepath = "meter_data/readings-feb-08-0031.json"
directory = "meter_data"
meterfiles = Path(directory).glob("readings*")

for i in meterfiles:
    print(i)

APIURL = "http://localhost:5000/meter"
APIURL2GETREADINGS = "http://localhost:5000/getmeterdata"

def packetreader(packet):
    response = requests.post(APIURL, json = packet)
    print(response.text, "| Status Code:", response.status_code)
    time.sleep((random.randrange(1, 5)/10))

if __name__ == "__main__":
    filecounter = 0

    for filepath in meterfiles:
        with open(filepath) as f:
            jsonfile = json.load(f)
            reading_list = jsonfile["readings"]
            with ThreadPoolExecutor(max_workers = 8) as executor:
                futures = [executor.submit(packetreader, i) for i in reading_list]
        filecounter += 1
        print(f"Readings for {filepath} all uploaded, this is file {filecounter}")
        time.sleep(5)

    response2 = requests.get(APIURL2GETREADINGS)
    print(response2.text)