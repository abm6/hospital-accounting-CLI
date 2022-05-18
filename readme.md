# Hospital Accounting CLI

This program is a hands on implementation of the operations of a hospital accounting of various staff and patients managed by the hostpital receptionist.

The database has been designed using SQLite3 and SQL code and the user interaction has been written in python. In the database, there are seven tables created And their structure has been demonstrated as follows.

## TABLE STRUCTURE

- ## patient
     The patient's table keeps track of all the patients, names, addresses and phone numbers
- ## appointment
     the appointments table keeps track of all the patients and their doctors appointments.
- ## healthcare_professional
     The healthcare table is a table to keep a record of all the doctors and nurses, and they can either be occupied or unoccupied.

- ## doctor, nurse
     Now all the healthcare staffs can either be doctors and nurses. So there are separate tables created for them as well.

- ## prescription
    The prescription table consists of the prescriptions assigned by the doctor to the patient. And once the prescription gets assigned, their reference will be updated into the appointment schedule table.

- ## appointment_schedule
    The most important table that maintains the linke between all the other tables. It keeps track of the past appointments and the future upcoming appointments.

## ER DIAGRAM AND ARCHITECTURE

<img src="https://github.com/abm6/hospital-accounting-CLI/blob/main/assets/er_diagram.jpeg" />


- The program follows object oriented principles and uses respective classes for respective operations.
- The programme also handles errors properly and they have been labelled so that the user can enter the proper inputs.
- There are three classes, the patient class, the staff class and the display class and their role is to perform various operations on the type of class they belong.

# PROGRAM WORKFLOW

- Initially, there is a dashboard asking either to log in or create account or view the doctors and the nurses.

- One can create a stop account. One can create a patience account.

- The database is initially empty.

- To get an appointment, we need to create a patient account.

- And also, there should be a doctor available in the health care department.

- If there is no doctor and appointment cannot be assigned.

- after the patient books for an appointment,

- the state of staff is marked as occupied and unless the staff gives

- the prescription to the patient, the staff shall not be free.

- Both the patients and the staff can view their previous appointments,

- considering the fact that those have been completed.

- A patient may even cancel the appointment.
