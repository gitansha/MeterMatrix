import requests
import json
from concurrent.futures import ProcessPoolExecutor
import time
from pathlib import Path
import random

directory = "meter_data"
meterfiles = sorted(Path(directory).glob("readings*"))

for i in meterfiles:
    print(i)

APIURL = "http://localhost:5000/meter"
APIURL2GETREADINGS = "http://localhost:5000/getmeterdata"

def packetreader(packet):
    response = requests.post(APIURL, json = packet)
    while response.status_code == 201:
        time.sleep(0.5)
        response = requests.post(APIURL, json = packet)
    print(response.text, "| Status Code:", response.status_code)
    time.sleep((random.randrange(1, 5)/10))

if __name__ == "__main__":
    filecounter = 0

    for filepath in meterfiles:
        with open(filepath) as f:
            jsonfile = json.load(f)
            reading_list = jsonfile["readings"]
            with ProcessPoolExecutor(max_workers = 8) as executor:
                futures = [executor.submit(packetreader, i) for i in reading_list]
        filecounter += 1
        print(f"Readings for {filepath} all uploaded, this is file {filecounter}")
        time.sleep(5) # Simulates 1/2 hour sending

    response2 = requests.get(APIURL2GETREADINGS)
    print(response2.text)

    for i in response2.text:
        print(len(i))