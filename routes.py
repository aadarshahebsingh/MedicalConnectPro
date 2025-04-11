import uuid
import datetime
from flask import render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from app import app, app_data, doctors_df
from models import User, Patient, Appointment
from utils import match_symptoms_to_specialist

# Home/Index route
@app.route('/')
def index():
    return render_template('index.html')

# Patient dashboard route
@app.route('/patient', methods=['GET', 'POST'])
def patient_dashboard():
    if request.method == 'POST':
        # Generate a unique ID for the patient
        patient_id = str(uuid.uuid4())
        
        # Collect patient data
        name = request.form.get('name')
        age = request.form.get('age')
        gender = request.form.get('gender')
        symptoms = request.form.get('symptoms')
        contact = request.form.get('contact')
        
        # Create new patient record
        new_patient = {
            'id': patient_id,
            'name': name,
            'age': age,
            'gender': gender,
            'symptoms': symptoms,
            'contact': contact,
            'assigned_doctor': None,
            'history': []
        }
        
        # Store patient data
        app_data['patients'][patient_id] = new_patient
        
        # Store patient ID in session
        session['patient_id'] = patient_id
        
        # Determine specialist based on symptoms
        specialist = match_symptoms_to_specialist(symptoms, app_data['symptom_to_specialist'])
        
        # Filter doctors by specialization
        recommended_doctors = doctors_df[doctors_df['specialization'] == specialist]
        
        if recommended_doctors.empty:
            flash('No matching specialists found for your symptoms. Please try with different symptoms.', 'warning')
            return redirect(url_for('patient_dashboard'))
        
        # Convert to dictionary for template
        doctors_list = recommended_doctors.to_dict('records')
        
        # Update specialty statistics
        app_data['specialty_stats'][specialist] += 1
        
        return render_template('recommended_doctors.html', 
                               doctors=doctors_list, 
                               specialist=specialist, 
                               symptoms=symptoms)
    
    return render_template('patient_dashboard.html')

# Doctor profile route
@app.route('/doctor/<doctor_id>')
def doctor_profile(doctor_id):
    doctor = None
    for _, row in doctors_df.iterrows():
        if str(row['id']) == doctor_id:
            doctor = row.to_dict()
            break
    
    if not doctor:
        flash('Doctor not found', 'error')
        return redirect(url_for('patient_dashboard'))
    
    return render_template('doctor_profile.html', doctor=doctor)

# Select doctor route
@app.route('/select_doctor/<doctor_id>', methods=['POST'])
def select_doctor(doctor_id):
    patient_id = session.get('patient_id')
    
    if not patient_id or patient_id not in app_data['patients']:
        flash('Patient session expired or invalid', 'error')
        return redirect(url_for('patient_dashboard'))
    
    # Get doctor and patient data
    doctor = None
    for _, row in doctors_df.iterrows():
        if str(row['id']) == doctor_id:
            doctor = row.to_dict()
            break
    
    if not doctor:
        flash('Doctor not found', 'error')
        return redirect(url_for('patient_dashboard'))
    
    # Assign doctor to patient
    patient = app_data['patients'][patient_id]
    patient['assigned_doctor'] = doctor_id
    
    # Add patient to doctor's list
    if doctor_id in app_data['doctors']:
        app_data['doctors'][doctor_id]['patients'].append(patient_id)
    
    # Create an appointment
    appointment_id = str(uuid.uuid4())
    new_appointment = {
        'id': appointment_id,
        'patient_id': patient_id,
        'doctor_id': doctor_id,
        'date': datetime.datetime.now().strftime('%Y-%m-%d'),
        'status': 'scheduled',
        'notes': ''
    }
    
    app_data['appointments'].append(new_appointment)
    
    # Add to patient history
    patient['history'].append({
        'date': datetime.datetime.now().strftime('%Y-%m-%d'),
        'doctor': doctor['name'],
        'specialization': doctor['specialization'],
        'status': 'Consultation scheduled'
    })
    
    flash(f'You have successfully selected {doctor["name"]} as your doctor', 'success')
    return redirect(url_for('patient_history'))

# Patient history route
@app.route('/patient/history')
def patient_history():
    patient_id = session.get('patient_id')
    
    if not patient_id or patient_id not in app_data['patients']:
        flash('Patient session expired or invalid', 'error')
        return redirect(url_for('patient_dashboard'))
    
    patient = app_data['patients'][patient_id]
    
    # Get assigned doctor details
    assigned_doctor = None
    if patient['assigned_doctor']:
        doctor_id = patient['assigned_doctor']
        for _, row in doctors_df.iterrows():
            if str(row['id']) == doctor_id:
                assigned_doctor = row.to_dict()
                break
    
    return render_template('patient_history.html', 
                           patient=patient, 
                           doctor=assigned_doctor)

