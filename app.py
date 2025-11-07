from flask import Flask, render_template, request, redirect, session, jsonify, flash
from flask_mysqldb import MySQL
import MySQLdb.cursors
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'hospital_secret_key'

# =========================
# 🔧 MySQL Configuration
# =========================
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'          # your MySQL username
app.config['MYSQL_PASSWORD'] = '25MCD10005'   # your MySQL password
app.config['MYSQL_DB'] = 'hospital_appointment_system'

mysql = MySQL(app)

# =========================
# 🔐 LOGIN SYSTEM
# =========================
@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM User WHERE username=%s AND password=%s', (username, password,))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['user_id']
            session['username'] = account['username']
            session['role'] = account['role']
            if account['role'] == 'Admin':
                return redirect('/admin/dashboard')
            elif account['role'] == 'Doctor':
                return redirect('/doctor/dashboard')
            elif account['role'] == 'Receptionist':
                return redirect('/receptionist/dashboard')
        else:
            msg = 'Incorrect username/password!'
    return render_template('login.html', msg=msg)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


# =========================
# 🧑‍💼 ADMIN DASHBOARD
# =========================
@app.route('/admin/dashboard')
def admin_dashboard():
    if 'loggedin' in session and session['role'] == 'Admin':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Fetch appointments
        cursor.execute("SELECT * FROM Appointment")
        appointments = cursor.fetchall()
        
        # Fetch departments
        cursor.execute("SELECT * FROM Department")
        departments = cursor.fetchall()
        
        # Fetch all doctors with department info
        cursor.execute("""
            SELECT d.doctor_id, d.name, d.specialization, d.contact_no, d.email,
                   d.available_days, d.available_time, d.department_id,
                   dep.department_name, u.username
            FROM Doctor d
            LEFT JOIN Department dep ON d.department_id = dep.department_id
            LEFT JOIN User u ON d.user_id = u.user_id
        """)
        doctors = cursor.fetchall()
        
        # Fetch all receptionists with user info
        cursor.execute("""
            SELECT r.receptionist_id, r.name, r.contact_no, r.email, u.username
            FROM Receptionist r
            JOIN User u ON r.user_id = u.user_id
        """)
        receptionists = cursor.fetchall()
        
        return render_template('dashboard_admin.html',
                               appointments=appointments,
                               departments=departments,
                               doctors=doctors,
                               receptionists=receptionists)
    return redirect('/login')


# =========================
# ➕ ADD DEPARTMENT (Admin Only)
# =========================
@app.route('/admin/add_department', methods=['POST'])
def add_department():
    if 'loggedin' in session and session['role'] == 'Admin':
        department_name = request.form['department_name']
        
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO Department (department_name) VALUES (%s)", (department_name,))
        mysql.connection.commit()
        flash('Department added successfully!', 'success')
        return redirect('/admin/dashboard')
    return redirect('/login')


# =========================
# ❌ REMOVE DEPARTMENT (Admin Only)
# =========================
@app.route('/admin/remove_department/<int:department_id>', methods=['POST'])
def remove_department(department_id):
    if 'loggedin' in session and session['role'] == 'Admin':
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM Department WHERE department_id = %s", (department_id,))
        mysql.connection.commit()
        flash('Department removed successfully!', 'success')
        return redirect('/admin/dashboard')
    return redirect('/login')


