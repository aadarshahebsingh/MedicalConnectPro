from flask_login import UserMixin
from db import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # admin, doctor
    
    def __repr__(self):
        return f'<User {self.username}>'

class Doctor(db.Model):
    __tablename__ = 'doctors'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    specialization = db.Column(db.String(50), nullable=False)
    experience = db.Column(db.Integer)
    phone_number = db.Column(db.String(20))
    contact = db.Column(db.String(100))  # Email or other contact info
    
    # Relationships
    patients = db.relationship('Patient', secondary='doctor_patient', back_populates='doctors')
    appointments = db.relationship('Appointment', back_populates='doctor')
    
    def __repr__(self):
        return f'<Doctor {self.name}, {self.specialization}>'

class Patient(db.Model):
    __tablename__ = 'patients'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    symptoms = db.Column(db.Text, nullable=False)
    contact = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    doctors = db.relationship('Doctor', secondary='doctor_patient', back_populates='patients')
    appointments = db.relationship('Appointment', back_populates='patient')
    history_entries = db.relationship('PatientHistory', back_populates='patient')
    
    def __repr__(self):
        return f'<Patient {self.name}>'

# Association table for many-to-many relationship between doctors and patients
doctor_patient = db.Table('doctor_patient',
    db.Column('doctor_id', db.Integer, db.ForeignKey('doctors.id'), primary_key=True),
    db.Column('patient_id', db.Integer, db.ForeignKey('patients.id'), primary_key=True)
)

class Appointment(db.Model):
    __tablename__ = 'appointments'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False, default='scheduled')  # scheduled, completed, cancelled
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    patient = db.relationship('Patient', back_populates='appointments')
    doctor = db.relationship('Doctor', back_populates='appointments')
    
    def __repr__(self):
        return f'<Appointment {self.id}, Status: {self.status}>'

class PatientHistory(db.Model):
    __tablename__ = 'patient_history'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    doctor_name = db.Column(db.String(100), nullable=False)
    specialization = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    notes = db.Column(db.Text)
    
    # Relationships
    patient = db.relationship('Patient', back_populates='history_entries')
    
    def __repr__(self):
        return f'<PatientHistory {self.id}>'

class SpecialtyStatistics(db.Model):
    __tablename__ = 'specialty_statistics'
    
    id = db.Column(db.Integer, primary_key=True)
    specialty = db.Column(db.String(50), unique=True, nullable=False)
    count = db.Column(db.Integer, default=0)
    
    def __repr__(self):
        return f'<SpecialtyStatistics {self.specialty}: {self.count}>'

# Add a symptom mapping model to store the mapping in the database
class SymptomMapping(db.Model):
    __tablename__ = 'symptom_mappings'
    
    id = db.Column(db.Integer, primary_key=True)
    symptom = db.Column(db.String(100), unique=True, nullable=False)
    specialist = db.Column(db.String(50), nullable=False)
    
    def __repr__(self):
        return f'<SymptomMapping {self.symptom}: {self.specialist}>'