############################## Imports ##############################

from flask import (
    Flask,
    jsonify,
    request,
    render_template_string,
    render_template,
    g,
    redirect,
    make_response,
)
import random
import datetime
from datetime import timedelta
import json
from pathlib import Path
import visualisation_files.management_dashboard as management_dash  # dash file
import pandas as pd
import subprocess
import platform
import multiprocessing
import sys
import time


# For testing

subprocess.check_call(
    [sys.executable, "-m", "pip", "install", "json-stream"]
)  # To install json-stream lib
import json_stream

app = Flask(__name__)

############################### Backup Codes ###########################

# Locks the thread for running a specific API only while it is being called. (/getmeterdata) for backup
# Can't get the Lock objects to work in flask. resort to global variable instead
# backuplock = multiprocessing.Lock()
# backuplock = threading.Lock()
backuplock = False


# I believe this is a github codespaces constraint as codespaces runs on 1 thread. Therefore I need to split the process out. Normally I believe the server should be able to run a batch/shell file right?
# Starts running the .bat file upon server start up, which begins the 2 hour backup cycle
def execute_backup_script():
    current_os = platform.system()

    if current_os == "Windows":
        pass
        # subprocess.run('backupper.bat', shell = True)
    else:  # Mac and Linux
        subprocess.run("./backupper.sh", shell=True)


def execute_backup_daily_script():
    current_os = platform.system()

    if current_os == "Windows":
        pass
        # subprocess.run('backupper_daily.bat', shell = True)
    else:  # Mac and Linux
        subprocess.run("./backupper_daily.sh", shell=True)


backup_process = multiprocessing.Process(target=execute_backup_script)
backup_daily_process = multiprocessing.Process(target=execute_backup_daily_script)

backup_process.start()  # pausing for other test
backup_daily_process.start()


# For constructing a new .json file
def backupwriter(new_file_path, uinfo, end=False):
    if not end:
        if (
            new_file_path.exists()
        ):  # File exists, so will not be first entry, means need a comma in front
            with open(new_file_path, "a") as nf:
                json_string = json.dumps(uinfo)
                json_string = json_string[1 : len(json_string) - 1]  # Get rid of {}
                json_string = "," + "\n" + json_string
                nf.write(json_string)
        else:
            with open(new_file_path, "w") as nf:
                json_string = json.dumps(uinfo)
                json_string = json_string[: len(json_string) - 1]  # Get rid of }
                nf.write(json_string)
    else:
        with open(new_file_path, "a") as nf:
            end_string = "\n}"
            nf.write(end_string)


############################### Management Dashboard ###########################
with app.app_context():
    # Define Flask context variables to be used in apps.
    # In this case, we define the dataframe used in the Population app (df)
    # and the Flask instance to be passed to both apps (cur_app)
    g.df = pd.read_csv("./visualisation_files/Electricity.csv")

    g.cur_app = app

    # Add Dash app to Flask context. Specify the app's url path and pass the flask server to your data
    app = management_dash.init_app("/management-dashboard/")


############################## Logging Code ##############################


class Log:
    def __init__(self, timestamp, request_type, details):
        self.timestamp = timestamp
        self.request_type = request_type
        self.details = details


logs = []

log_dir = Path("./logs")
log_file_path = log_dir / "logs.txt"


# Logging Function:
# Please use this funtion to add the logging details
# see the usage in get_meter_id function
def log_request(request_type, details):
    log = Log(datetime.datetime.now(), request_type, details)
    logs.append(log)

    if not log_file_path.exists():
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file_path.touch()

    with log_file_path.open("a") as log_file:
        log_file.write(f"{log.timestamp} - {log.request_type} - {log.details}\n")


############################## New User Code ##############################


# Function to get users from user.json
# Load users from users.json
def load_users():
    with open("database/users.json", "r") as file:
        return json.load(file)  # Return nested dictinory with users and their data


