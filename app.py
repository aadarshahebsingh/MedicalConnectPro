import os
import pandas as pd
from flask import Flask
from flask_login import LoginManager
from werkzeug.middleware.proxy_fix import ProxyFix

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Initialize Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'doctor_login'

# Load doctor data from CSV
doctors_df = pd.read_csv('attached_assets/doctors_indian_with_phone.csv')

# In-memory storage for application data
# This would be replaced with a database in production
app_data = {
    'users': {
        'admin': {
            'username': 'admin',
            'password': 'admin123',  # This would be hashed in production
            'role': 'admin'
        }
    },
    'doctors': {},
    'patients': {},
    'appointments': [],
    'symptom_to_specialist': {
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
        'autoimmune disorders': 'Rheumatologist',
        'lupus': 'Rheumatologist',
        'rheumatoid arthritis': 'Rheumatologist'
    }
}

# Initialize doctor user accounts from CSV data
for _, doctor in doctors_df.iterrows():
    doctor_id = str(doctor['id'])
    # Create user account entry
    app_data['users'][doctor_id] = {
        'username': doctor_id,
        'password': doctor_id + '123',  # Simple default password, would be hashed in production
        'role': 'doctor'
    }
    
    # Store doctor details
    app_data['doctors'][doctor_id] = {
        'id': doctor_id,
        'name': doctor['name'],
        'specialization': doctor['specialization'],
        'contact': doctor['contact'],
        'experience': doctor['experience'],
        'phone_number': doctor['phone_number'],
        'patients': []  # Track patients for this doctor
    }

# Specialty statistics counters
app_data['specialty_stats'] = {spec: 0 for spec in doctors_df['specialization'].unique()}

from models import User

@login_manager.user_loader
def load_user(user_id):
    if user_id in app_data['users']:
        user_data = app_data['users'][user_id]
        return User(
            id=user_id,
            username=user_data['username'],
            role=user_data['role']
        )
    return None
