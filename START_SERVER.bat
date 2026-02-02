@echo off
echo ================================
echo  PDF Editor Web App
echo ================================
echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Starting Flask development server...
echo.
echo The app will be available at:
echo   http://localhost:5000
echo.
echo Press CTRL+C to stop the server
echo.

python app.py

pause