def save_db(data, filename="database/data.json"):
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)
    log_request(
        "Updated database",
        f"{filename.split('/')[-1].split('.')[0]} database rewritten",
    )
    # print(f"Generated {filename}")


############################## Meter Data Code ##############################


class MeterData:
    def __init__(self, id, timestamp, reading):
        self.id = id
        self.timestamp = timestamp
        self.reading = reading


# Flushed daily to txt file
# Backup system reads from this every 2 hours
# format: {meterid1: {prevreading: meterdata,
#                     timestamp1: meterdata1.1,
#                    {timestamp2: meterdata1.2},
#          meterid2: {prevreading: meterdata,
#                     timestamp1: meterdata2.1,
#                     timestamp2: meterdata2.2}
#           }

# comment out later
# meter_readings = {}

# testing data
# in memory daily data (to be replaced by actual, test for now)
# df format
#           999999999  555555555  111111111  222222222  333333333
# 00:31       4.50       4.50       4.40       4.35       4.48
# 01:01       4.55       4.55       4.45       4.40       4.53
# 01:31       4.60       4.60       4.48       4.45       4.56
meter_readings = {}

# testing data
# in memory daily data (to be replaced by actual, test for now)
# df format
#           999999999  555555555  111111111  222222222  333333333
# 00:31       4.50       4.50       4.40       4.35       4.48
# 01:01       4.55       4.55       4.45       4.40       4.53
# 01:31       4.60       4.60       4.48       4.45       4.56
dailyDB = {
  "999999999": {
    "00:31": 4.50, "01:01": 4.55, "01:31": 4.60, "02:01": 4.58, "02:31": 4.62,
    "03:01": 4.47, "03:31": 4.53, "04:01": 4.48, "04:31": 4.59, "05:01": 4.61,
    "05:31": 4.50, "06:01": 4.52, "06:31": 4.46, "07:01": 4.49, "07:31": 4.57,
    "08:01": 4.60, "08:31": 4.54, "09:01": 4.63, "09:31": 4.55, "10:01": 4.50,
    "10:31": 4.58, "11:01": 4.62, "11:31": 4.47, "12:01": 4.59, "12:31": 4.54,
    "13:01": 4.51, "13:31": 4.60, "14:01": 4.53, "14:31": 4.48, "15:01": 4.57,
    "15:31": 4.49, "16:01": 4.61, "16:31": 4.55, "17:01": 4.50, "17:31": 4.46,
    "18:01": 4.60, "18:31": 4.52, "19:01": 4.58, "22:01":4.6, "prevreading": 7.3
  },
  "555555555": {
    "00:31": 4.50, "01:01": 4.55, "01:31": 4.60, "02:01": 4.58, "02:31": 4.62,
    "03:01": 4.47, "03:31": 4.53, "04:01": 4.48, "04:31": 4.59, "05:01": 4.61,
    "05:31": 4.50, "06:01": 4.52, "06:31": 4.46, "07:01": 4.49, "07:31": 4.57,
    "08:01": 4.60, "08:31": 4.54, "09:01": 4.63, "09:31": 4.55, "10:01": 4.50,
    "10:31": 4.58, "11:01": 4.62, "11:31": 4.47, "12:01": 4.59, "12:31": 4.54,
    "13:01": 4.51, "13:31": 4.60, "14:01": 4.53, "14:31": 4.48, "15:01": 4.57,
    "15:31": 4.49, "16:01": 4.61, "16:31": 4.55, "17:01": 4.50, "17:31": 4.46,
    "18:01": 4.60, "18:31": 4.52, "19:01": 4.58, "prevreading": 7.3
  },
  "111111111": {
    "00:31": 4.40, "01:01": 4.45, "01:31": 4.48, "02:01": 4.50, "02:31": 4.55,
    "03:01": 4.43, "03:31": 4.50, "04:01": 4.42, "04:31": 4.51, "05:01": 4.60,
    "05:31": 4.45, "06:01": 4.48, "06:31": 4.41, "07:01": 4.47, "07:31": 4.50,
    "08:01": 4.58, "08:31": 4.49, "09:01": 4.57, "09:31": 4.52, "10:01": 4.48,
    "10:31": 4.55, "11:01": 4.60, "11:31": 4.43, "12:01": 4.52, "12:31": 4.50,
    "13:01": 4.47, "13:31": 4.55, "14:01": 4.49, "14:31": 4.45, "15:01": 4.53,
    "15:31": 4.50, "16:01": 4.57, "16:31": 4.49, "17:01": 4.48, "17:31": 4.44,
    "18:01": 4.55, "18:31": 4.47, "19:01": 4.50, "prevreading": 7.3
  },
  "222222222": {
    "00:31": 4.35, "01:01": 4.40, "01:31": 4.45, "02:01": 4.47, "02:31": 4.50,
    "03:01": 4.38, "03:31": 4.46, "04:01": 4.35, "04:31": 4.48, "05:01": 4.52,
    "05:31": 4.44, "06:01": 4.45, "06:31": 4.39, "07:01": 4.41, "07:31": 4.50,
    "08:01": 4.52, "08:31": 4.48, "09:01": 4.53, "09:31": 4.46, "10:01": 4.43,
    "10:31": 4.50, "11:01": 4.55, "11:31": 4.40, "12:01": 4.47, "12:31": 4.44,
    "13:01": 4.41, "13:31": 4.49, "14:01": 4.43, "14:31": 4.38, "15:01": 4.50,
    "15:31": 4.45, "16:01": 4.52, "16:31": 4.47, "17:01": 4.42, "17:31": 4.40,
    "18:01": 4.50, "18:31": 4.44, "19:01": 4.48, "prevreading": 7.3
  },
  333333333: {
    "00:31": 4.48, "01:01": 4.53, "01:31": 4.56, "02:01": 4.55, "02:31": 4.60,
    "03:01": 4.49, "03:31": 4.54, "04:01": 4.50, "04:31": 4.57, "05:01": 4.63,
    "05:31": 4.53, "06:01": 4.55, "06:31": 4.50, "07:01": 4.52, "07:31": 4.58,
    "08:01": 4.62, "08:31": 4.57, "09:01": 4.64, "09:31": 4.58, "10:01": 4.55,
    "10:31": 4.60, "11:01": 4.65, "11:31": 4.52, "12:01": 4.60, "12:31": 4.56,
    "13:01": 4.53, "13:31": 4.62, "14:01": 4.55, "14:31": 4.50, "15:01": 4.60,
    "15:31": 4.53, "16:01": 4.65, "16:31": 4.58, "17:01": 4.55, "17:31": 4.50,
    "18:01": 4.62, "18:31": 4.55, "19:01": 4.60, "prevreading": 7.3
  }
}
def remove_prevreading(dailyDB):
    for key in dailyDB:
        dailyDB[key].pop("prevreading", None)  # Remove "prevreading" if it exists
    return dailyDB

