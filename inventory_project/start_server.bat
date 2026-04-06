@echo off
cd /d "C:\Inventory2026\inventory_project"
call "C:\Inventory2026\.venv\Scripts\activate"
python manage.py runserver 0.0.0.0:8000