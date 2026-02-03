from app import db

class Availability(db.Model):
    __tablename__ = 'availability'
    
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time_slot = db.Column(db.String(50), nullable=False)  # e.g., "09:00-10:00"
    is_available = db.Column(db.Boolean, default=True, nullable=False)
    
    # Unique constraint to prevent duplicate slots
    __table_args__ = (db.UniqueConstraint('doctor_id', 'date', 'time_slot', name='unique_doctor_slot'),)
    
    def __repr__(self):
        return f'<Availability {self.doctor_id} - {self.date} {self.time_slot}>'