dailyDB = remove_prevreading(dailyDB)


# reading master database
# format
# columns: name, meter_id, fin_no, previous_day(dict of 47 values with timestamps), previous days
#   name   meter_id     fin_no                                       previous_day  ...     2024-12-17  2024-12-16  2024-12-15  2024-12-14
# 0 Aashima  999999999  A3389127I  {'00:31': 8.33, '00:01': 4.73, '01:31': 8.7, '...  ...      250.18      121.27      266.34      198.4
with open("testing_data/masterDB.json", "r") as file:
    masterDB_dict = json.load(file)


# access_type either "add" or "backup"
def meterlogging(access_type, meterdata):
    if access_type == "add":
        if meterdata.id in meter_readings:
            slicedtimestamp = meterdata.timestamp[11:16]
            meter_readings[meterdata.id][slicedtimestamp] = round(
                (meterdata.reading - meter_readings[meterdata.id]["prevreading"]), 2
            )
            meter_readings[meterdata.id]["prevreading"] = meterdata.reading
            log_request(
                "Incoming meter reading",
                f"Meter reading added for account {meterdata.id}.",
            )
        else:
            slicedtimestamp = meterdata.timestamp[11:16]
            meter_readings[meterdata.id] = {"prevreading": meterdata.reading}
            meter_readings[meterdata.id][slicedtimestamp] = meterdata.reading
            log_request(
                "Incoming first meter reading",
                f"First meter reading added for account {meterdata.id}.",
            )


