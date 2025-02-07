from flask import Flask, jsonify, request
import requests
import random

app = Flask(__name__)

new_user_list = []
meter_id_list = set([random.randint(1, 1000000000) for i in range(40)])


@app.route("/", methods=["GET"])
def landing():
    return "Created so that server will run. Needs a lot of modifications"


@app.route("/register")
def register():
    return """
<html>
    <div id="rightdiv">
       Please enter your name to enter to register for the meter.
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
        if "name" in request.form:
            user = request.form["name"]
            new_user_list.append(user)
            meter_id = random.randint(1, 1000000000)  # Update this as needed
            while meter_id in meter_id_list:
                meter_id = random.randint(1, 1000000000)
            meter_id_list.add(meter_id)
            # TODO: Add a button which redirects to the electricity consumption page or login page
            return f"Hi {user}, your login ID is {meter_id:d}.<br> Use this ID to view your electricity consumption."
        else:
            return "Name not found in form data."
    elif request.method == "GET":
        return "Please submit the form to register."
    return "Invalid request method."


@app.route("/profile", methods=["POST"])
def retrieve(meterid):
    pass


@app.route("/profile/<meterid>", methods=["GET"])
def userlanding(meterid):
    pass


@app.route("/profile/<meterid>/consumption", methods=["GET"])
def consumption(meterid):
    pass


# @app.route("/profile/<meterid>/consumption", methods=["GET"])  # add the ?period thing
# def consumption(meterid):
#     pass


@app.route("/profile/<meterid>/consumption/download", methods=["GET"])
def downloadconsumption():
    pass


@app.route("/meter", methods=["POST"])
def meterfeed():
    pass


if __name__ == "__main__":
    app.run(host="localhost", port=5000, debug=False)