# Doctor login route
@app.route('/doctor/login', methods=['GET', 'POST'])
def doctor_login():
    if request.method == 'POST':
        doctor_id = request.form.get('doctor_id')
        password = request.form.get('password')
        
        if doctor_id in app_data['users'] and app_data['users'][doctor_id]['role'] == 'doctor':
            # In a real app, we would use proper password hashing
            if app_data['users'][doctor_id]['password'] == password:
                user = User(
                    id=doctor_id,
                    username=app_data['users'][doctor_id]['username'],
                    role='doctor'
                )
                login_user(user)
                return redirect(url_for('doctor_dashboard'))
            else:
                flash('Invalid password', 'error')
        else:
            flash('Doctor ID not found', 'error')
    
    return render_template('doctor_login.html')

# Doctor dashboard route
@app.route('/doctor/dashboard')
@login_required
def doctor_dashboard():
    if current_user.role != 'doctor':
        flash('Access denied: Doctor privileges required', 'error')
        return redirect(url_for('index'))
    
    doctor_id = current_user.id
    doctor = app_data['doctors'].get(doctor_id)
    
    if not doctor:
        flash('Doctor profile not found', 'error')
        return redirect(url_for('index'))
    
    # Get patients assigned to this doctor
    assigned_patients = []
    for patient_id in doctor['patients']:
        if patient_id in app_data['patients']:
            assigned_patients.append(app_data['patients'][patient_id])
    
    # Get appointments for this doctor
    doctor_appointments = [apt for apt in app_data['appointments'] 
                         if apt['doctor_id'] == doctor_id]
    
    return render_template('doctor_dashboard.html', 
                           doctor=doctor, 
                           patients=assigned_patients,
                           appointments=doctor_appointments)

# Admin login route
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username in app_data['users'] and app_data['users'][username]['role'] == 'admin':
            # In a real app, we would use proper password hashing
            if app_data['users'][username]['password'] == password:
                user = User(
                    id=username,
                    username=username,
                    role='admin'
                )
                login_user(user)
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Invalid password', 'error')
        else:
            flash('Admin username not found', 'error')
    
    return render_template('admin_login.html')

# Admin dashboard route
@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('Access denied: Admin privileges required', 'error')
        return redirect(url_for('index'))
    
    # Get specialty statistics for the admin dashboard
    specialty_stats = app_data['specialty_stats']
    
    # Get total patients
    total_patients = len(app_data['patients'])
    
    # Get total appointments
    total_appointments = len(app_data['appointments'])
    
    # Get appointment status breakdown
    appointment_stats = {
        'scheduled': len([a for a in app_data['appointments'] if a['status'] == 'scheduled']),
        'completed': len([a for a in app_data['appointments'] if a['status'] == 'completed']),
        'cancelled': len([a for a in app_data['appointments'] if a['status'] == 'cancelled'])
    }
    
    return render_template('admin_dashboard.html', 
                           specialty_stats=specialty_stats,
                           total_patients=total_patients,
                           total_appointments=total_appointments,
                           appointment_stats=appointment_stats)

# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

# Update appointment status route
@app.route('/update_appointment/<appointment_id>', methods=['POST'])
@login_required
def update_appointment(appointment_id):
    if current_user.role != 'doctor':
        flash('Access denied: Doctor privileges required', 'error')
        return redirect(url_for('index'))
    
    # Find the appointment
    appointment = None
    for apt in app_data['appointments']:
        if apt['id'] == appointment_id:
            appointment = apt
            break
    
    if not appointment:
        flash('Appointment not found', 'error')
        return redirect(url_for('doctor_dashboard'))
    
    # Update status
    new_status = request.form.get('status')
    notes = request.form.get('notes', '')
    
    appointment['status'] = new_status
    appointment['notes'] = notes
    
    # Update patient history
    patient_id = appointment['patient_id']
    if patient_id in app_data['patients']:
        patient = app_data['patients'][patient_id]
        
        # Get doctor name
        doctor_name = "Unknown Doctor"
        doctor_id = appointment['doctor_id']
        if doctor_id in app_data['doctors']:
            doctor_name = app_data['doctors'][doctor_id]['name']
        
        # Add to history
        patient['history'].append({
            'date': datetime.datetime.now().strftime('%Y-%m-%d'),
            'doctor': doctor_name,
            'status': f'Appointment {new_status}',
            'notes': notes
        })
    
    flash('Appointment updated successfully', 'success')
    return redirect(url_for('doctor_dashboard'))