############################## APIs ##############################


@app.route("/", methods=["GET"])
def landing():
    return render_template("main.html")


@app.route("/register", methods=["GET"])
def register():
    return render_template("register.html")


@app.route("/register-success", methods=["POST", "GET"])
def get_meter_id():
    print(request.method)
    if request.method == "POST":
        print("Form data:", request.form)
        if (
            "name" in request.form
        ):  # Is there a scenario where "name" will not be present if the form input for name is required in /register?
            user = request.form["name"]
            fin = request.form["fin"].upper()
            db = load_users()
            meter_id = random.randint(
                1, 1000000000
            )  # checking that meter id doesn't get duplicated
            while meter_id in db.keys():
                meter_id = random.randint(1, 1000000000)
            # ---------------- TODO:: Add the user to the main db during server shutdown-----------
            db[meter_id] = {"name": user, "fin_no": fin}
            save_db(db, "database/users.json")

            log_request(
                "add_meter_reading",
                f"Meter reading account added for user {user} with FIN no. {fin} account {meter_id}.",
            )
            return render_template(
                "register_success.html",
                user=user,
                meter_id=meter_id,
            )
        else:
            log_request(
                "ERROR : in add_meter_reading",
                f"Unable to fetch the name from the form data.",
            )
            return "Name not found in form data."

    elif request.method == "GET":  # How will this scenario happen?
        log_request("ERROR : in add_meter_reading", f"Request method recieved as GET")
        return "Please submit the form to register."
    log_request("ERROR : INVALID REQUEST METHOD")
    return "Invalid request method."


@app.route("/profile", methods=["GET", "POST"])
def user_login():
    if request.method == "GET":
        # Render login form
        return render_template("profile.html")

    elif request.method == "POST":
        # Get meter_id from the form
        meter_id = request.form.get("meter_id")

        # Load users from JSON
        users = load_users()

        # Check if meter_id exists in the dictionary
        if (meter_id) in users:
            # Redirect to the profile page
            return render_template_string(
                """
                <script>
                window.location.href = '/profile/{{ meter_id }}';
                </script>
             """,
                meter_id=meter_id,
            )
        else:
            # User not found
            log_request(f"Error", f"User entered wrong meter ID")
            return render_template_string(
                """
                <head>
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <link rel="stylesheet" href="{{url_for('static', filename='styles.css')}}">
                </head>
                <body>
                <p>Error: User not found. Please check your meter ID and try again.</p>
                <a href="{{ url_for('user_login') }}" class = "button">Back to login</a>
                </body>
            """
            )


@app.route("/profile/<meterid>", methods=["GET"])
def user_profile(meterid):
    users = load_users()
    if meterid in users:
        user = users[meterid]
        log_request("Login successful", f"Meter ID : {meterid} logged in successfully")
        return render_template(
            "profile_meter_id.html",
            name=user["name"],
            meter_id=meterid,
        )
    else:
        log_request("Login failed", f"Meter ID : {meterid} not in DB")
        return render_template_string(
            """
            <head>
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <link rel="stylesheet" href="{{url_for('static', filename='styles.css')}}">
            </head>
            <body>
            <p>Error: User not found. Please check your meter ID and try again.</p>
            <a href="{{ url_for('user_login') }}"  class = "button">Back to login</a>
            </body>
            """
        )


@app.route("/profile/<meterid>/consumption/", methods=["GET"])
def profile_home(meterid):
    # The JavaScript now simply redirects for any selected value.
    return render_template("profile_home.html", meterid=meterid)

