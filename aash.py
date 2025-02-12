import json
from flask import Flask, render_template_string
from datetime import datetime, timedelta

# Open and read the JSON file
with open('testing_data/masterDB.json', 'r') as file:
    masterDB_dict = json.load(file)  # Load JSON data into a dictionary


app = Flask(__name__)


def get_current_week_dates():
    """Return a list of date strings for the current week (Monday through Sunday)."""
    today = datetime.today().date()
    start_of_week = today - timedelta(days=today.weekday())  # Monday
    return [(start_of_week + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]

@app.route("/profile/<int:meterid>/consumption/this_week", methods=["GET"])
def consumption_this_week(meterid):
    meterid_str = str(meterid)
    if meterid_str not in masterDB_dict:
        return f"Meter ID {meterid} not found", 404

    # Get the list of dates for the current week
    week_dates = get_current_week_dates()

    # Filter the weekly data from the meter record; ignore keys that are not valid dates.
    weekly_data = {}
    for date_str, value in masterDB_dict[meterid_str].items():
        try:
            # Only process keys that look like dates (YYYY-MM-DD)
            datetime.strptime(date_str, "%Y-%m-%d")
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
    table_html += """
        </table>
        <br>
        <canvas id="consumptionChart" width="600" height="300"></canvas>
        <script>
            var ctx = document.getElementById('consumptionChart').getContext('2d');
            var chart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: """ + str(sorted_dates) + """,
                    datasets: [{
                        label: 'Consumption',
                        data: """ + str(sorted_values) + """,
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
    return render_template_string(table_html)

if __name__ == '__main__':
    app.run(debug=True)
