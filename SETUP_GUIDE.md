# How to Run the Hospital Appointment Booking System

## Prerequisites

Before you begin, make sure you have the following installed:

1. **Python 3.8 or higher**
   - Check version: `python --version` or `python3 --version`
   - Download from: https://www.python.org/downloads/

2. **MySQL Server**
   - Download from: https://dev.mysql.com/downloads/mysql/
   - Or use XAMPP/WAMP which includes MySQL

3. **pip** (Python package manager)
   - Usually comes with Python

## Step-by-Step Setup

### Step 1: Navigate to Project Directory

Open your terminal/command prompt and navigate to the project folder:

```bash
cd "C:\Users\Lenovo\Downloads\hospital appointment booking"
```

### Step 2: Create Virtual Environment (Recommended)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

### Step 3: Install Python Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- Flask
- Flask-SQLAlchemy
- Flask-Login
- PyMySQL
- Werkzeug

### Step 4: Setup MySQL Database

#### Option A: Using MySQL Command Line

1. Open MySQL command line or MySQL Workbench
2. Run these commands:

```sql
CREATE DATABASE hospital_booking;
```

#### Option B: Using phpMyAdmin (if using XAMPP/WAMP)

1. Open phpMyAdmin (usually at http://localhost/phpmyadmin)
2. Click "New" to create a database
3. Name it: `hospital_booking`
4. Click "Create"

### Step 5: Configure Database Connection

1. Open `config.py` file
2. Update the database connection string:

```python
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://username:password@localhost/hospital_booking'
```

**Replace:**
- `username` with your MySQL username (usually `root`)
- `password` with your MySQL password (leave empty if no password: `root:@localhost`)
- `localhost` if your MySQL is on a different host
- `hospital_booking` if you used a different database name

**Example:**
```python
# If MySQL has no password:
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root@localhost/hospital_booking'

# If MySQL has password "mypassword":
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:mypassword@localhost/hospital_booking'
```

### Step 6: Run the Application

```bash
python run.py
```

You should see output like:
```
 * Running on http://127.0.0.1:5000
 * Running on http://0.0.0.0:5000
```

### Step 7: Access the Application

Open your web browser and go to:
```
http://localhost:5000
```

## Default Login Credentials

### Admin Account
- **Email:** `admin@hospital.com`
- **Password:** `admin123`

**⚠️ Important:** Change this password after first login in production!

## First Time Setup Workflow

1. **Login as Admin** using the credentials above
2. **Add Doctors:**
   - Go to "Doctors" → "Add Doctor"
   - Fill in doctor details (name, email, password, department, specialization)
   - This creates both a user account and doctor profile

3. **Doctors Set Availability:**
   - Login as a doctor
   - Go to "Set Availability"
   - Select dates and time slots
   - Save availability

4. **Patients Book Appointments:**
   - Register as a patient
   - Browse departments and doctors
   - Select a doctor and book an appointment

## Troubleshooting

### Error: "ModuleNotFoundError: No module named 'flask'"

**Solution:** Make sure you activated the virtual environment and installed requirements:
```bash
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### Error: "Can't connect to MySQL server"

**Solutions:**
1. Make sure MySQL server is running
2. Check your MySQL credentials in `config.py`
3. Verify database exists: `SHOW DATABASES;` in MySQL

### Error: "Access denied for user"

**Solution:** Check your MySQL username and password in `config.py`

### Error: "Port 5000 already in use"

**Solution:** Change the port in `run.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

### Error: "No module named 'pymysql'"

**Solution:** Install PyMySQL:
```bash
pip install pymysql
```

### Database Tables Not Created

**Solution:** The tables are created automatically on first run. If they don't exist:
1. Make sure database connection is correct
2. Delete any existing tables and restart the app
3. Check for error messages in the terminal

## Testing the Application

1. **Test Patient Flow:**
   - Register a new patient account
   - Browse departments
   - Book an appointment
   - View and manage appointments

2. **Test Doctor Flow:**
   - Login as a doctor (created by admin)
   - Set availability for upcoming dates
   - View appointments
   - Update appointment status

3. **Test Admin Flow:**
   - Login as admin
   - Add a new doctor
   - View all appointments
   - Check dashboard statistics

## Project Structure Overview

```
hospital appointment booking/
├── app/
│   ├── models/          # Database models
│   ├── routes/          # Route handlers (controllers)
│   └── templates/       # HTML templates (views)
├── config.py            # Configuration
├── run.py              # Application entry point
├── requirements.txt    # Python dependencies
└── README.md          # Project documentation
```

## Stopping the Application

Press `Ctrl + C` in the terminal to stop the Flask server.

## Need Help?

- Check the `README.md` file for more details
- Review error messages in the terminal
- Verify all prerequisites are installed
- Ensure MySQL server is running
