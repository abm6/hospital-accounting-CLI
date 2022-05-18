#Medical Hospital Database Console Based Application
#Non prompting static Python app(App will quit on completion of a task)
#Loops are not used to avoid call stack errors
#One will need to re - run the application for each task
#Error Handling is done optimally 
#And If invalid inputs are entered by the user 
#The respective error codes will be displayed or a message would be shown stopping the application

import sqlite3
import os

#create the database directory if does not exist
if not os.path.exists('db'):
    os.mkdir('db')

#function to clear the console
clearConsole = lambda: os.system('cls'
                                 if os.name in ('nt', 'dos') else 'clear')

#connect to database
conn = sqlite3.connect('./db/hospital.db')

#create cursor
c = conn.cursor()

#this function generates the initial tables if they are not presernt
def create_tables():
    #create table
    #the unique ROW ID gets assigned for each patient 
    #When the account gets created
    c.execute("""
        CREATE TABLE IF NOT EXISTS patient(
            name text NOT NULL,
            address text,
            phone text
        );
    """)

    #here staff ID is assigned dynamically and initially starts with 100
    #the Pat_id references to the unique row id of the patien table
    c.execute("""
        CREATE TABLE IF NOT EXISTS appointment(
            type TEXT,
            staff_id INTEGER NOT NULL,
            pat_id INTEGER NOT NULL,
            status NUMBER,
            CONSTRAINT valid_status CHECK (status IN (0,1)),
            FOREIGN KEY (staff_id) references healthcare_professional(employee_num),
            FOREIGN KEY (pat_id) references patient(rowid)
        );
    """)

    #Healthealthcare_professional Staff Table keeps record of each hostpial staff 
    #i.e. Doctor or Nurse
    c.execute("""
        CREATE TABLE IF NOT EXISTS healthcare_professional(
            employee_num text NOT NULL PRIMARY KEY,
            name TEXT NOT NULL,
            role TEXT NOT NULL,
            occupied INTEGER,
            CONSTRAINT valid_occupy CHECK (occupied IN (0,1)),
            CONSTRAINT validate_role CHECK (role IN ('doctor','nurse'))
        );
    """)

    #This is a less used table and only fetches and stores doctors from the healthealthcare_professional table
    c.execute("""
        CREATE TABLE IF NOT EXISTS doctor(
            doc_id INTEGER NOT NULL PRIMARY KEY references healthcare_professional(employee_num),
            pre_id INTEGER,
            pat_id INTEGER references patient(pat_id)
        );
    """)

    #this is a less used table and only fetches and stores nurses from the healthealthcare_professional
    c.execute("""
        CREATE TABLE IF NOT EXISTS nurse(
            nurse_id INTEGER NOT NULL PRIMARY KEY references healthcare_professional(employee_num),
            name TEXT
        );

    """)

    #once a doctor issues a prescription
    #the entry gets added here and the doctor who was marked as occupied gets free
    c.execute("""
        CREATE TABLE IF NOT EXISTS prescription(
            type TEXT,
            pat_id INTEGER references patient(pat_id),
            doc_id INTEGER references doctor(doc_id),
            quantity INTEGER,
            dosage REAL
        );
    """)

    #this table keeps track of the appointments of all the patient and staff
    #this table is the main connection for the prescription and appointments
    #every patient can access their last appoint records
    #if the appointment has not been completed yet then it will show status as pending
    #this status is kept track by the completed variable in the table
    c.execute("""
        CREATE TABLE IF NOT EXISTS appointment_schedule(
            app_id INTEGER NOT NULL PRIMARY KEY references appointment(rowid),
            consultation TEXT,
            completed NUMBER,
            prescp_id INTEGER,
            CONSTRAINT valid_complete_status CHECK( completed IN (0,1)),
            FOREIGN KEY (prescp_id) REFERENCES prescription(rowid)
        );
    """)


