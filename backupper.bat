@ECHO OFF

:: This file serves to run the hourly backup of the in-memory data by calling the '/getmeterdata' API

IF NOT EXIST "daily_backup" MKDIR "daily_backup"

TIMEOUT /T 30 >nul

:: :LOOP
:: FOR loop for testing purposes
FOR %%i IN (1 2) DO (

ECHO Backup for %TIME% beginning....

curl -X GET "http://localhost:5000/getmeterdata" -o "daily_backup\backup.json"

ECHO Backup completed at %TIME%

:: Current wait time set to 30 seconds for testing purposes

TIMEOUT /T 30 >nul
)
:: GOTO LOOP