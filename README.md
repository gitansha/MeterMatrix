# MeterMatrix

## Table of Contents

1. [Data Structures](#1-data-structures)
   1. [Meter Reading (JSON packet)](#11-meter-reading-json-packet)
   2. [Daily In Memory Data](#12-daily-in-memory-data)
   3. [Daily Recovery JSON for 1.2](#13-daily-recovery-json-for-12)
   4. [Master Database](#14-master-database)
2. [Data Collection, Storage, and Backup Process](#2-data-collection-storage-and-backup-process)
   1. [Every Half an Hour](#21-every-half-an-hour)
   2. [Every 2 Hours](#22-every-2-hours)
   3. [End of the Day (23:31 to 23:59)](#23-end-of-the-day-2331-to-2359)
3. [API Documentation](#3-api-documentation)

---

## 1 Data Structures

### 1.1 Meter Reading (JSON packet)
This is the JSON packet a meter sends to the server every half hour when accessing the `/meter` API endpoint.  

A packet arriving at `00:31` indicates electricity consumption from `00:00` to `00:30`. The meter transmits data every half hour, from `00:31` to `23:31`, with no packets received between `23:30` and `00:00` due to backup operations. As a result, each meter sends **47 packets per day**.  

Our API expects the following format and will be coded accordingly.

JSON file (text file storing data)

```json
{
  "id": 999999999,
  "timestamp": "2025-02-08T00:31:00Z",
  "reading_kWh": 5.5
}
```
km,
### 1.2 Daily In Memory Data
This data structure (nested dictionary) is maintained by our `API.py` program. It stores all half-hourly readings from all meters for the current day and refreshes at `00:00`.  

At the end of the day, this data structure is used to update our master database, which contains all readings from all meters across all days. Once the data is updated to the master database, it gets refreshed (blanked) to store the next day's data.

Each meter will have 47 readings a day.
Python Nested Dictionary
```json
{
  "<meter_id_1>": {
    "00:31": "<reading_kWh>",
    "23:31": "<reading_kWh>",
  },
  "999999999": {
    "00:31": 4.50,
    "23:31": 4.35
  },
  "555555555": {
    "00:31": 4.50,
    "23:31": 4.35
  }
}
```

### 1.3 Daily Recovery JSON for 1.2
The Recovery JSON is a backup file for the daily data structure described in section 1.2. This file is updated every two hours as a safeguard against data loss.

Same format as 1.2.

### 1.4 Master Database
The master database contains all the data from all the meters, including the meter ID, energy consumption for each day, and the previous day's half-hourly consumption data (structured in the same way as described in section 1.2.). We store the previous day's half-hourly consumption data in case the user needs to query it. Dates are acting as keys for single value consumptions.

JSON file (text file storing data)
```json

{
  "999999999": {
    "name": "Aashima",
    "fin_no": "A3389127I",
    "previous_day": {
      "00:31": 8.33,
      "00:01": 4.73,
      "01:31": 8.7,
      "23:31": 2.59
    },
    "2025-02-11": 187.14,
    "2025-01-23": 177.93,
    "2025-01-22": 219.14,
    "2024-12-14": 198.41
  },
  "555555555": {
    "name": "Carlos",
    "fin_no": "A1234567I",
    "previous_day": {
      "00:31": 5.99,
      "22:01": 3.64,
      "23:31": 6.74
    },
    "2025-02-11": 112.96,
    "2025-02-10": 158.12,
  }
}

```

---


## 2 Data Collection, Storage, and Backup Process

### 2.1 Every Half an Hour
For every meter:
1. The API receives a JSON packet (refer to data structure 1.1) and stores it in a JSON packet class.
2. This JSON packet is then added to the Daily In Memory Data (data structure 1.2).

### 2.2 Every 2 Hours
1. The Daily In Memory Data (data structure 1.2) is flushed into the Daily Recovery JSON (data structure 1.3) as a backup.

### 2.3 End of the Day (23:31 to 23:59)
This is done to prepare our API for the next day.

For each meter,
1. Aggregate the day's consumption using the Daily In Memory Data (data structure 1.2).
2. Update the Master Database (data structure 1.4) with the current day's date and the aggregated sum from step 1.

Overall,
1. The Daily In Memory Data (data structure 1.2) is then flushed into the Master Database's previous_day field (data structure 1.4), resetting it for the next day's data collection.

---

## 3 API Documentation

| **Route**                                          | **Description**                                                                                   |
|----------------------------------------------------|---------------------------------------------------------------------------------------------------|
| `/`                                                | Landing page which shows options between new user or existing user.                               |
| `/register`                                        | Add a new user.                                                                                  |
| `/profile`                                         | Existing user enters their meter ID.                                                              |
| `/profile/{meterId}`                               | Landing page for that particular meter ID.                                                        |
| `/profile/{meterId}/consumption`                   | Displays consumption details for the meter ID.                                                     |
| `/profile/{meterId}/consumption?period=...`        | Query data by time period (e.g., `prev-hr`, `current-day`, `current-week`, `current-month`, `prev-month`) and also show graphs. |
| `/meter`                                           | Meter accesses this API and sends a JSON packet consisting of its ID, consumption in the previous half hour, and timestamp. |
| **Example:** `/profile/999-999-999`                 | This is an example of how to query a specific meter's profile.                                    |
| `/management-dashboard/`                            | Management dashboard to view the region wise consumption                                          |


## How to run the file locally and install required libraries
1. Create a vitual env by going to the desired directory and doing `pip install virtualenv` followed by `virtualenv venv`.
2. Activate the env using the initially going to the directory using cd
    eg: 'cd <location to git repo>/venv/Scripts'
    `./activate` 
    (to check if your env  got activated or not, **(venv)** shoould appear before your path in the cmd.)
    **Note please do it in the cmd and not powershell because i only know hiw to get it working**
3. to install the libraries, get out of the venv and back to the root folder and do a `pip install -r requirements.txt` (one time requirment only)
    (Also this is for windows, Sorry Mac Users)
4. To check if you got the required poackages, do a `pip list`.

## How to run the Server
1.  Run `python API.py`.
2.	Open in local host browser.
3.	For user login use ‘999999999’ for testing purposes. Can refer to file `testing_data/masterDB.json` to refer to test data.
4.	To check management dashboard: Add `/management-dashboard/` at the end of the link of landing page
5.	For meter and backup: Make sure API.py is running first and then run `meterlogger.py `


