from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app import db
from app.models.user import User
from app.models.doctor import Doctor
from app.models.availability import Availability
from app.models.appointment import Appointment
from datetime import date
from functools import wraps
from sqlalchemy import func

admin_bp = Blueprint('admin', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('user_role') != 'admin':
            flash('Please login as an admin to access this page', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    # Statistics
    total_appointments = Appointment.query.count()
    pending_appointments = Appointment.query.filter_by(status='pending').count()
    completed_appointments = Appointment.query.filter_by(status='completed').count()
    cancelled_appointments = Appointment.query.filter_by(status='cancelled').count()
    total_doctors = Doctor.query.count()
    total_patients = User.query.filter_by(role='patient').count()
    
    # Recent appointments
    recent_appointments = Appointment.query.order_by(
        Appointment.created_at.desc()
    ).limit(10).all()
    
    # Appointments by status (for chart)
    status_counts = {
        'pending': pending_appointments,
        'completed': completed_appointments,
        'cancelled': cancelled_appointments
    }
    
    return render_template('admin/dashboard.html',
                         total_appointments=total_appointments,
                         pending_appointments=pending_appointments,
                         completed_appointments=completed_appointments,
                         cancelled_appointments=cancelled_appointments,
                         total_doctors=total_doctors,
                         total_patients=total_patients,
                         recent_appointments=recent_appointments,
                         status_counts=status_counts)

@admin_bp.route('/doctors')
@login_required
def doctors():
    doctors_list = Doctor.query.all()
    return render_template('admin/doctors.html', doctors=doctors_list)

@admin_bp.route('/doctors/add', methods=['GET', 'POST'])
@login_required
def add_doctor():
    if request.method == 'POST':
        name = request.form.get('name')
        department = request.form.get('department')
        specialization = request.form.get('specialization')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not all([name, department, specialization, email, password]):
            flash('All fields are required', 'error')
            return render_template('admin/add_doctor.html')
        
        # Check if user with email exists
        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'error')
            return render_template('admin/add_doctor.html')
        
        # Create user for doctor
        from werkzeug.security import generate_password_hash
        user = User(
            name=name,
            email=email,
            password=generate_password_hash(password),
            role='doctor'
        )
        db.session.add(user)
        db.session.flush()  # Get user.id
        
        # Create doctor
        doctor = Doctor(
            name=name,
            department=department,
            specialization=specialization,
            user_id=user.id
        )
        db.session.add(doctor)
        db.session.commit()
        
        flash('Doctor added successfully', 'success')
        return redirect(url_for('admin.doctors'))
    
    # Get unique departments
    departments = db.session.query(Doctor.department).distinct().all()
    departments = [dept[0] for dept in departments]
    return render_template('admin/add_doctor.html', departments=departments)

@admin_bp.route('/doctors/edit/<int:doctor_id>', methods=['GET', 'POST'])
@login_required
def edit_doctor(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    
    if request.method == 'POST':
        doctor.name = request.form.get('name')
        doctor.department = request.form.get('department')
        doctor.specialization = request.form.get('specialization')
        
        db.session.commit()
        flash('Doctor updated successfully', 'success')
        return redirect(url_for('admin.doctors'))
    
    # Get unique departments
    departments = db.session.query(Doctor.department).distinct().all()
    departments = [dept[0] for dept in departments]
    return render_template('admin/edit_doctor.html', doctor=doctor, departments=departments)

@admin_bp.route('/doctors/delete/<int:doctor_id>')
@login_required
def delete_doctor(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    
    # Check if doctor has appointments
    appointments = Appointment.query.filter_by(doctor_id=doctor_id).count()
    if appointments > 0:
        flash('Cannot delete doctor with existing appointments', 'error')
        return redirect(url_for('admin.doctors'))
    
    # Delete user if exists
    if doctor.user_id:
        user = User.query.get(doctor.user_id)
        if user:
            db.session.delete(user)
    
    db.session.delete(doctor)
    db.session.commit()
    
    flash('Doctor deleted successfully', 'success')
    return redirect(url_for('admin.doctors'))

@admin_bp.route('/departments')
@login_required
def departments():
    # Get unique departments with doctor count
    departments_data = db.session.query(
        Doctor.department,
        func.count(Doctor.id).label('doctor_count')
    ).group_by(Doctor.department).all()
    
    departments = [{'name': dept[0], 'count': dept[1]} for dept in departments_data]
    return render_template('admin/departments.html', departments=departments)

@admin_bp.route('/departments/add', methods=['POST'])
@login_required
def add_department():
    department_name = request.form.get('department_name')
    
    if not department_name:
        flash('Department name is required', 'error')
        return redirect(url_for('admin.departments'))
    
    # Check if department exists
    existing = Doctor.query.filter_by(department=department_name).first()
    if existing:
        flash('Department already exists', 'info')
        return redirect(url_for('admin.departments'))
    
    flash('Department will be created when you add a doctor to it', 'info')
    return redirect(url_for('admin.departments'))

@admin_bp.route('/appointments')
@login_required
def appointments():
    appointments_list = Appointment.query.order_by(
        Appointment.date.desc(), Appointment.time.desc()
    ).all()
    return render_template('admin/appointments.html', appointments=appointments_list)
