from flask import Flask, jsonify, request, render_template_string, url_for
import requests
import random
import datetime

app = Flask(__name__)

new_user_list = ["john A"]
meter_id_list = set([random.randint(1, 1000000000) for i in range(40)])


# Logging Codes
class Log:
    def __init__(self, timestamp, request_type, details):
        self.timestamp = timestamp
        self.request_type = request_type
        self.details = details


logs = []


# Logging Function:
# Please use this funtion to add the logging details
# see the usage in get_meter_id function
def log_request(request_type, details):
    log = Log(datetime.datetime.now(), request_type, details)
    logs.append(log)
    with open("logs.txt", "a") as log_file:
        log_file.write(f"{log.timestamp} - {log.request_type} - {log.details}\n")


# Meter Data Codes
class meterdata:
    def __init__(self, timestamp, consumption):
        self.timestamp = timestamp
        self.consumption = consumption


# Flushed daily to txt file
# {meterid: [meterdata]}
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


# APIs
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


@app.route("/profile")
def retrieve(meterid):
    pass


@app.route("/profile/<meterid>", methods=["GET"])
def userlanding(meterid):
    pass


@app.route("/profile/<meterid>/consumption", methods=["GET"])
def consumption(meterid):
    pass


@app.route("/profile", methods=["POST"])
def retrieve(meterid):
    pass


@app.route("/profile/<meterid>/consumption/download", methods=["GET"])
def downloadconsumption():
    pass


@app.route("/meter", methods=["POST"])
def meterfeed():
    pass


if __name__ == "__main__":
    app.run(host="localhost", port=5000, debug=True)
