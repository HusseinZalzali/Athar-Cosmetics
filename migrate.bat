@echo off
REM Migration script for backend (Windows)

echo Initializing database...
flask db init

echo Creating migration...
flask db migrate -m "Initial migration"

echo Applying migration...
flask db upgrade

echo Seeding database...
python seed.py

echo Done!




