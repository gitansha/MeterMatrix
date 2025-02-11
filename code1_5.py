from flask import Flask, render_template_string, jsonify, redirect, url_for, request

app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Home</title>
    </head>
    <body>
        <h1>Welcome to the Consumption API</h1>
        <p>Please enter your Meter ID to view consumption data:</p>
        <form action="/profile" method="get">
            <label for="meterid">Meter ID:</label>
            <input type="text" id="meterid" name="meterid" required>
            <button type="submit">Submit</button>
        </form>
    </body>
    </html>
    '''

@app.route('/profile', methods=['GET'])
def profile_redirect():
    meterid = request.args.get('meterid')
    if meterid:
        return redirect(url_for('profile_home', meterid=meterid))
    return "Meter ID is required."

@app.route('/profile/<meterid>/consumption/', methods=['GET'])
def profile_home(meterid):
    return f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Profile Consumption</title>
        <script>
            function handleButtonClick(value) {{
                if (value) {{
                    fetch(`/profile/{meterid}/consumption/${{value}}`)
                        .then(response => response.json())
                        .then(data => alert("Consumption Data: " + JSON.stringify(data)))
                        .catch(error => console.error('Error:', error));
                }}
            }}
        </script>
    </head>
    <body>
        <h1>Welcome to your profile, Meter ID: {meterid}</h1>
        <label for="dropdown">Pick Time Period:</label>
        <select id="dropdown" onchange="handleButtonClick(this.value)">
            <option value="">Select</option>
            <option value="prev_hr">Previous Half Hour</option>
            <option value="today" selected>Today</option>
            <option value="this_week">This Week</option>
            <option value="this_month">This Month</option>
            <option value="last_month">Last Month</option>
        </select>
    </body>
    </html>
    '''

@app.route('/profile/<meterid>/consumption/<time_period>', methods=['GET'])
def get_consumption(meterid, time_period):
    # Example data based on the time period (you can replace this with actual logic)
    consumption_data = {
        "prev_hr": {"usage": 5.2},
        "today": {"usage": 10.4},
        "this_week": {"usage": 70.3},
        "this_month": {"usage": 300.5},
        "last_month": {"usage": 280.1}
    }
    
    # Return the corresponding consumption data in JSON format
    return jsonify(consumption_data.get(time_period, {"usage": "Data not available"}))

if __name__ == '__main__':
    app.run(debug=True)
