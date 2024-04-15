@echo off
cls

echo Setting up the virtual environment...
if not exist "venv" (
    python -m venv venv
    if errorlevel 1 (
        echo Failed to create virtual environment
        goto end
    )
)

echo Activating the virtual environment...
call venv\Scripts\activate
if errorlevel 1 (
    echo Failed to activate virtual environment
    goto end
)

echo Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo Failed to install dependencies
    goto end
)

echo Running the Python script for first time...
call generate_2d_map.bat
if errorlevel 1 (
    echo Failed to run the script
    goto end
)

echo Deactivating the virtual environment...
call venv\Scripts\deactivate
if errorlevel 1 (
    echo Failed to deactivate virtual environment
    goto end
)

echo Done.

:end
pause