@app.route("/profile/<meterId>/consumption/last-half-hour", methods=["GET"])
def get_last_half_hour(meterId):
    if meterId not in dailyDB:
        return f"Meter ID {meterId} not found", 404
    
    now = datetime.datetime.now().time()
    half_hour_ago = (datetime.datetime.now() - timedelta(minutes=30)).time()

    filtered_data = {
        time_str: value
        for time_str, value in dailyDB[meterId].items()
        if half_hour_ago <= datetime.datetime.strptime(time_str, "%H:%M").time() <= now
    }

    if not filtered_data:
        return f"No data found for the last half hour for Meter ID: {meterId}", 404

    latest_time, latest_consumption = list(filtered_data.items())[-1]

    table_html = f"""
    <html>
    <head>
        <title>Previous Half Hour Consumption</title>
        <style>
            table {{ width: 50%; border-collapse: collapse; }}
            th, td {{ border: 1px solid black; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
        </style>
    </head>
    <body>
        <h2>Previous Half Hour Consumption for Meter ID: {meterId}</h2>
        <table>
            <tr><th>Last Half Hour</th><th>Consumption</th></tr>
            <tr><td>{latest_time}</td><td>{latest_consumption}</td></tr>
        </table>
    </body>
    </html>
    """
    return render_template_string(table_html)


@app.route("/profile/<meterId>/consumption/today", methods=["GET"])
def get_consumption(meterId):
    if meterId not in dailyDB.keys():
        return f"Meter ID {meterId} not found", 404

    data = dailyDB[meterId]
    table_html = """
    <html>
    <head>
        <title>Consumption Data</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            table { width: 50%%; border-collapse: collapse; }
            th, td { border: 1px solid black; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
            .container { display: flex; gap: 20px; }
            .chart-container { width: 600px; height: 400px; }
        </style>
    </head>
    <body>
        <h2>Consumption Data for Meter ID: {{ meterId }}</h2>
        <div class="container">
            <div>
                <table>
                    <tr><th>Time</th><th>Consumption</th></tr>
                    {% for time, value in data.items() %}
                        <tr><td>{{ time }}</td><td>{{ value }}</td></tr>
                    {% endfor %}
                </table>
            </div>
            <div class="chart-container">
                <canvas id="consumptionChart"></canvas>
            </div>
        </div>

        <script>
            var ctx = document.getElementById('consumptionChart').getContext('2d');
            var chart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: {{ data.keys() | list | tojson }},
                    datasets: [{
                        label: 'Consumption',
                        data: {{ data.values() | list | tojson }},
                        borderColor: 'blue',
                        backgroundColor: 'rgba(0, 0, 255, 0.1)',
                        borderWidth: 2,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        x: { title: { display: true, text: 'Time' } },
                        y: { title: { display: true, text: 'Consumption' } }
                    }
                }
            });
        </script>
    </body>
    </html>
    """
    return render_template_string(table_html, meterId=meterId, data=data)


