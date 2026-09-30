PREDICTX - COMPLETE PROJECT
===========================

PROJECT FOLDER
--------------
C:\PredictX_Final

SETUP
-----
1. Open PowerShell:
   cd C:\PredictX_Final

2. Create Python 3.11 virtual environment:
   C:\Users\nandh\AppData\Local\Programs\Python\Python311\python.exe -m venv lstm_env

3. Activate:
   .\lstm_env\Scripts\Activate.ps1

4. Install packages:
   python -m pip install -r requirements.txt

5. Initialize database and default machines:
   python database\database.py
   python database\insert_machines.py

6. Start the app:
   python -m streamlit run app.py

7. Open:
   http://localhost:8501

ADMIN
-----
1. Register a normal account in PredictX.
2. Stop Streamlit if needed.
3. Run:
   python make_admin.py
4. Enter the registered email.
5. Start Streamlit again and login with that account.
6. The Admin button will appear in the sidebar.

REGISTRATION ERROR FIX
----------------------
The registration page does not manually modify st.session_state widget keys
such as register_name after creating the widgets. This prevents the error:
"st.session_state.register_name cannot be modified after the widget with key
register_name is instantiated."

DATABASE
--------
SQLite database file:
C:\PredictX_Final\database\predictx.db

Tables:
- users
- machines
- sensor_data
- predictions
- maintenance

Admin Dashboard can view registered users, machines, predictions and
maintenance records. Admin can also add/delete machines and generate PDF
machine reports.

PROJECT NOTE
------------
This is a software prototype. Physical sensors are not connected. Sensor
values are supplied through the CSV dataset or simulated manually. For a real-
time version, physical temperature/vibration/speed sensors can send data via
an IoT device to the application.

The supplied demo dataset has no true failure labels or real RUL targets.
Therefore Health Score and RUL are prototype estimates, not industrially
validated predictions.
