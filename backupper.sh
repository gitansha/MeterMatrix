#!/bin/bash

# This file serves to run the hourly backup of the in-memory data by calling the '/getmeterdata' API

if [ ! -d "daily_backup" ]; then
    mkdir "daily_backup"
fi

# Current wait time set to 30 seconds for testing purposes
sleep 30

# while true (this is the original, for loop is for testing)
# FOR loop for testing purposes
for i in 1 2
do
    echo "Backup for $(date) beginning...."

    curl -X GET "http://localhost:5000/getmeterdata" -o "daily_backup/backup.json"

    #For testing purposes
    sleep 2

    echo "Backup completed at $(date)"

    # Current wait time set to 30 seconds for testing purposes
    sleep 30
done