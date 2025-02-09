import json
from datetime import datetime, timedelta
import random


def load_initial_readings(filename):
    """Load the initial readings from a JSON file."""
    with open(filename, "r") as f:
        data = json.load(f)
        print(data)
    return data["readings"]


def generate_reading_files(initial_readings, base_date, num_intervals=12):
    """Generate multiple JSON files with readings at 30-minute intervals."""

    # For each time interval
    for i in range(num_intervals):
        # Calculate the timestamp for this interval
        current_time = base_date + timedelta(minutes=30 * i)
        timestamp = current_time.strftime("%Y-%m-%dT%H:%M:00Z")

        # Generate new readings with small increments
        new_readings = []
        for reading in initial_readings:
            # Add a small random increment (between 0.1 and 0.3 kWh per 30 minutes)
            increment = round(random.uniform(0.1, 0.3), 1)
            new_reading = {
                "id": reading["id"],
                "timestamp": timestamp,
                "reading_kWh": round(reading["reading_kWh"] + (increment * i), 1),
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
    initial_file = "readings-feb-08.json"  # Your input file
    base_date = datetime(2025, 2, 8, 0, 31, 0)  # Starting at 00:31:00

    # try:
    # Load initial readings
    initial_readings = load_initial_readings("./readings-feb-08.json")

    # Generate the files
    generate_reading_files(initial_readings, base_date)

    print("Successfully generated all files!")

    # except Exception as e:
    #     print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
