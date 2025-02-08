# MeterMatrix

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

### 1.2 Daily In Memory Data
This data structure (nested dictionary) is maintained by our `API.py` program. It stores all half-hourly readings from all meters for the current day and refreshes at `00:00`.  

At the end of the day, this data structure is used to update our master database, which contains all readings from all meters across all days. Once the data is updated to the master database, it gets refreshed (blanked) to store the next day's data.

Each meter will have 47 readings a day.
Python Nested Dictionary
```json
{
  "<meter_id_1>": {
    "00:31": <reading_kWh>,
    "23:31": <reading_kWh>,
  },
  "999999999": {
    "00:31": 4.50,
    ...
    "23:31": 4.35
  },
  "555555555": {
    "00:31": 4.50,
    "23:31": 4.35
  }
}
```

### 1.3 Recovery JSON for 1.2
The Recovery JSON is a backup file for the daily data structure described in section 1.2. This file is updated every two hours as a safeguard against data loss.

Same format as 1.2.

### 1.4 Master Database
The master database contains all the data from all the meters, including the meter ID, energy consumption for each day, and the previous day's half-hourly consumption data (structured in the same way as described in section 1.2.). We store the previous day's half-hourly consumption data in case the user needs to query it.

JSON file (text file storing data)
```json
{
  "999999999": {
    "previous_day": {
      "00:31": 4.50,
      "23:31": 4.35
    },
    "day_wise_consumption": {
      "2025-02-07": 161.50,
      "2025-02-06": 157.50
    }
  },
  "555555555": {
    "previous_day": {
      "00:31": 4.50,
      "23:31": 4.35
    },
    "day_wise_consumption": {
      "2025-02-07": 161.50,
      "2025-02-06": 157.50
    }
  }
}
```



## How to run the file
1. Create a vitual env by going to the desired directory and doing `pip install virtualenv` followed by `virtualenv venv`.
2. Activate the env using the initially going to the directory using cd
    eg: 'cd <location to git repo>/venv/Scripts'
    `./activate` 
    (to check if your env  got activated or not, **(venv)** shoould appear before your path in the cmd.)
    **Note please do it in the cmd and not powershell because i only know hiw to get it working**
3. to install the libraries, get out of the venv and back to the root folder and do a `pip install -r requirements.txt` (one time requirment only)
    (Also this is for windows, Sorry Mac Users)
4. To check if you got the required poackages, do a `pip list`.
5. Now run the file normally using python ./file_name.py


