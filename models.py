from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, username, role):
        self.id = id
        self.username = username
        self.role = role

class Patient:
    def __init__(self, id, name, age, gender, symptoms, contact):
        self.id = id
        self.name = name
        self.age = age
        self.gender = gender
        self.symptoms = symptoms
        self.contact = contact
        self.assigned_doctor = None
        self.history = []

class Appointment:
    def __init__(self, id, patient_id, doctor_id, date, status="scheduled"):
        self.id = id
        self.patient_id = patient_id
        self.doctor_id = doctor_id
        self.date = date
        self.status = status  # scheduled, completed, cancelled
        self.notes = ""
