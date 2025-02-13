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
# Load users from users.json
def load_users():
    with open('./database/users.json', 'r') as file:
        return json.load(file) #Return nested dictinory with users and their data

############################## Logging Code ##############################

class Log:
    def __init__(self, timestamp, request_type, details):
        self.timestamp = timestamp
        self.request_type = request_type
        self.details = details


logs = []

log_dir = Path("./logs")
log_file_path = log_dir/"logs.txt"

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

meter_readings = {}


# access_type either "add" or "backup"
def meterlogging(access_type, meterdata):
    if access_type == "add":
        if meterdata.id in meter_readings:
            slicedtimestamp = meterdata.timestamp[11:16]
            meter_readings[meterdata.id][slicedtimestamp] = meter_readings[meterdata.id]["prevreading"] - meterdata.reading
            meter_readings[meterdata.id]["prevreading"] = meterdata.reading
            log_request(
                "Incoming meter reading", f"Meter reading added for account {meterdata.id}."
            )
        else:
            slicedtimestamp = meterdata.timestamp[11:16]
            meter_readings[meterdata.id] = {"prevreading": meterdata.reading}
            meter_readings[meterdata.id][slicedtimestamp] = meterdata.reading
            log_request(
                "Incoming first meter reading",
                f"First meter reading added for account {meterdata.id}.",
            )

    elif access_type == "2hrbackup":
        tempbackuppath = Path("./daily_backup")
        tempbackup_file_path = tempbackuppath/"hourlybackup.json"
        tempbackuppath.mkdir(parents=True, exist_ok=True)
        tempbackup_file_path.touch()
        with open(tempbackup_file_path, w) as tempf:
            json.dump(meter_readings, tempf)

############################## APIs ##############################

@app.route("/", methods=["GET"])
def landing():
    return render_template_string(
        """
        <html>
        <body>
            <h1>Welcome to Meter Registration</h1>
            <button onclick="location.href='/register'">Register</button>
            <button onclick="location.href='/profile'">Login</button>
        </body>
        </html>
        """
            )


@app.route("/register", methods=["GET"])
def register():
    return render_template_string(
        """
        <html>
        <body>
            <h2>Register for a Meter</h2>
            <form action="/register-success" method="post">
                <label for="name">Name:</label>
                <input type="text" id="name" name="name" required>
                <br>
                <label for="fin">FIN:</label>
                <input type="text" id="fin" name="fin" required>
                <br>
                <input type="submit" value="Register">
            </form>
        </body>
        </html>
        """
    )



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
                <button onclick="window.location.href='/profile'">Go to Login</button>
                <button onclick="window.location.href='/profile/{{ meter_id }}/consumption'">View Electricity Consumption</button>
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


@app.route('/profile', methods=['GET', 'POST'])
def user_login():
    if request.method == 'GET':
        # Render login form
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
    elif request.method == 'POST':
        # Get meter_id from the form
        meter_id = request.form.get('meter_id')

        # Load users from JSON
        users = load_users()

        # Check if meter_id exists in the dictionary
        if (meter_id) in users:
            # Redirect to the profile page
            log_request(f"User logged in",f"Meter ID : {meter_id} logged in")
            return render_template_string("""
                <script>
                window.location.href = '/profile/{{ meter_id }}';
                </script>
             """, meter_id=meter_id)
                
        else:
            # User not found
            log_request(f"Error",f"User entered wrong meter ID")
            return render_template_string("""
                <p>Error: User not found. Please check your meter ID and try again.</p>
                <a href="{{ url_for('user_login') }}">Back to login</a>
            """)
            

@app.route("/profile/<meterid>", methods=["GET"])
def user_profile(meterid):
    # Load users from the users.json file
    users = load_users()

    # Check if meterID exists in the dictionary
    if (meterid) in users:
        user = users[(meterid)]  # User details
        log_request(f"Login successful",f"Meter ID : {meterid} logged in successfully")

        # Return the profile page with a button leading to the consumption page
        return render_template_string("""
            <h1>Welcome, {{ name }}!</h1>
            <p>Your Meter ID is: {{ meter_id }}</p>
            <form method="get" action="/profile/{{ meter_id }}/consumption">
                <input type="submit" value="Go to Consumption">
            </form>
        """, name=user['name'], meter_id=meterid)
    
    
    
    else:
        # If user is not found, show error message (In case something goes wrong)
        log_request(f"Login failed",f"Meter ID : {meterid} not in DB")
        return render_template_string("""
            <p>Error: User not found. Please check your meter ID and try again.</p>
            <a href="{{ url_for('user_login') }}">Back to login</a>
        """)


@app.route("/profile/<meterid>/consumption", methods=["GET"])
def consumption(meterid):
    return "test"


@app.route("/profile", methods=["POST"])
def profile_retrieval(meterid):
    pass


@app.route("/profile/<meterid>/consumption/download", methods=["GET"])
def downloadconsumption():
    pass


@app.route("/meter", methods=["POST"])
def meterfeed():
    meterdatajson = request.get_json()
    if meterdatajson is None:
        log_request("Failed Meter Reading Request", "Missing meter reading data")
        return "Missing meter data"
    
    else:
        meterdata = MeterData(meterdatajson["id"], meterdatajson["timestamp"], meterdatajson["reading_kWh"])
        meterlogging("add", meterdata)
        return "Meter successfully logged"
    
# This is a barebones test API endpoint to extract out current in-memory meter reading data as the server is running. To delete, or maybe keep. Who knows?
@app.route("/getmeterdata", methods=["GET"])
def meterdiver():
    return meter_readings


############################## Runs the file ##############################

if __name__ == "__main__":
    app.run(host="localhost", port=5000, debug=True)
