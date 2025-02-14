@ECHO OFF

:: This file serves to run the daily backup of the in-memory data by calling the '/fullserverbackup' API
SET target_time=23:30

:LOOP
    FOR /f "tokens=1-2 delims=:" %%a IN ("%TIME%") DO (
        SET current_time=%%a:%%b
    )

    IF "%current_time%"=="%target_time%" (
        ECHO Full server backup for %DATE% %TIME% beginning...
        
        curl -X GET "http://localhost:5000/fullserverbackup"

        ECHO Backup completed at %DATE% %TIME%

        TIMEOUT /T 79200 >nul
    )

    TIMEOUT /T 15 >nul

GOTO LOOP