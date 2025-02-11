# command to run in terminal
# cd testing_data/ && python print_masterDB.py

import json

# Load the JSON file
file_path = "masterDB.json"  # Update the path if needed

with open(file_path, "r") as file:
    data = json.load(file)

# Function to print a table-like format
def print_table(headers, rows):
    col_widths = [max(len(str(item)) for item in col) for col in zip(headers, *rows)]
    row_format = " | ".join("{:<" + str(width) + "}" for width in col_widths)

    print("-" * (sum(col_widths) + 3 * (len(headers) - 1)))  # Top border
    print(row_format.format(*headers))  # Header row
    print("-" * (sum(col_widths) + 3 * (len(headers) - 1)))  # Separator
    for row in rows:
        print(row_format.format(*row))
    print("-" * (sum(col_widths) + 3 * (len(headers) - 1)))  # Bottom border

# Print meter details
meter_details = [[meter["name"], meter["meter_id"], meter["fin_no"]] for meter in data]

print("\nMeter Details:")
print_table(["Name", "Meter ID", "FIN No"], meter_details)

# Print previous day readings for each meter
for meter in data:
    prev_day_data = [[time, value] for time, value in meter["previous_day"].items()]
    print(f"\nPrevious Day Readings for {meter['name']} (Meter ID: {meter['meter_id']}):")
    print_table(["Time", "Consumption (kWh)"], prev_day_data)

# Print daily readings for the last 60 days
for meter in data:
    daily_data = [[date, value] for date, value in sorted(meter.items()) if date not in ["name", "meter_id", "fin_no", "previous_day"]]
    print(f"\nDaily Readings for {meter['name']} (Meter ID: {meter['meter_id']}):")
    print_table(["Date", "Consumption (kWh)"], daily_data)
