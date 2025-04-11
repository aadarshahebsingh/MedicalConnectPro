import datetime
from flask import render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from app import app, doctors_df, db
from models import User, Doctor, Patient, Appointment, PatientHistory, SpecialtyStatistics, SymptomMapping
from utils import match_symptoms_to_specialist
from sqlalchemy import func

# Home/Index route
@app.route('/')
def index():
    return render_template('index.html')

# Patient dashboard route
@app.route('/patient', methods=['GET', 'POST'])
def patient_dashboard():
    if request.method == 'POST':
        # Only collect symptoms at this stage
        symptoms = request.form.get('symptoms')
        
        # Store symptoms in session for later use when creating patient record
        session['symptoms'] = symptoms
        
        # Get symptom mappings from database
        symptom_mappings = {m.symptom: m.specialist for m in SymptomMapping.query.all()}
        
        # Determine specialist based on symptoms
        specialist = match_symptoms_to_specialist(symptoms, symptom_mappings)
        
        # Store specialist in session
        session['specialist'] = specialist
        
        # Update specialty statistics
        specialty_stat = SpecialtyStatistics.query.filter_by(specialty=specialist).first()
        if specialty_stat:
            specialty_stat.count += 1
            db.session.commit()
        
        # Redirect to recommended doctors page
        return redirect(url_for('recommended_doctors'))
    
    return render_template('patient_dashboard.html')

# Recommended doctors route
@app.route('/recommended-doctors')
def recommended_doctors():
    specialist = session.get('specialist')
    symptoms = session.get('symptoms')
    
    if not specialist or not symptoms:
        flash('Please describe your symptoms first', 'warning')
        return redirect(url_for('patient_dashboard'))
    
    # Get doctors from the database based on specialization
    doctors = Doctor.query.filter_by(specialization=specialist).all()
    
    return render_template('recommended_doctors.html', 
                           doctors=doctors, 
                           specialist=specialist, 
                           symptoms=symptoms)

