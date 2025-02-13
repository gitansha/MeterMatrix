import json
from datetime import datetime, timedelta
import random
import os


def load_readings(filename):
    """Load readings from a JSON file."""
    with open(filename, "r") as f:
        data = json.load(f)
    return data["readings"]


def get_previous_filename(current_time):
    """Generate the filename for the previous 30-minute interval."""
    previous_time = current_time - timedelta(minutes=30)
    time_str = previous_time.strftime("%H%M")
    return f"readings-feb-08-{time_str}.json"


def generate_reading_files(initial_readings, base_date, num_intervals=12):
    """Generate multiple JSON files with readings at 30-minute intervals."""
    current_readings = initial_readings

    # For each time interval, starting from the second interval (since we have 00:31)
    for i in range(1, num_intervals):  # Start from 1 since we already have 00:31
        # Calculate the timestamp for this interval
        current_time = base_date + timedelta(minutes=30 * i)
        timestamp = current_time.strftime("%Y-%m-%dT%H:%M:00Z")

        # Generate new readings with increments from previous readings
        new_readings = []

        # Get the previous file's readings
        previous_filename = get_previous_filename(current_time)
        try:
            current_readings = load_readings(previous_filename)
        except FileNotFoundError:
            print(f"Warning: Could not find previous file {previous_filename}")
            continue

        for reading in current_readings:
            # Add a small random increment (between 0.1 and 0.3 kWh per 30 minutes)
            increment = round(random.uniform(1, 3), 1)

            # Use the current reading as the base and add the increment
            new_reading = {
                "id": reading["id"],
                "timestamp": timestamp,
                "reading_kWh": round(reading["reading_kWh"] + increment, 1),
            }
            new_readings.append(new_reading)

        # Create the output data structure
        output_data = {"readings": new_readings}

        # Generate filename based on the timestamp
        time_str = current_time.strftime("%H%M")
        filename = f"readings-feb-08-{time_str}.json"

        # Write to file
        with open(filename, "w") as f:
            json.dump(output_data, f, indent=2)
        print(f"Generated {filename}")


def main():
    # Initial setup
    initial_file = "readings-feb-08-0031.json"
    base_date = datetime(2025, 2, 8, 0, 31, 0)  # Starting at 00:31:00

    try:
        # Load initial readings
        initial_readings = load_readings(initial_file)

        # Generate the files
        generate_reading_files(initial_readings, base_date)
        print("Successfully generated all files!")

    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
