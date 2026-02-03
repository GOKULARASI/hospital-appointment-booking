# Hospital Appointment Booking System

A comprehensive web application for managing hospital appointments with support for Patients, Doctors, and Administrators.

## Features

### Patient Features
- User registration and login
- View departments and doctors
- Book appointments by selecting date and available time slots
- View all appointments
- Cancel appointments
- Reschedule appointments
- Receive booking confirmation messages

### Doctor Features
- Login to doctor account
- Set availability (date & time slots)
- View upcoming appointments
- Update appointment status (completed/cancelled)

### Admin Features
- Login to admin account
- Add, update, and delete doctors
- Manage departments
- View all appointments
- Dashboard with appointment statistics

## Tech Stack

- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **Backend**: Python Flask
- **Database**: MySQL (using SQLAlchemy ORM)
- **Authentication**: Session-based login
- **Architecture**: MVC pattern

## Project Structure

```
hospital appointment booking/
├── app/
│   ├── __init__.py          # Flask app initialization
│   ├── models/              # Database models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── doctor.py
│   │   ├── availability.py
│   │   └── appointment.py
│   ├── routes/              # Route handlers
│   │   ├── auth.py
│   │   ├── patient.py
│   │   ├── doctor.py
│   │   └── admin.py
│   ├── templates/           # HTML templates
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── auth/
│   │   ├── patient/
│   │   ├── doctor/
│   │   └── admin/
│   └── static/              # CSS, JS, images
├── config.py                # Configuration
├── run.py                   # Application entry point
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Database Schema

### Tables

1. **users**
   - id (Primary Key)
   - name
   - email (Unique)
   - password (Hashed)
   - role (patient/doctor/admin)

2. **doctors**
   - id (Primary Key)
   - name
   - department
   - specialization
   - user_id (Foreign Key to users)

3. **availability**
   - id (Primary Key)
   - doctor_id (Foreign Key to doctors)
   - date
   - time_slot
   - is_available (Boolean)

4. **appointments**
   - id (Primary Key)
   - patient_id (Foreign Key to users)
   - doctor_id (Foreign Key to doctors)
   - date
   - time
   - status (pending/completed/cancelled)
   - created_at

## Installation & Setup

### Prerequisites

- Python 3.8 or higher
- MySQL Server
- pip (Python package manager)

### Step 1: Clone or Download the Project

Navigate to the project directory:
```bash
cd "hospital appointment booking"
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Setup MySQL Database

1. Start MySQL server
2. Create a new database:
```sql
CREATE DATABASE hospital_booking;
```

3. Update database credentials in `config.py`:
```python
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://username:password@localhost/hospital_booking'
```
Replace `username` and `password` with your MySQL credentials.

### Step 5: Run the Application

```bash
python run.py
```

The application will be available at `http://localhost:5000`

## Default Admin Account

- **Email**: admin@hospital.com
- **Password**: admin123

**Note**: Change the admin password after first login in production!

## Usage Guide

### For Patients

1. Register a new account or login
2. Browse departments and doctors
3. Select a doctor and book an appointment
4. View, cancel, or reschedule appointments from the dashboard

### For Doctors

1. Login with doctor credentials (created by admin)
2. Set your availability for upcoming dates
3. View upcoming appointments
4. Update appointment status (mark as completed or cancel)

### For Administrators

1. Login with admin credentials
2. Add new doctors with their credentials
3. Manage departments
4. View all appointments and statistics
5. Edit or delete doctor profiles

## Important Notes

- The application uses session-based authentication
- Passwords are hashed using Werkzeug's password hashing
- Time slots are in format "HH:MM-HH:MM" (e.g., "09:00-10:00")
- Appointments can only be booked for available time slots
- Cancelled appointments free up the time slot automatically

## Security Considerations

For production deployment:

1. Change the `SECRET_KEY` in `config.py`
2. Use environment variables for sensitive data
3. Implement stronger password requirements
4. Add rate limiting for login attempts
5. Use HTTPS
6. Regularly update dependencies
7. Implement proper error handling and logging

## Troubleshooting

### Database Connection Error

- Verify MySQL server is running
- Check database credentials in `config.py`
- Ensure database exists

### Module Not Found Error

- Activate virtual environment
- Run `pip install -r requirements.txt` again

### Port Already in Use

- Change port in `run.py`: `app.run(port=5001)`

## License

This project is open source and available for educational purposes.

## Support

For issues or questions, please check the code comments or create an issue in the repository.
