#!/bin/bash

# This file serves to manually call the '/recovery' API to recovery the 2 hourly data if needed

echo "Recovery on $(date) beginning...."

curl -X GET "http://localhost:5000/recovery"

echo "Recovery completed at $(date)"