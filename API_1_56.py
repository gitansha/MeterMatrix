from flask import Flask, render_template_string, jsonify, redirect, url_for, request
from datetime import datetime, timedelta

import pandas as pd
#in memory daily data (to be replaced by actual, test for now)
# df format
#           999999999  555555555  111111111  222222222  333333333
# 00:31       4.50       4.50       4.40       4.35       4.48
# 01:01       4.55       4.55       4.45       4.40       4.53
# 01:31       4.60       4.60       4.48       4.45       4.56
dailyDB = {
  999999999: {
    "00:31": 4.50, "01:01": 4.55, "01:31": 4.60, "02:01": 4.58, "02:31": 4.62,
    "03:01": 4.47, "03:31": 4.53, "04:01": 4.48, "04:31": 4.59, "05:01": 4.61,
    "05:31": 4.50, "06:01": 4.52, "06:31": 4.46, "07:01": 4.49, "07:31": 4.57,
    "08:01": 4.60, "08:31": 4.54, "09:01": 4.63, "09:31": 4.55, "10:01": 4.50,
    "10:31": 4.58, "11:01": 4.62, "11:31": 4.47, "12:01": 4.59, "12:31": 4.54,
    "13:01": 4.51, "13:31": 4.60, "14:01": 4.53, "14:31": 4.48, "15:01": 4.57,
    "15:31": 4.49, "16:01": 4.61, "16:31": 4.55, "17:01": 4.50, "17:31": 4.46,
    "18:01": 4.60, "18:31": 4.52, "19:01": 4.58
  },
  555555555: {
    "00:31": 4.50, "01:01": 4.55, "01:31": 4.60, "02:01": 4.58, "02:31": 4.62,
    "03:01": 4.47, "03:31": 4.53, "04:01": 4.48, "04:31": 4.59, "05:01": 4.61,
    "05:31": 4.50, "06:01": 4.52, "06:31": 4.46, "07:01": 4.49, "07:31": 4.57,
    "08:01": 4.60, "08:31": 4.54, "09:01": 4.63, "09:31": 4.55, "10:01": 4.50,
    "10:31": 4.58, "11:01": 4.62, "11:31": 4.47, "12:01": 4.59, "12:31": 4.54,
    "13:01": 4.51, "13:31": 4.60, "14:01": 4.53, "14:31": 4.48, "15:01": 4.57,
    "15:31": 4.49, "16:01": 4.61, "16:31": 4.55, "17:01": 4.50, "17:31": 4.46,
    "18:01": 4.60, "18:31": 4.52, "19:01": 4.58
  },
  111111111: {
    "00:31": 4.40, "01:01": 4.45, "01:31": 4.48, "02:01": 4.50, "02:31": 4.55,
    "03:01": 4.43, "03:31": 4.50, "04:01": 4.42, "04:31": 4.51, "05:01": 4.60,
    "05:31": 4.45, "06:01": 4.48, "06:31": 4.41, "07:01": 4.47, "07:31": 4.50,
    "08:01": 4.58, "08:31": 4.49, "09:01": 4.57, "09:31": 4.52, "10:01": 4.48,
    "10:31": 4.55, "11:01": 4.60, "11:31": 4.43, "12:01": 4.52, "12:31": 4.50,
    "13:01": 4.47, "13:31": 4.55, "14:01": 4.49, "14:31": 4.45, "15:01": 4.53,
    "15:31": 4.50, "16:01": 4.57, "16:31": 4.49, "17:01": 4.48, "17:31": 4.44,
    "18:01": 4.55, "18:31": 4.47, "19:01": 4.50
  },
  222222222: {
    "00:31": 4.35, "01:01": 4.40, "01:31": 4.45, "02:01": 4.47, "02:31": 4.50,
    "03:01": 4.38, "03:31": 4.46, "04:01": 4.35, "04:31": 4.48, "05:01": 4.52,
    "05:31": 4.44, "06:01": 4.45, "06:31": 4.39, "07:01": 4.41, "07:31": 4.50,
    "08:01": 4.52, "08:31": 4.48, "09:01": 4.53, "09:31": 4.46, "10:01": 4.43,
    "10:31": 4.50, "11:01": 4.55, "11:31": 4.40, "12:01": 4.47, "12:31": 4.44,
    "13:01": 4.41, "13:31": 4.49, "14:01": 4.43, "14:31": 4.38, "15:01": 4.50,
    "15:31": 4.45, "16:01": 4.52, "16:31": 4.47, "17:01": 4.42, "17:31": 4.40,
    "18:01": 4.50, "18:31": 4.44, "19:01": 4.48
  },
  333333333: {
    "00:31": 4.48, "01:01": 4.53, "01:31": 4.56, "02:01": 4.55, "02:31": 4.60,
    "03:01": 4.49, "03:31": 4.54, "04:01": 4.50, "04:31": 4.57, "05:01": 4.63,
    "05:31": 4.53, "06:01": 4.55, "06:31": 4.50, "07:01": 4.52, "07:31": 4.58,
    "08:01": 4.62, "08:31": 4.57, "09:01": 4.64, "09:31": 4.58, "10:01": 4.55,
    "10:31": 4.60, "11:01": 4.65, "11:31": 4.52, "12:01": 4.60, "12:31": 4.56,
    "13:01": 4.53, "13:31": 4.62, "14:01": 4.55, "14:31": 4.50, "15:01": 4.60,
    "15:31": 4.53, "16:01": 4.65, "16:31": 4.58, "17:01": 4.55, "17:31": 4.50,
    "18:01": 4.62, "18:31": 4.55, "19:01": 4.60
  }
}
dailyDB_df = pd.DataFrame(dailyDB)