#the patient class possesses all the methods and operations for the patient
class Patient:
    def __init__(self):
        pass

    #function to check if a patient exists
    def patientExists(self,patient_id, name):
        c.execute(f"""
            SELECT rowid from patient
            where rowid = "{patient_id}"
            AND name = "{name}"
        """)
        found = c.fetchone()
        return found and patient_id in found

    #SUB Dashboard for the Patients for various services
    def menu(self,pat_id, patient_name=None):
        clearConsole()
        print("========Receptionist======")

        while (True):
            print("1. Make Appointment")
            print("2. Cancel appointments")
            print("3. View your upcoming appointments")
            print("4. View the last appointment report")
            print("q. Go back")
            choice = input("Enter Choice: ")

            if choice == '1':
                Receptionist().manage_appointments("make",
                                        patient_id=pat_id,
                                        patient_name=patient_name)
            elif choice == '2':
                _appointments = Receptionist().manage_appointments("view", patient_id=pat_id)
                if len(_appointments) < 1:
                    print("You have no appointments.\n")
                    continue
                else:
                    try:
                        appointment_code = int(
                            input("Enter Appointment code to cancel: "))
                    except ValueError:
                        print("Enter a valid appointment code!")
                        continue

                    if appointment_code in _appointments:
                        e = Receptionist().manage_appointments(
                            'cancel', appointment_id=appointment_code)
                        if e == 0:
                            print("appointment cancelled successfully")
                        else:
                            print("appointment was not cancelled")
                    else:
                        print("you entered an invalid appointment code")
            elif choice == '3':
                e = Receptionist().manage_appointments("view", patient_id=pat_id)
                if len(e) < 1:
                    print("You have no appointments.\n")
                    continue
            elif choice == '4':
                print("patient id",type(pat_id))
                AppointmentSchedule().viewAppointmentReport(caller="patient",patient_id=pat_id)


            elif choice == 'q' or choice == 'Q':
                Receptionist().dashboard()
            else:
                print("Invalid Choice")

    #function to add patients with a unique ID. 
    #Two patients with the same name can exist
    def addPatient(self):
        print("Creating your patient account")
        name = input("Enter name: ").lower()
        address = input("Enter Address: ").lower()
        phone = input("Enter phone: ")

        c.execute(f"""
            INSERT INTO patient VALUES(
                "{name}",
                "{address}",
                "{phone}"
            )
        """)

        conn.commit()
        return c.lastrowid


    #Function to login patient
    def patientLogin(self):
        clearConsole()
        try:
            patient_id = int(input("Enter you ID: "))
            name = input("Enter name: ").lower()

            if self.patientExists(patient_id, name):
                clearConsole()
                print("patient Record found")
                print("name: ", name.capitalize())
                print("id: ", patient_id)
                self.menu(patient_id, patient_name=name)
            else:
                print("Patient Record not found")
                exit()
        except ValueError:
            print("Entered ID must be a number and name cannot contain numbers")


