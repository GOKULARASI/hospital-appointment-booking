from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app import db
from app.models.user import User
from app.models.doctor import Doctor
from app.models.availability import Availability
from app.models.appointment import Appointment
from datetime import datetime, date, timedelta
from functools import wraps

from flask import Blueprint

doctor_bp = Blueprint('doctor', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('user_role') != 'doctor':
            flash('Please login as a doctor to access this page', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@doctor_bp.route('/dashboard')
@login_required
def dashboard():
    user_id = session.get('user_id')
    # Find doctor by user_id
    doctor = Doctor.query.filter_by(user_id=user_id).first()
    
    if not doctor:
        flash('Doctor profile not found. Please contact admin.', 'error')
        return redirect(url_for('auth.logout'))
    
    # Get upcoming appointments
    today = date.today()
    appointments = Appointment.query.filter_by(
        doctor_id=doctor.id
    ).filter(
        Appointment.date >= today
    ).order_by(Appointment.date.asc(), Appointment.time.asc()).all()
    
    return render_template('doctor/dashboard.html', doctor=doctor, appointments=appointments)

@doctor_bp.route('/availability', methods=['GET', 'POST'])
@login_required
def set_availability():
    user_id = session.get('user_id')
    doctor = Doctor.query.filter_by(user_id=user_id).first()
    
    if not doctor:
        flash('Doctor profile not found', 'error')
        return redirect(url_for('doctor.dashboard'))
    
    if request.method == 'POST':
        avail_date = request.form.get('date')
        time_slots = request.form.getlist('time_slots')
        
        if not avail_date or not time_slots:
            flash('Please select date and at least one time slot', 'error')
            return redirect(url_for('doctor.set_availability'))
        
        selected_date = datetime.strptime(avail_date, '%Y-%m-%d').date()
        
        # Remove existing availabilities for this date
        Availability.query.filter_by(doctor_id=doctor.id, date=selected_date).delete()
        
        # Add new availabilities
        for time_slot in time_slots:
            # Check if there's an appointment at this slot
            existing_appointment = Appointment.query.filter_by(
                doctor_id=doctor.id,
                date=selected_date,
                time=time_slot,
                status='pending'
            ).first()
            
            is_available = not bool(existing_appointment)
            
            availability = Availability(
                doctor_id=doctor.id,
                date=selected_date,
                time_slot=time_slot,
                is_available=is_available
            )
            db.session.add(availability)
        
        db.session.commit()
        flash('Availability updated successfully', 'success')
        return redirect(url_for('doctor.set_availability'))
        
    # Get existing availabilities for next 30 days
    today = date.today()
    availabilities = {}
    for i in range(30):
        check_date = today + timedelta(days=i)
        slots = Availability.query.filter_by(doctor_id=doctor.id, date=check_date).all()
        if slots:
            availabilities[str(check_date)] = [slot.time_slot for slot in slots if slot.is_available]
    
    # Standard time slots
    time_slots = [
        '09:00-10:00', '10:00-11:00', '11:00-12:00',
        '14:00-15:00', '15:00-16:00', '16:00-17:00'
    ]
    
    return render_template('doctor/availability.html', availabilities=availabilities, time_slots=time_slots, today=today)

@doctor_bp.route('/appointments')
@login_required
def appointments():
    user_id = session.get('user_id')
    doctor = Doctor.query.filter_by(user_id=user_id).first()
    
    if not doctor:
        flash('Doctor profile not found', 'error')
        return redirect(url_for('doctor.dashboard'))
    
    appointments = Appointment.query.filter_by(doctor_id=doctor.id).order_by(
        Appointment.date.desc(), Appointment.time.desc()
    ).all()
    
    return render_template('doctor/appointments.html', appointments=appointments)

@doctor_bp.route('/update_status/<int:appointment_id>', methods=['POST'])
@login_required
def update_status(appointment_id):
    user_id = session.get('user_id')
    doctor = Doctor.query.filter_by(user_id=user_id).first()
    
    if not doctor:
        flash('Doctor profile not found', 'error')
        return redirect(url_for('doctor.dashboard'))
    
    appointment = Appointment.query.get_or_404(appointment_id)
    
    if appointment.doctor_id != doctor.id:
        flash('Unauthorized access', 'error')
        return redirect(url_for('doctor.appointments'))
    
    new_status = request.form.get('status')
    
    if new_status in ['completed', 'cancelled']:
        appointment.status = new_status
        
        # If cancelled, free up the slot
        if new_status == 'cancelled':
            availability = Availability.query.filter_by(
                doctor_id=doctor.id,
                date=appointment.date,
                time_slot=appointment.time
            ).first()
            if availability:
                availability.is_available = True
        
        db.session.commit()
        flash(f'Appointment status updated to {new_status}', 'success')
    else:
        flash('Invalid status', 'error')
    
    return redirect(url_for('doctor.appointments'))