# reading master database
# format
# columns: name, meter_id, fin_no, previous_day(dict of 47 values with timestamps), previous days
#   name   meter_id     fin_no                                       previous_day  ...     2024-12-17  2024-12-16  2024-12-15  2024-12-14
#0 Aashima  999999999  A3389127I  {'00:31': 8.33, '00:01': 4.73, '01:31': 8.7, '...  ...      250.18      121.27      266.34      198.4
masterDB_df = pd.read_json('testing_data/masterDB.json')

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

# default shows today
# need to show table and graph
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
                    if (value === 'prev_hr') {{
                        // Redirect to the new route for the previous half hour
                        window.location.href = `/profile/{meterid}/consumption/last_half_hour`;
                    }} else {{
                        // Handle other values, like fetching data via API
                        fetch(`/profile/{meterid}/consumption/${{value}}`)
                            .then(response => response.json())
                            .then(data => alert("Consumption Data: " + JSON.stringify(data)))
                            .catch(error => console.error('Error:', error));
                    }}
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


@app.route("/profile/<int:meterid>/consumption/last_half_hour", methods=["GET"])
def get_last_half_hour(meterid):
    if meterid not in dailyDB:
        return f"Meter ID {meterid} not found", 404
    
    now = datetime.now().time()
    half_hour_ago = (datetime.now() - timedelta(minutes=30)).time()

    filtered_data = {
        time_str: value
        for time_str, value in dailyDB[meterid].items()
        if half_hour_ago <= datetime.strptime(time_str, "%H:%M").time() <= now
    }

    if not filtered_data:
        return f"No data found for the last half hour for Meter ID: {meterid}", 404

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
        <h2>Previous Half Hour Consumption for Meter ID: {meterid}</h2>
        <table>
            <tr><th>Last Half Hour</th><th>Consumption</th></tr>
            <tr><td>{latest_time}</td><td>{latest_consumption}</td></tr>
        </table>
    </body>
    </html>
    """
    return render_template_string(table_html)


@app.route("/profile/<int:meterid>/consumption/today", methods=["GET"])
def get_consumption_today(meterid):
    if meterid not in dailyDB:
        return f"Meter ID {meterid} not found", 404

    data = dailyDB[meterid]
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
        <h2>Consumption Data for Meter ID: {{ meterid }}</h2>
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
    return render_template_string(table_html, meterid=meterid, data=data)


if __name__ == '__main__':
    app.run(debug=True)