# Doctor profile route
@app.route('/doctor/<int:doctor_id>')
def doctor_profile(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    return render_template('doctor_profile.html', doctor=doctor)

# Select doctor route - GET: Display form, POST: Process booking
@app.route('/select-doctor/<int:doctor_id>', methods=['GET', 'POST'])
def select_doctor(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    symptoms = session.get('symptoms')
    specialist = session.get('specialist')
    
    if not symptoms or not specialist:
        flash('Session expired. Please describe your symptoms again.', 'warning')
        return redirect(url_for('patient_dashboard'))
    
    if request.method == 'GET':
        return render_template('patient_details.html', doctor=doctor, specialist=specialist)
    
    # Process POST request - collect patient details and create records
    if request.method == 'POST':
        # Get patient details from form
        name = request.form.get('name')
        age = request.form.get('age')
        gender = request.form.get('gender')
        contact = request.form.get('contact')
        
        # Validate required fields
        if not all([name, age, gender, contact]):
            flash('All fields are required', 'error')
            return render_template('patient_details.html', doctor=doctor, specialist=specialist)
        
        # Create new patient record
        new_patient = Patient(
            name=name,
            age=age,
            gender=gender,
            symptoms=symptoms,
            contact=contact
        )
        
        db.session.add(new_patient)
        db.session.commit()
        
        # Store patient ID in session
        session['patient_id'] = new_patient.id
        
        # Associate patient with doctor
        new_patient.doctors.append(doctor)
        
        # Create appointment
        appointment = Appointment(
            patient_id=new_patient.id,
            doctor_id=doctor.id,
            date=datetime.datetime.now(),
            status='scheduled'
        )
        
        # Create patient history entry
        history_entry = PatientHistory(
            patient_id=new_patient.id,
            doctor_id=doctor.id,
            doctor_name=doctor.name,
            specialization=doctor.specialization,
            status='scheduled'
        )
        
        db.session.add(appointment)
        db.session.add(history_entry)
        db.session.commit()
        
        flash(f'You have successfully booked an appointment with Dr. {doctor.name}', 'success')
        return redirect(url_for('patient_history'))

# Patient history route
@app.route('/patient/history')
def patient_history():
    patient_id = session.get('patient_id')
    
    if not patient_id:
        flash('Please complete your profile first', 'warning')
        return redirect(url_for('patient_dashboard'))
    
    patient = Patient.query.get(patient_id)
    
    if not patient:
        flash('Patient record not found', 'error')
        return redirect(url_for('patient_dashboard'))
    
    # Get the current doctor (most recent)
    doctor = None
    if patient.doctors:
        doctor = patient.doctors[-1]
    
    # Get patient history entries sorted by date
    history = PatientHistory.query.filter_by(patient_id=patient.id).order_by(PatientHistory.date.desc()).all()
    
    return render_template('patient_history.html', 
                           patient=patient, 
                           doctor=doctor, 
                           history=history)

# Doctor login route
@app.route('/doctor/login', methods=['GET', 'POST'])
def doctor_login():
    if request.method == 'POST':
        doctor_id = request.form.get('doctor_id')
        password = request.form.get('password')
        
        # Find doctor in database
        doctor = Doctor.query.get(doctor_id)
        
        if doctor:
            # In a real application, we would check a hashed password
            # For now, we use a simple pattern of ID + "123"
            expected_password = f"{doctor_id}123"
            
            if password == expected_password:
                # Create a User object for Flask-Login
                user = User.query.filter_by(username=f"doctor_{doctor_id}").first()
                
                # If user doesn't exist, create it
                if not user:
                    user = User(
                        username=f"doctor_{doctor_id}",
                        password_hash=generate_password_hash(expected_password),
                        role='doctor'
                    )
                    db.session.add(user)
                    db.session.commit()
                
                login_user(user)
                session['doctor_id'] = doctor_id
                flash(f'Welcome, Dr. {doctor.name}', 'success')
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
    doctor_id = session.get('doctor_id')
    
    if not doctor_id:
        flash('Please log in first', 'warning')
        return redirect(url_for('doctor_login'))
    
    doctor = Doctor.query.get(doctor_id)
    
    if not doctor:
        flash('Doctor record not found', 'error')
        return redirect(url_for('doctor_login'))
    
    # Get all patients associated with this doctor
    patients = doctor.patients
    
    # Get all appointments for this doctor
    appointments = Appointment.query.filter_by(doctor_id=doctor.id).all()
    
    return render_template('doctor_dashboard.html', 
                           doctor=doctor, 
                           patients=patients, 
                           appointments=appointments)

# Admin login route
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Find admin user in database
        user = User.query.filter_by(username=username, role='admin').first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Welcome, Admin', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid admin credentials', 'error')
    
    return render_template('admin_login.html')

# Admin dashboard route
@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_authenticated or current_user.role != 'admin':
        flash('Admin access required', 'error')
        return redirect(url_for('admin_login'))
    
    # Get statistics from database
    total_patients = Patient.query.count()
    total_appointments = Appointment.query.count()
    
    # Get specialty statistics
    specialty_stats = {stat.specialty: stat.count for stat in SpecialtyStatistics.query.all()}
    
    # Get appointment status statistics
    appointment_stats = {
        'scheduled': Appointment.query.filter_by(status='scheduled').count(),
        'completed': Appointment.query.filter_by(status='completed').count(),
        'cancelled': Appointment.query.filter_by(status='cancelled').count()
    }
    
    return render_template('admin_dashboard.html', 
                           total_patients=total_patients,
                           total_appointments=total_appointments,
                           specialty_stats=specialty_stats,
                           appointment_stats=appointment_stats)

# Medicine analyzer route
@app.route('/medicine-analyzer')
def medicine_analyzer():
    return render_template('medicine_analyzer.html')

# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

# Update appointment status route
@app.route('/appointment/<int:appointment_id>/update', methods=['POST'])
@login_required
def update_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    
    # Check if user is the doctor for this appointment
    if current_user.role != 'admin' and str(appointment.doctor_id) != session.get('doctor_id'):
        flash('Unauthorized access', 'error')
        return redirect(url_for('doctor_dashboard'))
    
    new_status = request.form.get('status')
    
    if new_status in ['scheduled', 'completed', 'cancelled']:
        appointment.status = new_status
        
        # Update corresponding history entry
        history_entry = PatientHistory.query.filter_by(
            patient_id=appointment.patient_id,
            doctor_id=appointment.doctor_id
        ).order_by(PatientHistory.date.desc()).first()
        
        if history_entry:
            history_entry.status = new_status
        
        db.session.commit()
        flash('Appointment status updated successfully', 'success')
    else:
        flash('Invalid status', 'error')
    
    if current_user.role == 'admin':
        return redirect(url_for('admin_dashboard'))
    else:
        return redirect(url_for('doctor_dashboard'))