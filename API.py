############################## Imports ##############################

from flask import Flask, jsonify, request, render_template_string, url_for
import random
import datetime
import json
from pathlib import Path

app = Flask(__name__)

############################## New User Code ##############################

new_user_list = ["john A"]
meter_id_list = set([random.randint(1, 1000000000) for i in range(40)])


# Function to get users from user.json
def load_users():
    with open("users.json", "r") as file:
        data = json.load(file)
    return data["users"]  # Return list of users


############################## Logging Code ##############################


class Log:
    def __init__(self, timestamp, request_type, details):
        self.timestamp = timestamp
        self.request_type = request_type
        self.details = details


logs = []

log_dir = Path("./logs")
log_file_path = log_dir / "logs.txt"

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


############################## Meter Data Code ##############################


class meterdata:
    def __init__(self, timestamp, consumption):
        self.timestamp = timestamp
        self.consumption = consumption


# Flushed daily to txt file
# Backup system reads from this every 2 hours
# format: {meterid1: [meterdata1, meterdata2, ...],
#          meterid2: [meterdata1, meterdata2, ...]}
meter_readings = {}


# access_type either "add" or "backup"
def meterlogging(access_type, meter_id, meter_data=None):
    if access_type == "add":
        if meter_id in meter_readings:
            meter_readings[meter_id].append(meter_data)
            log_request(
                "Incoming meter reading", f"Meter reading added for account {meter_id}."
            )
        else:
            meter_readings[meter_id] = [meter_data]
            log_request(
                "Incoming first meter reading",
                f"First meter reading added for account {meter_id}.",
            )

    elif access_type == "backup":
        # TODO
        pass


############################## APIs ##############################


@app.route("/", methods=["GET"])
def landing():
    # TODO Form to lead to /profile which takes in user meterid
    return "Created so that server will run. Needs a lot of modifications"


@app.route("/register")
def register():
    return """
<html>
    <div id="rightdiv">
       Please enter your name to register for the meter.
       <form action="/register-success" method="post">
              <label for="name">
                <strong>Name</strong>
              </label>
              <input type="text" id="name" placeholder="Enter your name to register" name="name" required>
              <br>
              <input type="submit" value="Click to register"/>
       </form>
    </div>
    </html>"""


@app.route("/register-success", methods=["POST", "GET"])
def get_meter_id():
    print(request.method)
    if request.method == "POST":
        print("Form data:", request.form)
        if (
            "name" in request.form
        ):  # Is there a scenario where "name" will not be present if the form input for name is required in /register?
            user = request.form["name"]
            new_user_list.append(user)
            meter_id = random.randint(1, 1000000000)  # Update this as needed
            while meter_id in meter_id_list:
                meter_id = random.randint(1, 1000000000)
            meter_id_list.add(meter_id)
            # TODO: Add a button which redirects to the electricity consumption page or login page
            log_request(
                "add_meter_reading",
                f"Meter reading account added for user {user} account {meter_id}.",
            )
            return render_template_string(
                """
                <p>Hi {{ user }}, your login ID is {{ meter_id }}.</p>
                <p>You will be redirected to main page in 10 seconds.</p>
                <p>Use this id to view your electricity consumption.</p>
                <script>
                    setTimeout(function() {
                        window.location.href = "{{ url_for('landing') }}";
                    }, 10000);  // Redirect after 10 seconds
                </script>
            """,
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
        # If it's a GET request, render the login form
        return """
            <html>
                <body>
                    <h2>User Login</h2>
                    <form method="POST" action="/profile">
                        <label for="meter_id">Enter your Meter ID:</label>
                        <input type="text" id="meter_id" name="meter_id" required>
                        <input type="submit" value="Login">
                    </form>
                </body>
            </html>
        """
    elif request.method == "POST":
        # If it's a POST request, process the login
        meter_id = request.form.get("meter_id")

        # Load users from the users.json file
        users = load_users()

        # Check if the meter_id exists in the list of users
        user_found = None
        for user in users:
            if user["meter_id"] == int(meter_id):  # Match the meter_id
                user_found = user
                break

        if user_found:
            # If user found, redirect to the profile page
            return render_template_string(
                """
                <script>
                window.location.href = '/profile/{{ meter_id }}';
                </script>
             """,
                meter_id=meter_id,
            )
        else:
            # Error message and option to return to the login page
            return render_template_string(
                """
                <p>Error: User not found. Please check your meter ID and try again.</p>
                <a href="{{ url_for('user_login') }}">Back to login</a>
            """
            )


@app.route("/profile/<meterid>", methods=["GET"])
def user_profile(meterid):
    # Load users from the users.json file
    users = load_users()

    # Find the user by meter_id
    for user in users:
        if user["meter_id"] == int(meterid):  # Match the meter_id
            # Return the profile page with the button leading to consumption page
            return render_template_string(
                """
                <h1>Welcome, {{ name }}!</h1>
                <p>Your Meter ID is: {{ meter_id }}</p>
                <form method="get" action="/profile/{{ meter_id }}/consumption">
                    <input type="submit" value="Go to Consumption">
                </form>
            """,
                name=user["name"],
                meter_id=meterid,
            )

    # If the user is not found (in case something goes wrong)
    return f"Error: User with Meter ID {meterid} not found."


@app.route("/profile/<meterid>/consumption", methods=["GET"])
def consumption(meterid):
    pass


# @app.route("/profile", methods=["POST"])
# def retrieve(meterid):
#     pass


@app.route("/profile/<meterid>/consumption/download", methods=["GET"])
def downloadconsumption():
    pass


@app.route("/meter", methods=["POST"])
def meterfeed():
    meterdata = request.get_json()
    print(meterdata)
    if meterdata is None:
        log_request("Failed Meter Reading Request", "Missing meter reading data")
        return "Missing meter data"

    else:
        meterlogging("add", meterdata["id"], meterdata["reading_kWh"])
        return "Meter successfully logged"


############################## Runs the file ##############################

if __name__ == "__main__":
    app.run(host="localhost", port=5000, debug=True)