# =========================
# ➕ ADD DOCTOR (Admin Only)
# =========================
@app.route('/admin/add_doctor', methods=['POST'])
def add_doctor():
    if 'loggedin' in session and session['role'] == 'Admin':
        try:
            name = request.form['name']
            department_id = request.form['department_id']
            specialization = request.form['specialization']
            contact_no = request.form['contact_no']
            email = request.form['email']
            available_days = request.form['available_days']
            available_time = request.form['available_time']
            username = request.form['username']
            password = request.form['password']

            # Basic validation
            if not name.strip() or not username.strip():
                flash('Doctor name and username are required!', 'error')
                return redirect('/admin/dashboard')

            cursor = mysql.connection.cursor()

            # Check if username already exists
            cursor.execute("SELECT user_id FROM User WHERE username = %s", (username,))
            existing_user = cursor.fetchone()
            
            if existing_user:
                flash('Username already exists! Please choose a different username.', 'error')
                return redirect('/admin/dashboard')

            # 1️⃣ Create doctor user account
            cursor.execute("""
                INSERT INTO User (username, password, role)
                VALUES (%s, %s, 'Doctor')
            """, (username, password))
            user_id = cursor.lastrowid

            # 2️⃣ Insert into Doctor table
            cursor.execute("""
                INSERT INTO Doctor (user_id, department_id, name, specialization, contact_no, email, available_days, available_time)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (user_id, department_id, name, specialization, contact_no, email, available_days, available_time))
            
            mysql.connection.commit()
            flash('Doctor added successfully!', 'success')
            
        except Exception as e:
            mysql.connection.rollback()
            flash('Error adding doctor: ' + str(e), 'error')
        
        return redirect('/admin/dashboard')
    return redirect('/login')


# =========================
# 👀 VIEW DOCTORS
# =========================
@app.route('/admin/view_doctors')
def view_doctors():
    if 'loggedin' in session and session['role'] == 'Admin':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("""
            SELECT d.doctor_id, d.name, d.specialization, d.contact_no, d.email,
                   d.available_days, d.available_time,
                   dep.department_name
            FROM Doctor d
            LEFT JOIN Department dep ON d.department_id = dep.department_id
        """)
        doctors = cursor.fetchall()
        return render_template('view_doctors.html', doctors=doctors)
    return redirect('/login')


# =========================
# ❌ REMOVE DOCTOR
# =========================
@app.route('/admin/remove_doctor/<int:doctor_id>', methods=['POST'])
def remove_doctor(doctor_id):
    if 'loggedin' in session and session['role'] == 'Admin':
        try:
            cursor = mysql.connection.cursor()
            
            # Get user_id from doctor
            cursor.execute("SELECT user_id FROM Doctor WHERE doctor_id = %s", (doctor_id,))
            doctor = cursor.fetchone()
            
            if doctor:
                user_id = doctor[0]
                
                # Remove doctor
                cursor.execute("DELETE FROM Doctor WHERE doctor_id = %s", (doctor_id,))
                
                # Remove user account
                cursor.execute("DELETE FROM User WHERE user_id = %s", (user_id,))
            
            mysql.connection.commit()
            flash('Doctor removed successfully!', 'success')
            
        except Exception as e:
            mysql.connection.rollback()
            flash('Error removing doctor: ' + str(e), 'error')
        
        return redirect('/admin/dashboard')
    return redirect('/login')


# =========================
# ✏️ UPDATE DOCTOR (Admin Only)
# =========================
@app.route('/admin/update_doctor/<int:doctor_id>', methods=['POST'])
def update_doctor(doctor_id):
    if 'loggedin' in session and session['role'] == 'Admin':
        try:
            name = request.form['name']
            department_id = request.form['department_id']
            specialization = request.form['specialization']
            contact_no = request.form['contact_no']
            email = request.form['email']
            available_days = request.form['available_days']
            available_time = request.form['available_time']
            username = request.form['username']
            password = request.form['password']

            cursor = mysql.connection.cursor()

            # Get current doctor data
            cursor.execute("""
                SELECT d.user_id, u.username as current_username 
                FROM Doctor d 
                JOIN User u ON d.user_id = u.user_id 
                WHERE d.doctor_id = %s
            """, (doctor_id,))
            current_data = cursor.fetchone()

            if not current_data:
                flash('Doctor not found!', 'error')
                return redirect('/admin/dashboard')

            user_id = current_data[0]
            current_username = current_data[1]

            # Check if new username is taken by another user
            if username != current_username:
                cursor.execute("SELECT user_id FROM User WHERE username = %s AND user_id != %s", (username, user_id))
                if cursor.fetchone():
                    flash('Username already taken! Please choose a different username.', 'error')
                    return redirect('/admin/dashboard')

            # Update Doctor table
            cursor.execute("""
                UPDATE Doctor 
                SET name = %s, department_id = %s, specialization = %s, 
                    contact_no = %s, email = %s, available_days = %s, available_time = %s
                WHERE doctor_id = %s
            """, (name, department_id, specialization, contact_no, email, available_days, available_time, doctor_id))

            # Update User table
            if password.strip():
                # Update both username and password
                cursor.execute("""
                    UPDATE User 
                    SET username = %s, password = %s 
                    WHERE user_id = %s
                """, (username, password, user_id))
            else:
                # Update only username
                cursor.execute("""
                    UPDATE User 
                    SET username = %s 
                    WHERE user_id = %s
                """, (username, user_id))
            
            mysql.connection.commit()
            flash('Doctor updated successfully!', 'success')
            
        except Exception as e:
            mysql.connection.rollback()
            flash('Error updating doctor: ' + str(e), 'error')
        
        return redirect('/admin/dashboard')
    return redirect('/login')


# =========================
# ➕ ADD RECEPTIONIST (Admin Only)
# =========================
@app.route('/admin/add_receptionist', methods=['POST'])
def add_receptionist():
    if 'loggedin' in session and session['role'] == 'Admin':
        try:
            name = request.form['name']
            contact_no = request.form['contact_no']
            email = request.form['email']
            username = request.form['username']
            password = request.form['password']

            # Basic validation
            if not name.strip() or not username.strip():
                flash('Receptionist name and username are required!', 'error')
                return redirect('/admin/dashboard')

            cursor = mysql.connection.cursor()

            # Check if username already exists
            cursor.execute("SELECT user_id FROM User WHERE username = %s", (username,))
            existing_user = cursor.fetchone()
            
            if existing_user:
                flash('Username already exists! Please choose a different username.', 'error')
                return redirect('/admin/dashboard')

            # 1️⃣ Create receptionist user account
            cursor.execute("""
                INSERT INTO User (username, password, role)
                VALUES (%s, %s, 'Receptionist')
            """, (username, password))
            user_id = cursor.lastrowid

            # 2️⃣ Insert into Receptionist table
            cursor.execute("""
                INSERT INTO Receptionist (user_id, name, contact_no, email)
                VALUES (%s, %s, %s, %s)
            """, (user_id, name, contact_no, email))
            
            mysql.connection.commit()
            flash('Receptionist added successfully!', 'success')
            
        except Exception as e:
            mysql.connection.rollback()
            flash('Error adding receptionist: ' + str(e), 'error')
        
        return redirect('/admin/dashboard')
    return redirect('/login')


# =========================
# ❌ REMOVE RECEPTIONIST (Admin Only)
# =========================
@app.route('/admin/remove_receptionist/<int:receptionist_id>', methods=['POST'])
def remove_receptionist(receptionist_id):
    if 'loggedin' in session and session['role'] == 'Admin':
        try:
            cursor = mysql.connection.cursor()
            
            # Get user_id from receptionist
            cursor.execute("SELECT user_id FROM Receptionist WHERE receptionist_id = %s", (receptionist_id,))
            receptionist = cursor.fetchone()
            
            if receptionist:
                user_id = receptionist[0]
                
                # Remove receptionist
                cursor.execute("DELETE FROM Receptionist WHERE receptionist_id = %s", (receptionist_id,))
                
                # Remove user account
                cursor.execute("DELETE FROM User WHERE user_id = %s", (user_id,))
            
            mysql.connection.commit()
            flash('Receptionist removed successfully!', 'success')
            
        except Exception as e:
            mysql.connection.rollback()
            flash('Error removing receptionist: ' + str(e), 'error')
        
        return redirect('/admin/dashboard')
    return redirect('/login')


# =========================
# ✏️ UPDATE RECEPTIONIST (Admin Only)
# =========================
@app.route('/admin/update_receptionist/<int:receptionist_id>', methods=['POST'])
def update_receptionist(receptionist_id):
    if 'loggedin' in session and session['role'] == 'Admin':
        try:
            name = request.form['name']
            contact_no = request.form['contact_no']
            email = request.form['email']
            username = request.form['username']
            password = request.form['password']

            cursor = mysql.connection.cursor()

            # Get current receptionist data
            cursor.execute("""
                SELECT r.user_id, u.username as current_username 
                FROM Receptionist r 
                JOIN User u ON r.user_id = u.user_id 
                WHERE r.receptionist_id = %s
            """, (receptionist_id,))
            current_data = cursor.fetchone()

            if not current_data:
                flash('Receptionist not found!', 'error')
                return redirect('/admin/dashboard')

            user_id = current_data[0]
            current_username = current_data[1]

            # Check if new username is taken by another user
            if username != current_username:
                cursor.execute("SELECT user_id FROM User WHERE username = %s AND user_id != %s", (username, user_id))
                if cursor.fetchone():
                    flash('Username already taken! Please choose a different username.', 'error')
                    return redirect('/admin/dashboard')

            # Update Receptionist table
            cursor.execute("""
                UPDATE Receptionist 
                SET name = %s, contact_no = %s, email = %s 
                WHERE receptionist_id = %s
            """, (name, contact_no, email, receptionist_id))

            # Update User table
            if password.strip():
                # Update both username and password
                cursor.execute("""
                    UPDATE User 
                    SET username = %s, password = %s 
                    WHERE user_id = %s
                """, (username, password, user_id))
            else:
                # Update only username
                cursor.execute("""
                    UPDATE User 
                    SET username = %s 
                    WHERE user_id = %s
                """, (username, user_id))
            
            mysql.connection.commit()
            flash('Receptionist updated successfully!', 'success')
            
        except Exception as e:
            mysql.connection.rollback()
            flash('Error updating receptionist: ' + str(e), 'error')
        
        return redirect('/admin/dashboard')
    return redirect('/login')


# =========================
# 🩺 DOCTOR DASHBOARD
# =========================
@app.route('/doctor/dashboard')
def doctor_dashboard():
    if 'loggedin' in session and session['role'] == 'Doctor':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Get doctor ID from session
        cursor.execute("""
            SELECT d.doctor_id 
            FROM Doctor d 
            JOIN User u ON d.user_id = u.user_id 
            WHERE u.username = %s
        """, (session['username'],))
        doctor = cursor.fetchone()
        
        if doctor:
            doctor_id = doctor['doctor_id']
            
            # Fetch appointments with patient details
            cursor.execute("""
                SELECT a.*, p.name as patient_name, p.age, p.gender, p.blood_group, 
                       p.contact_no as patient_contact, p.email as patient_email,
                       p.address, p.medical_history
                FROM Appointment a
                JOIN Patient p ON a.patient_id = p.patient_id
                WHERE a.doctor_id = %s AND a.status IN ('Scheduled', 'Completed')
                ORDER BY a.appointment_date DESC, a.appointment_time DESC
            """, (doctor_id,))
            appointments = cursor.fetchall()
            
            # Fetch prescriptions for completed appointments
            for appointment in appointments:
                if appointment['status'] == 'Completed':
                    cursor.execute("""
                        SELECT pr.*, m.medicine_name, m.dosage, m.duration
                        FROM Prescription pr
                        LEFT JOIN Medicine m ON pr.prescription_id = m.prescription_id
                        WHERE pr.appointment_id = %s
                    """, (appointment['appointment_id'],))
                    prescription_data = cursor.fetchall()
                    appointment['prescription'] = prescription_data
            
            return render_template('dashboard_doctor.html', 
                                   appointments=appointments, 
                                   doctor_id=doctor_id)
    
    return redirect('/login')


# =========================
# 👀 VIEW PATIENT DETAILS (For Doctor)
# =========================
@app.route('/doctor/patient/<int:patient_id>')
def view_patient_details_doctor(patient_id):
    if 'loggedin' in session and session['role'] == 'Doctor':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Get patient details
        cursor.execute("SELECT * FROM Patient WHERE patient_id = %s", (patient_id,))
        patient = cursor.fetchone()
        
        # Get doctor's appointments with this patient
        cursor.execute("""
            SELECT d.doctor_id 
            FROM Doctor d 
            JOIN User u ON d.user_id = u.user_id 
            WHERE u.username = %s
        """, (session['username'],))
        doctor = cursor.fetchone()
        
        if patient and doctor:
            # Verify this patient has appointments with this doctor
            cursor.execute("""
                SELECT * FROM Appointment 
                WHERE patient_id = %s AND doctor_id = %s
                ORDER BY appointment_date DESC, appointment_time DESC
            """, (patient_id, doctor['doctor_id']))
            appointments = cursor.fetchall()
            
            if appointments:
                return render_template('patient_details.html', 
                                       patient=patient, 
                                       appointments=appointments)
        
        return redirect('/doctor/dashboard')
    return redirect('/login')


# =========================
# 👀 VIEW PATIENT DETAILS (For Receptionist) - NEW ROUTE
# =========================
@app.route('/receptionist/patient/<int:patient_id>')
def view_patient_details_receptionist(patient_id):
    if 'loggedin' in session and session['role'] == 'Receptionist':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Get patient details
        cursor.execute("SELECT * FROM Patient WHERE patient_id = %s", (patient_id,))
        patient = cursor.fetchone()
        
        if patient:
            # Get all appointments for this patient
            cursor.execute("""
                SELECT a.*, d.name as doctor_name
                FROM Appointment a
                LEFT JOIN Doctor d ON a.doctor_id = d.doctor_id
                WHERE a.patient_id = %s
                ORDER BY a.appointment_date DESC, a.appointment_time DESC
            """, (patient_id,))
            appointments = cursor.fetchall()
            
            return render_template('patient_details.html', 
                                   patient=patient, 
                                   appointments=appointments)
        
        flash('Patient not found!', 'error')
        return redirect('/receptionist/dashboard')
    return redirect('/login')


# =========================
# ✅ COMPLETE APPOINTMENT
# =========================
@app.route('/doctor/complete_appointment/<int:appointment_id>', methods=['POST'])
def complete_appointment(appointment_id):
    if 'loggedin' in session and session['role'] == 'Doctor':
        try:
            cursor = mysql.connection.cursor()
            
            # Verify the appointment belongs to this doctor
            cursor.execute("""
                SELECT a.* 
                FROM Appointment a
                JOIN Doctor d ON a.doctor_id = d.doctor_id
                JOIN User u ON d.user_id = u.user_id
                WHERE a.appointment_id = %s AND u.username = %s
            """, (appointment_id, session['username']))
            appointment = cursor.fetchone()
            
            if appointment:
                cursor.execute("UPDATE Appointment SET status='Completed' WHERE appointment_id=%s", (appointment_id,))
                mysql.connection.commit()
                flash('Appointment marked as completed!', 'success')
                return '', 204
            else:
                return 'Appointment not found', 404
                
        except Exception as e:
            mysql.connection.rollback()
            return 'Error: ' + str(e), 500
        
    return redirect('/login')


# =========================
# 💊 ADD PRESCRIPTION
# =========================
@app.route('/doctor/add_prescription/<int:appointment_id>', methods=['POST'])
def add_prescription(appointment_id):
    if 'loggedin' in session and session['role'] == 'Doctor':
        try:
            advice = request.form['advice']
            medicines = request.form.getlist('medicine_name[]')
            dosages = request.form.getlist('dosage[]')
            durations = request.form.getlist('duration[]')
            
            cursor = mysql.connection.cursor()
            
            # Verify the appointment belongs to this doctor and is completed
            cursor.execute("""
                SELECT a.* 
                FROM Appointment a
                JOIN Doctor d ON a.doctor_id = d.doctor_id
                JOIN User u ON d.user_id = u.user_id
                WHERE a.appointment_id = %s AND u.username = %s AND a.status = 'Completed'
            """, (appointment_id, session['username']))
            appointment = cursor.fetchone()
            
            if appointment:
                # Insert prescription
                cursor.execute("""
                    INSERT INTO Prescription (appointment_id, date, advice)
                    VALUES (%s, CURDATE(), %s)
                """, (appointment_id, advice))
                prescription_id = cursor.lastrowid
                
                # Insert medicines
                for i in range(len(medicines)):
                    if medicines[i].strip():  # Only add if medicine name is not empty
                        cursor.execute("""
                            INSERT INTO Medicine (prescription_id, medicine_name, dosage, duration)
                            VALUES (%s, %s, %s, %s)
                        """, (prescription_id, medicines[i], dosages[i], durations[i]))
                
                mysql.connection.commit()
                flash('Prescription added successfully!', 'success')
            else:
                flash('Appointment not found or not completed!', 'error')
                
        except Exception as e:
            mysql.connection.rollback()
            flash('Error adding prescription: ' + str(e), 'error')
        
        return redirect('/doctor/dashboard')
    return redirect('/login')


# =========================
# 🧾 RECEPTIONIST DASHBOARD - UPDATED
# =========================
@app.route('/receptionist/dashboard')
def receptionist_dashboard():
    if 'loggedin' in session and session['role'] == 'Receptionist':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Ensure receptionist record exists for the current user
        cursor.execute("SELECT receptionist_id FROM Receptionist WHERE user_id = %s", (session['id'],))
        receptionist = cursor.fetchone()
        
        if not receptionist:
            # Create a receptionist record if it doesn't exist
            cursor.execute("""
                INSERT INTO Receptionist (user_id, name, contact_no, email) 
                VALUES (%s, %s, %s, %s)
            """, (session['id'], session['username'], 'Not provided', ''))
            mysql.connection.commit()
            flash('Receptionist profile created successfully!', 'success')

        # Fetch all appointments with patient and doctor names
        cursor.execute("""
            SELECT a.*, p.name as patient_name, d.name as doctor_name
            FROM Appointment a
            LEFT JOIN Patient p ON a.patient_id = p.patient_id
            LEFT JOIN Doctor d ON a.doctor_id = d.doctor_id
            ORDER BY a.appointment_date DESC, a.appointment_time DESC
        """)
        appointments = cursor.fetchall()

        # Fetch all patients
        cursor.execute("SELECT * FROM Patient ORDER BY name")
        patients = cursor.fetchall()

        # Fetch all doctors for appointment booking
        cursor.execute("""
            SELECT d.doctor_id, d.name, d.specialization, dep.department_name
            FROM Doctor d
            LEFT JOIN Department dep ON d.department_id = dep.department_id
            ORDER BY d.name
        """)
        doctors = cursor.fetchall()

        # Get today's date for the form
        today = datetime.now().strftime('%Y-%m-%d')

        return render_template('dashboard_receptionist.html',
                               appointments=appointments,
                               patients=patients,
                               doctors=doctors,
                               today=today)
    return redirect('/login')


# =========================
# ➕ ADD PATIENT (Enhanced)
# =========================
@app.route('/add_patient', methods=['POST'])
def add_patient():
    if 'loggedin' in session and session['role'] == 'Receptionist':
        try:
            # Get form data
            name = request.form['name']
            age = request.form['age']
            gender = request.form['gender']
            blood_group = request.form['blood_group']
            contact_no = request.form['contact_no']
            email = request.form['email']
            address = request.form['address']
            medical_history = request.form['medical_history']

            # Basic validation
            if not name.strip():
                flash('Patient name is required!', 'error')
                return redirect('/receptionist/dashboard')

            cursor = mysql.connection.cursor()
            
            # Check if patient with same contact or email already exists
            cursor.execute("""
                SELECT patient_id FROM Patient 
                WHERE contact_no = %s OR email = %s
            """, (contact_no, email))
            existing_patient = cursor.fetchone()
            
            if existing_patient:
                flash('Patient with same contact number or email already exists!', 'error')
                return redirect('/receptionist/dashboard')

            # Insert new patient
            cursor.execute("""
                INSERT INTO Patient (name, age, gender, blood_group, contact_no, email, address, medical_history)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (name, age, gender, blood_group, contact_no, email, address, medical_history))
            
            mysql.connection.commit()
            flash('Patient added successfully!', 'success')
            
        except Exception as e:
            mysql.connection.rollback()
            flash('Error adding patient: ' + str(e), 'error')
        
        return redirect('/receptionist/dashboard')
    return redirect('/login')


