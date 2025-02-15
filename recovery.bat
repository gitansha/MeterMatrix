@ECHO OFF

:: This file serves to manually call the '/recovery' API to recovery the 2 hourly data if needed

ECHO Recovery on %TIME% beginning....

curl -X GET "http://localhost:5000/recovery"

ECHO Recovery completed at %TIME%
