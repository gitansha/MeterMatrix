#!/bin/bash

# This file serves to run the daily backup of the in-memory data by calling the '/fullserverbackup' API

# Current wait time set to 70 seconds after running script for testing purposes
target_time=$(date -d "+70 seconds" +"%H:%M")
# target_time = "23:30"

while true
do
    current_time=$(date +"%H:%M")
   
    if [ "$current_time" == "$target_time" ]; then

        echo "Full Server Backup for $(date) beginning...."

        curl -X GET "http://localhost:5000/fullserverbackup"

        echo "Backup completed at $(date)"

        sleep 79200 # Sleep for 22 hours before resuming time check
    fi

    sleep 15 # check time very 15 seconds after waking up
done