#Class to manage all staff related operations
class HealthcareProfessional:
    def __init__(self):
        pass

    #function to check if a patient exists
    def staffExists(self,staff_id, name):
        c.execute(f"""
            SELECT employee_num from healthcare_professional
            where employee_num = {staff_id}
            AND name = "{name}"
        """)

        found = c.fetchone()

        return found and str(staff_id) in found


    #function to add Doctors or Nurses to the healthealthcare_professional Staff
    #only doctors do the treatment
    def addStaff(self):
        print("Creating your Healthealthcare_professional Professional account")
        name = input("Enter name: ").lower()
        designation = input("Enter Designation [doctor/nurse] : ")

        if designation.lower() == 'doctor' or designation.lower() == "nurse":

            #get the last employee id
            c.execute("""
                SELECT MAX(employee_num) from healthcare_professional
            """)

            prevEmployeeID = c.fetchone()[0]
            newEmployeeId = -1

            if not prevEmployeeID:
                newEmployeeId = 100
            else:
                newEmployeeId = int(prevEmployeeID) + 1

            c.execute(f"""
             INSERT INTO healthcare_professional VALUES(
                 {newEmployeeId},
                 "{name}",
                 "{designation}",
                 0
                 )
            """)

            conn.commit()
            return newEmployeeId

        else:
            print("Invalid designation!")

    #Internal database operations for the staff
    def staffLogin(self):
        clearConsole()
        try:
            staff_id = int(input("Enter you ID: "))
            name = input("Enter name: ").lower()

            if self.staffExists(staff_id, name):
                clearConsole()
                print("Staff Record found")
                print("name: ", name.capitalize())
                print("id: ", staff_id)
                self.menu(staff_id)
            else:
                print("Staff Record not found")
        except ValueError as er:
            print("Your ID must be a number and name must be a string")
            print(er)

    #The SUB dash board screen for the Hospital staff
    #i.e Nurses or Doctors
    #User interaciton Panel
    def menu(self,staff_id):
        while (True):
            print("-----------------------------------------------------")
            print("                   Staff Services")
            print("1. View Upcoming Appointments")
            print("2. Review a patient and give prescription")
            print("3. View The last appointment report")
            print("q. Go back")
    
            choice = input("Enter Choice: ")
            if choice == '1':
                _appointments = Prescription().staffOperations(task='view', staff_id=staff_id)
    
                if len(_appointments) >= 1:
                    print("--------viewing Appointments-------")
                    for item in _appointments:
                        print("Appointment Number: ", item[0])
                        print("Appointment Type:   ", item[1])
                        print("Employee Number:    ", item[2])
                        print("Patient Number:     ", item[3])
                else:
                    clearConsole()
                    print("You have no appointments")
            elif choice == "2":
                presc = []
                _appointments = Prescription().staffOperations(task='view', staff_id=staff_id)
    
                try:
                    _appointmentNumber = int(
                        input("Enter an Appointment Number: "))
                    flag = False
                    index = 0
                    for index in range(0, len(_appointments)):
                        if _appointments[index][0] == _appointmentNumber:
                            flag = True
                            break
                        index += 1
    
                    if flag:
                        clearConsole()
                        print("Generating Prescription:")
                        print("Appointment Number:   ", _appointmentNumber)
                        print("Appointment Type:     ", _appointments[index][1])
                        print("Staff ID:             ", _appointments[index][2])
                        print("Patient ID:           ", _appointments[index][3])
                        presc.append(input("Prescription Type:     "))  #type
                        presc.append(_appointments[index][3])  #patient id
                        presc.append(_appointments[index][2])  #doctor id
                        presc.append(input("Quantity of medicines: "))  #quantity
                        presc.append(input("Dosage:                "))  #dosage
    
                        consultation = input("Consultation: ")

                        #get a prescription ID for the prescription created
                        _prescriptionId = Prescription().staffOperations(
                            task='precp',
                            staff_id=staff_id,
                            presc=presc,
                            consult=consultation,
                            app_id=_appointmentNumber)
    
                        if _prescriptionId != -1:
                            print("Prescription generated successfully")
                            print("PescriptionID: ", _prescriptionId)
    
                        else:
                            print(
                                "there was some error in generating prescription")
                    else:
                        clearConsole()
                        print(
                            f"The appointment code: '{_appointmentNumber}' does not exist"
                        )
                except ValueError as er:
                    print("ERROR! Incorrect Value Entered!")
    
            elif choice == '3':
                AppointmentSchedule().viewAppointmentReport(caller="staff",staff_id=staff_id)
    
            elif choice == "q" or choice == "Q":
                Receptionist().dashboard()
            else:
                print("Error! invalid choice")


#the doctor class inherits from healthcare professional
class Doctor(HealthcareProfessional):
    def __init__(self):
        pass

    def update_doctors(self):

        #before updating the doctor table delete all the doctors
        c.execute("DELETE FROM doctor")

        c.execute("""
           INSERT INTO doctor 
           select doc_id, rowid, pat_id 
           from prescription;
        """)

#every nurse is a healthcare professional
class Nurse(HealthcareProfessional):
    def __init__(self):
        pass
    
    def update_nurses(self):

        #before emptying the nurse table, delete all the records
        c.execute("DELETE from Nurse")

        c.execute("""
           INSERT INTO nurse 
           select employee_num, name
           from healthcare_professional
           where role="nurse";
        """)

class Prescription:
    def __init__(self):
        pass

    #all data manipulation done by the healthealthcare_professional staff
    def staffOperations(self,task=None,         #Task code
                        staff_id=None,          #Doctor Number
                        presc=[],               #The prescription data input by the doctor
                        consult=None,           #The consultation fiven by the doctor
                        app_id=None):           #the appointment ID

        #View the appointments for the logged in doctor only
        if task == "view" and staff_id:
            c.execute(f"""
                SELECT rowid,* from appointment 
                WHERE staff_id = "{staff_id}"
                AND status=0
            """)

            _appointments = c.fetchall()
            return _appointments            #Return a list of this doctor's appointments

        #generate prescription
        elif task == "precp" and staff_id and len(presc) == 5 and app_id:
            _prescriptionId = -1
            try:
                c.execute(f"""
                    INSERT into prescription VALUES (
                        "{presc[0]}",
                        "{presc[1]}",
                        "{presc[2]}",
                        "{presc[3]}",
                        "{presc[4]}"
                    )
                """)

                _prescriptionId = c.lastrowid

                #post appointment
                #mark the doctor or nurse as Unoccupied to othe patients
                c.execute(f"""
                    UPDATE healthcare_professional
                    SET occupied=0
                    WHERE employee_num="{staff_id}"
                """)

                #Mark the appointment status as done
                c.execute(f"""
                    UPDATE appointment
                    SET status=1
                    WHERE rowid={app_id}
                """)

                ######################################
                # Consultation will be updated in the appointment_schedule table
                c.execute(f"""
                    UPDATE appointment_schedule
                    SET consultation ="{consult}",
                    completed=1,
                    prescp_id={_prescriptionId}
                    WHERE app_id={app_id}
                """)

                conn.commit()

            except sqlite3.Error as er:
                print("Error! ", er)
                return -1

            return _prescriptionId
        else:
            print("ERROR in Staff Operations!")


