from app import db
from datetime import datetime

class Appointment(db.Model):
    __tablename__ = 'appointments'

    id = db.Column(db.Integer, primary_key=True)

    patient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)

    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default='pending', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # ✅ relationships (NO backref here)
    patient = db.relationship('User', back_populates='appointments')
    doctor = db.relationship('Doctor', back_populates='appointments')

    def __repr__(self):
        return f'<Appointment {self.id}>'