# =========================
# ❌ REMOVE PATIENT (Receptionist) - NEW ROUTE
# =========================
@app.route('/receptionist/remove_patient/<int:patient_id>', methods=['POST'])
def remove_patient(patient_id):
    if 'loggedin' in session and session['role'] == 'Receptionist':
        try:
            cursor = mysql.connection.cursor()
            
            # Check if patient has any appointments
            cursor.execute("SELECT COUNT(*) as appointment_count FROM Appointment WHERE patient_id = %s", (patient_id,))
            appointment_count = cursor.fetchone()[0]
            
            if appointment_count > 0:
                flash(f'Cannot remove patient! Patient has {appointment_count} appointment(s) in the system. Please cancel all appointments first.', 'error')
                return redirect('/receptionist/dashboard')
            
            # Remove patient
            cursor.execute("DELETE FROM Patient WHERE patient_id = %s", (patient_id,))
            mysql.connection.commit()
            flash('Patient removed successfully!', 'success')
            
        except Exception as e:
            mysql.connection.rollback()
            flash('Error removing patient: ' + str(e), 'error')
        
        return redirect('/receptionist/dashboard')
    return redirect('/login')


# =========================
# ➕ BOOK APPOINTMENT (Receptionist) - FIXED
# =========================
@app.route('/receptionist/book_appointment', methods=['POST'])
def book_appointment():
    if 'loggedin' in session and session['role'] == 'Receptionist':
        try:
            patient_id = request.form['patient_id']
            doctor_id = request.form['doctor_id']
            appointment_date = request.form['appointment_date']
            appointment_time = request.form['appointment_time']
            consultation_type = request.form.get('consultation_type', 'In-person')
            remarks = request.form.get('remarks', '')

            # Basic validation
            if not patient_id or not doctor_id or not appointment_date or not appointment_time:
                flash('All required fields must be filled!', 'error')
                return redirect('/receptionist/dashboard')

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            
            # Get receptionist ID from session - FIXED
            cursor.execute("SELECT receptionist_id FROM Receptionist WHERE user_id = %s", (session['id'],))
            receptionist = cursor.fetchone()
            
            # Check if receptionist exists and get the ID properly
            if receptionist:
                receptionist_id = receptionist['receptionist_id']
            else:
                # If no receptionist record found, use NULL
                receptionist_id = None

            # Check for conflicting appointments
            cursor.execute("""
                SELECT appointment_id FROM Appointment 
                WHERE doctor_id = %s AND appointment_date = %s AND appointment_time = %s AND status = 'Scheduled'
            """, (doctor_id, appointment_date, appointment_time))
            conflicting_appointment = cursor.fetchone()
            
            if conflicting_appointment:
                flash('Doctor already has an appointment at that time! Please choose a different time.', 'error')
                return redirect('/receptionist/dashboard')

            # Insert appointment
            cursor.execute("""
                INSERT INTO Appointment (patient_id, doctor_id, receptionist_id, appointment_date, appointment_time, consultation_type, status, remarks)
                VALUES (%s, %s, %s, %s, %s, %s, 'Scheduled', %s)
            """, (patient_id, doctor_id, receptionist_id, appointment_date, appointment_time, consultation_type, remarks))
            
            mysql.connection.commit()
            flash('Appointment booked successfully!', 'success')
            
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Error booking appointment: {str(e)}', 'error')
        
        return redirect('/receptionist/dashboard')
    return redirect('/login')


