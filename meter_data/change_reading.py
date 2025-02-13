import json
from datetime import datetime, timedelta
import random


def load_initial_readings(filename):
    """Load the initial readings from a JSON file."""
    with open(filename, "r") as f:
        data = json.load(f)
        print(data)
    return data["readings"]


df = load_initial_readings("./readings-feb-08.json")
print(df)
for i in df:
    i["reading_kWh"] = 0.0
print(df)
output_data = {"readings": df}
with open("readings-feb-08.json", "w") as f:
    json.dump(output_data, f, indent=2)