class Appointment:
    def __init__(self):
        pass

    #Book the appointment if a doctor is available
    #the name of the functions depict what they are doing
    def bookAppointment(self,appoint_type, staff_id, patient_id, patient_name):
        if not self.patientExists(patient_id, patient_name):
            print(f"Error! Patient {patient_id} does not exist")
            return 1

        try:
            c.execute(f"""
            INSERT INTO appointment VALUES(
                "{appoint_type}",
                {staff_id},
                {patient_id},
                {0}
            )
            """)

            clearConsole()
            print("--------------------------------------------------------------")
            print("Appointment Successfully booked")
            _appointmentID = c.lastrowid
            print("Appointment Number: ", _appointmentID)
            print("--------------------------------------------------------------")

            c.execute(f"""
                UPDATE healthcare_professional 
                SET occupied=1
                WHERE employee_num={staff_id}
            """)

            c.execute(f"""
                INSERT INTO appointment_schedule VALUES(
                    {_appointmentID},
                    "",
                    0,
                    ''
                )
            """)

            conn.commit()
        except sqlite3.Error as er:
            print("ERROR!", er)

    #function to delete the appointment
    def deleteAppointment(self,appointment_id):
        try:
            c.execute(f"""
            DELETE FROM appointment
            WHERE rowid={appointment_id}
        """)

            conn.commit()
        except sqlite3.Error as er:
            print("Could not delete!", er)


class AppointmentSchedule:
    def __init__(self):
        pass

    #print the appointment report after matching from the database
    def viewAppointmentReport(self,caller="",staff_id=None, patient_id=None):
        if caller == "patient" and patient_id:
            print("CALLED")
            c.execute(f"""
                    SELECT * FROM appointment_schedule t1
                    LEFT JOIN prescription t2
                    ON t1.prescp_id=t2.rowid 
                    WHERE EXISTS (
                        SELECT * from appointment t3
                        WHERE t1.app_id=t3.rowid
                        AND t3.pat_id={patient_id}
                    );
                """)
        elif caller =="staff" and staff_id :
            c.execute(f"""
                    SELECT * FROM appointment_schedule t1
                    LEFT JOIN prescription t2
                    ON t1.prescp_id=t2.rowid 
                    WHERE EXISTS (
                        SELECT * from appointment t3
                        WHERE t1.app_id=t3.rowid
                        AND t3.staff_id={staff_id}
                    );
            """)

        report = c.fetchall()

        if (len(report) < 1):
            clearConsole()
            print("No previous reports found")
        else:
            report = report[0]
            print(f"""
====================Viewing the Appointment report============

                    APPOINTMENT STATUS   : {"Completed" if report[2] == 1 else "Pending"}
                    APPOINTMENT NUMBER   : {report[0]}
                    PRESCRIPTION NUMBER  : {report[3]}
                    DOCTOR NUMBER        : {report[6]}
                    PATIENT NUMBER       : {report[5]}
                    PRESCRIPTION TYPE    : {report[4]}
                    CONSULTATION         : {report[1]}
                    QUANTITY OF MEDICINE : {report[7]}
                    DOSAGE FREQUENCY     : {report[8]}

                """)


