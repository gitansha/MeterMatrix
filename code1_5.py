# 1.5 '/profile/{meterId}/consumption' page where the user can query Aash  
# ​​​Drop down to chose between 4 queries, show table and graph: link to appropriate query API '/profile/{meterId}/consumption?period=...' 
# ​​​Default: Show today’s consumption table and graph 
# ​​​Access in memory for default table + graph 
# ​​​Need: sample in memory dictionary for testing 

# import packages (dash)
from flask import Flask, render_template
from dash import Dash, html, dash_table, dcc, callback, Output, Input
import pandas as pd
import plotly.express as px

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
print(dailyDB_df)

# reading master database
# format
# columns: name, meter_id, fin_no, previous_day(dict of 47 values with timestamps), previous days
#   name   meter_id     fin_no                                       previous_day  ...     2024-12-17  2024-12-16  2024-12-15  2024-12-14
#0 Aashima  999999999  A3389127I  {'00:31': 8.33, '00:01': 4.73, '01:31': 8.7, '...  ...      250.18      121.27      266.34      198.4
masterDB_df = pd.read_json('testing_data/masterDB.json')

# # dash inside flask
# server = Flask(__name__)
# app = Dash(__name__, server=server, routes_pathname_prefix='/dash/')