# =========================
# ❌ CANCEL APPOINTMENT (Receptionist)
# =========================
@app.route('/receptionist/cancel_appointment/<int:appointment_id>', methods=['POST'])
def cancel_appointment(appointment_id):
    if 'loggedin' in session and session['role'] == 'Receptionist':
        try:
            cursor = mysql.connection.cursor()
            cursor.execute("UPDATE Appointment SET status='Cancelled' WHERE appointment_id=%s", (appointment_id,))
            mysql.connection.commit()
            flash('Appointment cancelled successfully!', 'success')
        except Exception as e:
            mysql.connection.rollback()
            flash('Error cancelling appointment: ' + str(e), 'error')
        
        return redirect('/receptionist/dashboard')
    return redirect('/login')


# =========================
# 📅 ALL APPOINTMENTS PAGE
# =========================
@app.route('/appointments')
def view_appointments():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("""
            SELECT a.*, p.name as patient_name, d.name as doctor_name
            FROM Appointment a
            LEFT JOIN Patient p ON a.patient_id = p.patient_id
            LEFT JOIN Doctor d ON a.doctor_id = d.doctor_id
            ORDER BY a.appointment_date DESC, a.appointment_time DESC
        """)
        appointments = cursor.fetchall()
        return render_template('appointments.html', appointments=appointments)
    return redirect('/login')


# =========================
# 🏠 MAIN
# =========================
if __name__ == '__main__':
    app.run(debug=True)