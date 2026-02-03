from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app import db
from app.models.user import User
from app.models.doctor import Doctor
from app.models.availability import Availability
from app.models.appointment import Appointment
from datetime import datetime, date, timedelta
from functools import wraps

patient_bp = Blueprint('patient', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('user_role') != 'patient':
            flash('Please login as a patient to access this page', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@patient_bp.route('/dashboard')
@login_required
def dashboard():
    patient_id = session.get('user_id')
    appointments = Appointment.query.filter_by(patient_id=patient_id).order_by(Appointment.date.desc(), Appointment.time.desc()).all()
    return render_template('patient/dashboard.html', appointments=appointments)

@patient_bp.route('/departments')
@login_required
def departments():
    # Get unique departments
    departments = db.session.query(Doctor.department).distinct().all()
    departments = [dept[0] for dept in departments]
    return render_template('patient/departments.html', departments=departments)

@patient_bp.route('/doctors')
@login_required
def doctors():
    department = request.args.get('department')
    if department:
        doctors_list = Doctor.query.filter_by(department=department).all()
    else:
        doctors_list = Doctor.query.all()
    return render_template('patient/doctors.html', doctors=doctors_list, selected_dept=department)

@patient_bp.route('/book/<int:doctor_id>', methods=['GET', 'POST'])
@login_required
def book_appointment(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    patient_id = session.get('user_id')

    if request.method == 'POST':
        selected_date = request.form.get('date')
        selected_time = request.form.get('time_slot')
        
        if not selected_date or not selected_time:
            flash('Please select both date and time slot', 'error')
            return redirect(url_for('patient.book_appointment', doctor_id=doctor_id))
        
        # Check if slot is still available
        availability = Availability.query.filter_by(
            doctor_id=doctor_id,
            date=datetime.strptime(selected_date, '%Y-%m-%d').date(),
            time_slot=selected_time,
            is_available=True
        ).first()
        
        if not availability:
            flash('This time slot is no longer available', 'error')
            return redirect(url_for('patient.book_appointment', doctor_id=doctor_id))
        
        # Check if patient already has an appointment at this time
        existing = Appointment.query.filter_by(
            patient_id=patient_id,
            date=datetime.strptime(selected_date, '%Y-%m-%d').date(),
            time=selected_time,
            status='pending'
        ).first()
        
        if existing:
            flash('You already have an appointment at this time', 'error')
            return redirect(url_for('patient.book_appointment', doctor_id=doctor_id))
        
        # Create appointment
        appointment = Appointment(
            patient_id=patient_id,
            doctor_id=doctor_id,
            date=datetime.strptime(selected_date, '%Y-%m-%d').date(),
            time=selected_time,
            status='pending'
        )
        
        # Mark availability as booked
        availability.is_available = False
        
        db.session.add(appointment)
        db.session.commit()

        flash(f'Appointment booked successfully with Dr. {doctor.name} on {selected_date} at {selected_time}', 'success')
        return redirect(url_for('patient.dashboard'))
    
    # Get available dates (next 30 days)
    today = date.today()
    available_dates = []
    for i in range(30):
        check_date = today + timedelta(days=i)
        availabilities = Availability.query.filter_by(
            doctor_id=doctor_id,
            date=check_date,
            is_available=True
        ).all()
        if availabilities:
            available_dates.append({
                'date': check_date.strftime('%Y-%m-%d'),
                'date_obj': check_date,
                'slots': [av.time_slot for av in availabilities]
            })
    
    return render_template('patient/book_appointment.html', doctor=doctor, available_dates=available_dates)

@patient_bp.route('/appointments')
@login_required
def appointments():
    patient_id = session.get('user_id')
    appointments = Appointment.query.filter_by(patient_id=patient_id).order_by(Appointment.date.desc(), Appointment.time.desc()).all()
    return render_template('patient/appointments.html', appointments=appointments)

@patient_bp.route('/cancel/<int:appointment_id>')
@login_required
def cancel_appointment(appointment_id):
    patient_id = session.get('user_id')
    appointment = Appointment.query.get_or_404(appointment_id)
    
    if appointment.patient_id != patient_id:
        flash('Unauthorized access', 'error')
        return redirect(url_for('patient.appointments'))
    
    if appointment.status == 'cancelled':
        flash('Appointment is already cancelled', 'info')
        return redirect(url_for('patient.appointments'))
    
    # Mark availability as available again
    availability = Availability.query.filter_by(
        doctor_id=appointment.doctor_id,
        date=appointment.date,
        time_slot=appointment.time
    ).first()
    
    if availability:
        availability.is_available = True
    
    appointment.status = 'cancelled'
    db.session.commit()
    
    flash('Appointment cancelled successfully', 'success')
    return redirect(url_for('patient.appointments'))

@patient_bp.route('/reschedule/<int:appointment_id>', methods=['GET', 'POST'])
@login_required
def reschedule_appointment(appointment_id):
    patient_id = session.get('user_id')
    appointment = Appointment.query.get_or_404(appointment_id)
    
    if appointment.patient_id != patient_id:
        flash('Unauthorized access', 'error')
        return redirect(url_for('patient.appointments'))
    
    if appointment.status == 'cancelled':
        flash('Cannot reschedule a cancelled appointment', 'error')
        return redirect(url_for('patient.appointments'))
    
    doctor = Doctor.query.get(appointment.doctor_id)
    
    if request.method == 'POST':
        selected_date = request.form.get('date')
        selected_time = request.form.get('time_slot')
        
        if not selected_date or not selected_time:
            flash('Please select both date and time slot', 'error')
            return redirect(url_for('patient.reschedule_appointment', appointment_id=appointment_id))
        
        # Free up old slot
        old_availability = Availability.query.filter_by(
            doctor_id=appointment.doctor_id,
            date=appointment.date,
            time_slot=appointment.time
        ).first()
        if old_availability:
            old_availability.is_available = True
        
        # Check if new slot is available
        new_availability = Availability.query.filter_by(
            doctor_id=appointment.doctor_id,
            date=datetime.strptime(selected_date, '%Y-%m-%d').date(),
            time_slot=selected_time,
            is_available=True
        ).first()
        
        if not new_availability:
            flash('This time slot is no longer available', 'error')
            return redirect(url_for('patient.reschedule_appointment', appointment_id=appointment_id))
        
        # Update appointment
        appointment.date = datetime.strptime(selected_date, '%Y-%m-%d').date()
        appointment.time = selected_time
        new_availability.is_available = False
        
        db.session.commit()
        
        flash('Appointment rescheduled successfully', 'success')
        return redirect(url_for('patient.appointments'))
    
    # Get available dates
    today = date.today()
    available_dates = []
    for i in range(30):
        check_date = today + timedelta(days=i)
        availabilities = Availability.query.filter_by(
            doctor_id=appointment.doctor_id,
            date=check_date,
            is_available=True
        ).all()
        if availabilities:
            available_dates.append({
                'date': check_date.strftime('%Y-%m-%d'),
                'date_obj': check_date,
                'slots': [av.time_slot for av in availabilities]
            })
    
    return render_template('patient/reschedule_appointment.html', appointment=appointment, doctor=doctor, available_dates=available_dates)