def get_current_week_dates():
    """Return a list of date strings for the current week (Monday through Sunday)."""
    today = datetime.datetime.today().date()
    start_of_week = today - timedelta(days=today.weekday())  # Monday
    return [(start_of_week + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]


@app.route("/profile/<meterid>/consumption/current-week", methods=["GET"])
def consumption_this_week(meterid):
    if meterid not in masterDB_dict:
        return f"Meter ID {meterid} not found", 404

    # Get the list of dates for the current week
    week_dates = get_current_week_dates()

    # Filter the weekly data from the meter record; ignore keys that are not valid dates.
    weekly_data = {}
    for date_str, value in masterDB_dict[meterid].items():
        try:
            # Only process keys that look like dates (YYYY-MM-DD)
            datetime.datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            continue
        if date_str in week_dates:
            weekly_data[date_str] = value

    if not weekly_data:
        return f"No data found for the current week for Meter ID: {meterid}", 404

    # Sort the dates to maintain order for both table and graph
    sorted_dates = sorted(weekly_data.keys())
    sorted_values = [weekly_data[date] for date in sorted_dates]

    # Build an HTML page that includes both a table and a graph (using Chart.js)
    table_html = f"""
    <html>
    <head>
        <title>This Week's Consumption</title>
        <style>
            table {{
                width: 50%;
                border-collapse: collapse;
            }}
            th, td {{
                border: 1px solid black;
                padding: 8px;
                text-align: left;
            }}
            th {{
                background-color: #f2f2f2;
            }}
        </style>
        <!-- Load Chart.js from CDN -->
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    </head>
    <body>
        <h2>This Week's Consumption for Meter ID: {meterid}</h2>
        <table>
            <tr>
                <th>Date</th>
                <th>Consumption</th>
            </tr>
    """
    for date_str in sorted_dates:
        table_html += f"<tr><td>{date_str}</td><td>{weekly_data[date_str]}</td></tr>"
    table_html += (
        """
        </table>
        <br>
        <canvas id="consumptionChart" width="600" height="300"></canvas>
        <script>
            var ctx = document.getElementById('consumptionChart').getContext('2d');
            var chart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: """
        + str(sorted_dates)
        + """,
                    datasets: [{
                        label: 'Consumption',
                        data: """
        + str(sorted_values)
        + """,
                        backgroundColor: 'rgba(75, 192, 192, 0.2)',
                        borderColor: 'rgba(75, 192, 192, 1)',
                        borderWidth: 2,
                        fill: false
                    }]
                },
                options: {
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        </script>
    </body>
    </html>
    """
    )
    return render_template_string(table_html)


@app.route("/profile/<meterid>/consumption/current-month", methods=["GET"])
def consumption_this_month(meterid):
    if meterid not in masterDB_dict:
        return f"Meter ID {meterid} not found", 404

    now = datetime.datetime.today()
    current_year = now.year
    current_month = now.month

    # Filter the data for the current month (using calendar month boundaries)
    monthly_data = {}
    for key, value in masterDB_dict[meterid].items():
        try:
            # Only process keys that follow the date format YYYY-MM-DD
            dt = datetime.datetime.strptime(key, "%Y-%m-%d")
        except ValueError:
            continue
        if dt.year == current_year and dt.month == current_month:
            monthly_data[key] = value

    if not monthly_data:
        return f"No data found for the current month for Meter ID: {meterid}", 404

    # Sort dates for consistent ordering in the table and graph
    sorted_dates = sorted(monthly_data.keys())
    sorted_values = [monthly_data[date] for date in sorted_dates]

    # Build the HTML output with a table and a Chart.js graph
    html_template = f"""
    <html>
    <head>
        <title>This Month's Consumption</title>
        <style>
            table {{
                width: 50%;
                border-collapse: collapse;
            }}
            th, td {{
                border: 1px solid black;
                padding: 8px;
                text-align: left;
            }}
            th {{
                background-color: #f2f2f2;
            }}
        </style>
        <!-- Load Chart.js from CDN -->
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    </head>
    <body>
        <h2>This Month's Consumption for Meter ID: {meterid}</h2>
        <table>
            <tr>
                <th>Date</th>
                <th>Consumption</th>
            </tr>
    """
    for date_str in sorted_dates:
        html_template += (
            f"<tr><td>{date_str}</td><td>{monthly_data[date_str]}</td></tr>"
        )
    html_template += (
        """
        </table>
        <br>
        <canvas id="consumptionChart" width="800" height="400"></canvas>
        <script>
            var ctx = document.getElementById('consumptionChart').getContext('2d');
            var chart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: """
        + str(sorted_dates)
        + """,
                    datasets: [{
                        label: 'Consumption',
                        data: """
        + str(sorted_values)
        + """,
                        backgroundColor: 'rgba(75, 192, 192, 0.2)',
                        borderColor: 'rgba(75, 192, 192, 1)',
                        borderWidth: 2,
                        fill: false
                    }]
                },
                options: {
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        </script>
    </body>
    </html>
    """
    )
    return render_template_string(html_template)


@app.route("/profile/<meterid>/consumption/last-month", methods=["GET"])
def consumption_last_month(meterid):
    if meterid not in masterDB_dict:
        return f"Meter ID {meterid} not found", 404

    now = datetime.datetime.today()
    # Determine last month's year and month (handle January rollover)
    if now.month == 1:
        last_month = 12
        year = now.year - 1
    else:
        last_month = now.month - 1
        year = now.year

    # Filter the data for last month using the calendar month and year
    monthly_data = {}
    for key, value in masterDB_dict[meterid].items():
        try:
            dt = datetime.datetime.strptime(key, "%Y-%m-%d")
        except ValueError:
            continue
        if dt.year == year and dt.month == last_month:
            monthly_data[key] = value

    if not monthly_data:
        return f"No data found for last month for Meter ID: {meterid}", 404

    # Sort the dates for consistent ordering in the table and graph
    sorted_dates = sorted(monthly_data.keys())
    sorted_values = [monthly_data[date] for date in sorted_dates]

    # Create an HTML page that displays a table of the data and a Chart.js graph
    html_template = f"""
    <html>
    <head>
        <title>Last Month's Consumption</title>
        <style>
            table {{
                width: 50%;
                border-collapse: collapse;
            }}
            th, td {{
                border: 1px solid black;
                padding: 8px;
                text-align: left;
            }}
            th {{
                background-color: #f2f2f2;
            }}
        </style>
        <!-- Load Chart.js from a CDN -->
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    </head>
    <body>
        <h2>Last Month's Consumption for Meter ID: {meterid}</h2>
        <table>
            <tr>
                <th>Date</th>
                <th>Consumption</th>
            </tr>
    """
    for date_str in sorted_dates:
        html_template += (
            f"<tr><td>{date_str}</td><td>{monthly_data[date_str]}</td></tr>"
        )
    html_template += (
        """
        </table>
        <br>
        <canvas id="consumptionChart" width="800" height="400"></canvas>
        <script>
            var ctx = document.getElementById('consumptionChart').getContext('2d');
            var chart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: """
        + str(sorted_dates)
        + """,
                    datasets: [{
                        label: 'Consumption',
                        data: """
        + str(sorted_values)
        + """,
                        backgroundColor: 'rgba(75, 192, 192, 0.2)',
                        borderColor: 'rgba(75, 192, 192, 1)',
                        borderWidth: 2,
                        fill: false
                    }]
                },
                options: {
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        </script>
    </body>
    </html>
    """
    )
    return render_template_string(html_template)


@app.route("/meter", methods=["POST"])
def meterfeed():
    if not backuplock:
        meterdatajson = request.get_json()
        if meterdatajson is None:
            log_request("Failed Meter Reading Request", "Missing meter reading data")
            return "Missing meter data"

        else:
            meterdata = MeterData(
                str(meterdatajson["id"]),
                meterdatajson["timestamp"],
                meterdatajson["reading_kWh"],
            )
            meterlogging("add", meterdata)
            return "Meter successfully logged"
    else:
        return make_response("Server Paused", 201)


# For backup
@app.route("/getmeterdata", methods=["GET"])
def meterdiver():
    global backuplock
    backuplock = True
    jsoned_meter_readings = json.dumps(meter_readings, indent=4)

    # Testing block
    time.sleep(4)
    print("sleep over")
    # Testing block

    backuplock = False
    return jsoned_meter_readings


@app.route("/fullserverbackup", methods=["GET"])
def dailybackup():
    global meter_readings
    global backuplock
    backuplock = True
    backup_file_path = Path("./database/data.json")
    userlist_file_path = Path("./database/users.json")
    new_backup_file_path = Path("./database/datason.json")
    grandpa_backup_file_path = Path("./database/datagrandpa.json")
    if backup_file_path.exists():
        with open(backup_file_path, "r") as f:
            data = json_stream.load(f)
            for key, value in data.items():
                tempdict = dict(
                    value.items()
                )  # Store values in transient JSON object into temp dict
                if (
                    key in meter_readings
                ):  # There is already an entry in existing database, need to add new aggregate value to it
                    meter_readings[key].pop("prev_reading", None)
                    daily_consumption = sum(meter_readings[key].values())
                    tempdict[str(datetime.date.today())] = (
                        daily_consumption  # Add new data to the packet copy
                    )
                    complete_packet = {key: tempdict}
                    backupwriter(new_backup_file_path, complete_packet)
                    meter_readings.pop(
                        key, None
                    )  # Remove the key:value pair in meter_readings so what is leftover will be new meter_ids that have no backup before
                else:  # There is no new meter readings for that particular meter_id in backup. So rewrite the old back up data to the new backup data
                    complete_packet = {key: tempdict}
                    backupwriter(new_backup_file_path, complete_packet)

        # Whatever left over in meter_readings are new meter_ids yet to have been backed up before
        if meter_readings:  # empty dicts return False
            userdata = load_users()
            for key, value in meter_readings.items():
                # Construct format
                json_packet = {}
                daily_consumption = sum(meter_readings[key].values())
                username = userdata[key]["name"]
                userFIN = userdata[key]["fin_no"]
                json_packet[key] = {
                    "name": username,
                    "fin_no": userFIN,
                    str(datetime.date.today()): daily_consumption,
                }
                backupwriter(new_backup_file_path, json_packet)

        # Add the } at the end to complete the json file
        backupwriter(new_backup_file_path, None, True)

        # Flush meter_readings. Should already be empty
        meter_readings = {}
        log_request("In-memory Flush", "Backup Done, flushing in-memory data")

        # Replace old back up file with new and move old backup to older backup while deleting oldest backup
        if grandpa_backup_file_path.exists():
            grandpa_backup_file_path.unlink()
            log_request("Deletion of oldest backup", "Grandpa Backup Deleted")
        backup_file_path.rename(grandpa_backup_file_path)
        log_request("Backup Rename", "Renamed current backup to Grandpa Backup")
        new_backup_file_path.rename(backup_file_path)
        log_request("Backup Rename", "Renamed new (son) backup to current Backup")

    else:  # No backup_file exists. Create and populate a new one
        if meter_readings:  # empty dicts return False
            userdata = load_users()
            for key, value in meter_readings.items():
                # Construct format
                json_packet = {}
                daily_consumption = sum(meter_readings[key].values())
                username = userdata[key]["name"]
                userFIN = userdata[key]["fin_no"]
                json_packet[key] = {
                    "name": username,
                    "fin_no": userFIN,
                    str(datetime.date.today()): daily_consumption,
                }
                backupwriter(backup_file_path, json_packet)

            # Add the } at the end to complete the json file
            backupwriter(backup_file_path, None, True)
            log_request("Backup Created", "First Backup Done")

            # Flush meter_readings
            meter_readings = {}
            log_request("In-memory Flush", "Backup Done, flushing in-memory data")

    backuplock = False

    return "Completed"


# Recovery from backup data
@app.route("/recovery", methods=["GET"])
def recovery():
    global backuplock
    global meter_readings
    backuplock = True
    recovery_file_path = Path("./daily_backup/backup.json")

    if recovery_file_path.exists():  # Check if the backup file exists
        with open(recovery_file_path, "r") as rf:
            recovery_data = json.load(rf)
            meter_readings = recovery_data
        log_request("Backup Recovery", "Recovery from daily backup done.")
        backuplock = True
        return "Backup Sucessfully Completed"

    else:
        log_request("Backup Recovery", "No backup found")
        backuplock = False
        return "Backup Failed"


############################## Runs the file ##############################

if __name__ == "__main__":
    app.run(
        host="localhost", port=5000, debug=False  ######### change port to 5000
    )  # Changing to False to test process locking
