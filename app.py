import os
import pandas as pd
from flask import Flask
from flask_login import LoginManager
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.security import generate_password_hash
from db import db

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the Flask-SQLAlchemy extension
db.init_app(app)

# Initialize Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'doctor_login'

# Load doctor data from CSV
doctors_df = pd.read_csv('attached_assets/doctors_indian_with_phone.csv')

# Import models after initializing db to avoid circular imports
from models import User, Doctor, Patient, Appointment, PatientHistory, SpecialtyStatistics, SymptomMapping

# Load user function for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    # Check if user_id is numeric (database id) or username string
    try:
        user_id = int(user_id)
        return User.query.get(user_id)
    except ValueError:
        # If it's not numeric, it might be a username
        return User.query.filter_by(username=user_id).first()

# Create database tables if they don't exist
with app.app_context():
    db.create_all()
    
    # Create admin user if not exists
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            password_hash=generate_password_hash('admin123'),
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()
    
    # Initialize specialty statistics if empty
    specialties = ['Cardiologist', 'Dermatologist', 'Neurologist', 'Orthopedic', 'Pediatrician', 
                  'Psychiatrist', 'Oncologist', 'Gynecologist', 'Endocrinologist', 'Ophthalmologist',
                  'ENT Specialist', 'Urologist', 'Gastroenterologist', 'Pulmonologist', 'Rheumatologist']
    
    for specialty in specialties:
        if not SpecialtyStatistics.query.filter_by(specialty=specialty).first():
            db.session.add(SpecialtyStatistics(specialty=specialty, count=0))
    
    # Add symptom mappings if empty
    symptom_mappings = {
        'chest pain': 'Cardiologist',
        'heart palpitations': 'Cardiologist',
        'shortness of breath': 'Cardiologist',
        'high blood pressure': 'Cardiologist',
        
        'skin rash': 'Dermatologist',
        'acne': 'Dermatologist',
        'eczema': 'Dermatologist',
        'psoriasis': 'Dermatologist',
        
        'headache': 'Neurologist',
        'migraines': 'Neurologist',
        'seizures': 'Neurologist',
        'dizziness': 'Neurologist',
        'memory problems': 'Neurologist',
        
        'joint pain': 'Orthopedic',
        'bone fractures': 'Orthopedic',
        'back pain': 'Orthopedic',
        'arthritis': 'Orthopedic',
        
        'fever in children': 'Pediatrician',
        'child development': 'Pediatrician',
        'childhood illnesses': 'Pediatrician',
        'vaccinations': 'Pediatrician',
        
        'depression': 'Psychiatrist',
        'anxiety': 'Psychiatrist',
        'mood disorders': 'Psychiatrist',
        'sleep problems': 'Psychiatrist',
        
        'cancer symptoms': 'Oncologist',
        'tumor': 'Oncologist',
        'chemotherapy support': 'Oncologist',
        
        'pregnancy': 'Gynecologist',
        'menstrual problems': 'Gynecologist',
        'fertility issues': 'Gynecologist',
        'pap smear': 'Gynecologist',
        
        'diabetes': 'Endocrinologist',
        'thyroid disorders': 'Endocrinologist',
        'hormone imbalance': 'Endocrinologist',
        
        'vision problems': 'Ophthalmologist',
        'eye pain': 'Ophthalmologist',
        'cataracts': 'Ophthalmologist',
        'glaucoma': 'Ophthalmologist',
        
        'ear pain': 'ENT Specialist',
        'hearing loss': 'ENT Specialist',
        'sore throat': 'ENT Specialist',
        'sinus problems': 'ENT Specialist',
        
        'urinary problems': 'Urologist',
        'kidney stones': 'Urologist',
        'prostate issues': 'Urologist',
        
        'stomach pain': 'Gastroenterologist',
        'digestive issues': 'Gastroenterologist',
        'acid reflux': 'Gastroenterologist',
        'liver problems': 'Gastroenterologist',
        
        'coughing': 'Pulmonologist',
        'asthma': 'Pulmonologist',
        'breathing difficulties': 'Pulmonologist',
        'lung disease': 'Pulmonologist',
        
        'joint inflammation': 'Rheumatologist',
        'lupus': 'Rheumatologist',
        'autoimmune disorders': 'Rheumatologist'
    }
    
    for symptom, specialist in symptom_mappings.items():
        if not SymptomMapping.query.filter_by(symptom=symptom).first():
            db.session.add(SymptomMapping(symptom=symptom, specialist=specialist))
    
    # Import doctors from CSV if no doctors exist in database
    if Doctor.query.count() == 0:
        for _, row in doctors_df.iterrows():
            doctor = Doctor(
                name=row['name'],
                specialization=row['specialization'],
                experience=row['experience'],
                phone_number=row['phone_number'],
                contact=f"{row['name'].lower().replace(' ', '.')}@mediconnect.com"
            )
            db.session.add(doctor)
    
    db.session.commit()