# This class Contains all viewing tools for both patient and staff
# The receptionist is also responsible for viewing, booking and cancelling an appointment
class Receptionist:
    def __init__(self):
        pass

    #MAIN DASHBOARD
    def dashboard(self):
        clearConsole()
        print("WELEOME TO THE HOSPITAL")

        print("1: Staff Login")
        print("2: Patient Login")
        print("3: Create Account")
        print("4: View Doctors")
        print("5: View Nurses")
        print("6: View Patients")
        print("q: Quit")
        choice = input("Enter Choice: ")
        if choice == '1':
            HealthcareProfessional().staffLogin()
        elif choice == '2':
            p = Patient()
            p.patientLogin()
        elif choice == '3':
            memberChoice = input("create staff account? [y/n]: ")
            if memberChoice == 'y':
                id = HealthcareProfessional().addStaff()
                if id:
                    print("Account created, please remember the ID")
                    print("ID= ", id)
                    print("")
                else:
                    print("account not created")
            elif memberChoice == 'n':
                memberChoice = input("create patient account? [y/n]: ")
                if memberChoice == 'y':
                    id = Patient().addPatient()
                    print("accoutn created, please remember the ID")
                    print("ID= ", id)
                    print("")
                
                else:
                    print("No account created!")
            else:
                print("No account created!")
        elif choice == '4':
            Doctor().update_doctors()
            self.viewDoctors()
        elif choice == '5':
            Nurse().update_nurses()
            self.viewNurses()
        elif choice == '6':
            self.viewPatients()

        elif choice == 'q' or choice == 'Q':
            exit()
        else:
            print("Invalid Choice")

    #all data manipulation done by the receptionist 
    def manage_appointments(self,task=None,
                                patient_id=None,
                                appointment_id=None,
                                patient_name=None):

        clearConsole()
        #create an appointment 
        if task == 'make' and patient_id:
            c.execute("""
                SELECT * from healthcare_professional
                where occupied=0
            """)

            staff_list = c.fetchall()
            if (len(staff_list) > 0):               #check if there are doctors available
                print("Select one of the following Healthealthcare_professional professionals:")

                for staff in staff_list:
                    print(f"""
                        NUMBER     : {staff[0]}
                        NAME       : {staff[1]}
                        DESIGNATION: {staff[2]}

                    """)

                staff_choice = input("Enter Doctor ID (ONLY): ")
                flag = False
                for staff in staff_list:
                    if staff[0] == staff_choice and staff[2] != "nurse":
                        flag = True
                        break

                if flag:
                    appoint_type = input("Enter the type of appointment: ")
                    Appointment().bookAppointment(appoint_type, staff_choice, patient_id,
                                    patient_name)
                    conn.commit()
                else:
                    print("Invalid Doctor ID")
            else:
                print("no doctors available")

        #view the upcoming appointments
        elif task == 'view' and patient_id:
            c.execute(f"""
                SELECT rowid, * from appointment
                where pat_id = "{patient_id}"
                AND
                status=0
            """)

            _appointments = c.fetchall()

            if len(_appointments) > 0:
                _appointmentCodes = []
                for item in _appointments:
                    print(f"""
                        Appointment Number: {item[0]}
                        Appointment Type  : {item[1].capitalize()}
                    """)
                    _appointmentCodes.append(item[0])
                return _appointmentCodes
            else:
                return []

        #cancel an appointment
        elif task == 'cancel' and appointment_id:
            print("------------------------------------------------------------")
            print("Cancelling Appointment Number: ", appointment_id)
            try:

                c.execute(f"""
                    SELECT staff_id FROM appointment
                    WHERE rowid={appointment_id}
                """)

                _staff_id = c.fetchone()

                c.execute(f"""
                DELETE from appointment
                where rowid = "{appointment_id}"
                """)

                c.execute(f"""
                    DELETE from appointment_schedule
                    WHERE app_id={appointment_id}
                """)

                c.execute(f"""
                    UPDATE healthcare_professional SET occupied=0
                    WHERE employee_num={_staff_id}
                """)

                conn.commit()
                return 0
            except sqlite3.Error as er:
                print("Error", er)
            return 1

        else:
            print("No task specified")


    #list all doctors
    def viewDoctors(self):
        c.execute("""
            SELECT employee_num, name
            FROM healthcare_professional
            WHERE role = "doctor"
        """)

        doctors = c.fetchall()

        if len(doctors) >=1:
            for doc in doctors:
                print(f"{doc[1]} -- {doc[0]}")
        else:
            print("No Doctors in Hospital")
    
    #list all nurses
    def viewNurses(self):
        c.execute("""
            SELECT employee_num, name
            FROM healthcare_professional
            WHERE role = "nurse"
        """)

        nurses = c.fetchall()

        if len(nurses) >= 1 :
            for nur in nurses:
                print(f"{nur[1]} -- {nur[0]}")
        else:
            print("No nurses")

    #list all patients
    def viewPatients(self):
        c.execute("""
            SELECT rowid, name
            FROM patient
        """)

        patients = c.fetchall()

        if len(patients) >= 1 :
            for patient in patients:
                print(f"{patient[0]} -- {patient[1]}")
        else:
            print("No Patients")


#main function
def main():
    create_tables()
    displayMenu = Receptionist()
    
    displayMenu.dashboard()

    #Commit our command
    conn.commit()

    #Close our connection
    conn.close()


if __name__ == "__main__":
    main()
