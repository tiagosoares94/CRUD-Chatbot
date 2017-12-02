'''
Contém as operações relacionadas ao banco de dados.
'''
import sqlite3
import os

class Database():
    '''
    Class that handles the database operations.
    '''
    def __init__(self, istest=False):
        '''
        Initialize the database
        '''
        database_exists = os.path.isfile('main.db')
        if istest:
            self.connection = sqlite3.connect(
                ':memory:',
                detect_types=sqlite3.PARSE_DECLTYPES,
                check_same_thread=False
            )
        else:
            self.connection = sqlite3.connect(
                'main.db',
                detect_types=sqlite3.PARSE_DECLTYPES,
                check_same_thread=False
            )
        self.cursor = self.connection.cursor()

        if not database_exists or istest:
            self.create_schema()

    def create_schema(self):
        '''
        Cria o schema do banco de dados caso ele não exista.
        '''
        self.cursor.execute(
            '''
            CREATE TABLE doctors (
                id INTEGER PRIMARY KEY NOT NULL,
                first_name CHAR(40) NOT NULL,
                last_name CHAR(40) NOT NULL,
                telegram_id INT NOT NULL,
                address char(200)
            )
            '''
        )
        self.cursor.execute(
            '''
            CREATE TABLE patients (
                id INTEGER PRIMARY KEY NOT NULL,
                first_name CHAR(40) NOT NULL,
                last_name CHAR(40) NOT NULL,
                birth_date DATE NOT NULL,
                telegram_id INT NOT NULL
            )
            '''
        )
        self.cursor.execute(
            '''CREATE TABLE appointments (
                id INTEGER PRIMARY KEY NOT NULL,
                date DATETIME NOT NULL,
                address char(200),
                doctor_id INT NOT NULL,
                patient_id INT NOT NULL,
                status INT NOT NULL DEFAULT 0,
                FOREIGN KEY(doctor_id) REFERENCES doctors(id),
                FOREIGN KEY(patient_id) REFERENCES patients(id)
            )
            '''
        )
        self.connection.commit()

    def new_doctor(self, doctor):
        '''
        Creates a new doctor row on the database.
        '''
        args = (
            None,
            doctor['first_name'],
            doctor['last_name'],
            doctor['telegram_id']
        )
        self.cursor.execute(
            '''
            INSERT INTO doctors
            VALUES (?, ?, ?, ?)
            ''', args
        )

    def new_patient(self, patient):
        '''
        Creates a new patient row on the database.
        '''
        args = (
            None,
            patient['first_name'],
            patient['last_name'],
            patient['birth_date'],
            patient['telegram_id']
        )
        self.cursor.execute(
            '''
            INSERT INTO patients
            VALUES (?, ?, ?, ?, ?)
            ''', args
        )

    def new_appointment(self, appointment):
        '''
        Creates a new appointment row on the database.
        '''
        args = (
            None,
            appointment['when'],
            appointment['address'],
            appointment['doctor_id'],
            appointment['patient_id'],
            appointment['status'] if 'status' in appointment else 0
        )
        self.cursor.execute(
            '''
            INSERT INTO appointments
            VALUES (?, ?, ?, ?, ?, ?)
            ''', args
        )
        self.connection.commit()

    def get_doctor(self, doctor_id):
        '''
        Get doctor by its id
        '''
        args = (str(doctor_id))
        self.cursor.execute(
            '''
            SELECT * FROM doctors WHERE id = ?
            ''', args
        )
        record = self.cursor.fetchone()
        return {
            'id' : record[0],
            'first_name' : record[1],
            'last_name' : record[2],
            'telegram_id' : record[3]
        }

    def get_patient(self, patient_id):
        '''
        Get patient by its id
        '''
        args = (str(patient_id))
        self.cursor.execute(
            '''
            SELECT * FROM patients WHERE id = ?
            ''', args
        )
        record = self.cursor.fetchone()
        return {
            'id' : record[0],
            'first_name' : record[1],
            'last_name' : record[2],
            'birth_date' : record[3],
            'telegram_id' : record[4]
        }

    def get_patient_by_telegram_id(self, telegram_id):
        '''
        Get patient by telegram's id
        '''
        self.cursor.execute(
            '''
            SELECT * FROM patients WHERE telegram_id = (?)
            ''', (telegram_id,)
        )
        record = self.cursor.fetchone()
        return {
            'id' : record[0],
            'first_name' : record[1],
            'last_name' : record[2],
            'birth_date' : record[3],
            'telegram_id' : record[4]
        }

    def get_appointments(self, patient_id):
        '''
        Returns all patient's appointments
        '''
        args = (str(patient_id))
        self.cursor.execute(
            '''
            SELECT * FROM appointments WHERE patient_id = ?
            ''', args
        )
        records = [{
            'id' : record[0],
            'date': record[1],
            'address' : record[2],
            'doctor_id' : record[3],
            'patient_id' : record[4],
            'status' : Database.get_appointment_status(record[5])
        } for record in self.cursor.fetchall()]
        return records

    def get_appointment(self, appointment_id):
        '''
        Returns all patient's appointments
        '''
        args = (str(appointment_id))
        self.cursor.execute(
            '''
            SELECT * FROM appointments WHERE id = ?
            ''', args
        )
        data = self.cursor.fetchone()
        return {
            'id' : data[0],
            'date': data[1],
            'address' : data[2],
            'doctor_id' : data[3],
            'patient_id' : data[4],
            'status' : Database.get_appointment_status(data[5])
        }

    def update_appointment_date(self, appointment_id, new_date):
        '''
        Updates an appointment date
        '''
        try:
            self.cursor.execute(
                '''
                UPDATE appointments SET date = '{}' WHERE id = {}
                '''.format(new_date, appointment_id)
            )
            self.connection.commit()
        except Exception:
            return False
        return True

    def delete_appointments(self, patient_id):
        '''
        Delete patient's appointments
        '''
        self.cursor.execute(
            '''
            DELETE FROM appointments WHERE patient_id = (?)
            ''', str(patient_id)
        )
        self.connection.commit() # commits changes to the database

    def get_doctors(self):
        '''
        Returns doctors
        '''
        self.cursor.execute(
            '''
            SELECT * FROM doctors LIMIT 5
            '''
        )
        return [{
            'id' : record[0],
            'first_name' : record[1],
            'last_name' : record[2],
            'telegram_id' : record[3]
        } for record in self.cursor.fetchall()]

    def get_doctors_by_id(self, doctors_ids):
        '''
        Return doctors based on their ids on the database
        '''
        self.cursor.execute(
            '''
            SELECT id, first_name, last_name, address FROM doctors WHERE id IN ({})
            '''.format(','.join([str(d_id) for d_id in doctors_ids]))
        )
        return [{
            'id' : record[0],
            'first_name': record[1],
            'last_name': record[2],
            'address' : record[3]
        } for record in self.cursor.fetchall()]

    def get_doctor_address(self, doctor_id):
        '''
        Return doctor address
        '''
        doctors = self.get_doctors_by_id([doctor_id])
        for doc in doctors:
            return doc['address']
        return 'UNDEFINED_ADDRESS'

    def create_appointment(self, doctor_id, patient_id, date):
        address = self.get_doctor_address(doctor_id)
        try:
            self.cursor.execute(
                '''
                INSERT INTO appointments VALUES (NULL, '{}', '{}', {}, {}, {})
                '''.format(str(date), address, doctor_id, patient_id, '1')
            )
            self.connection.commit()
        except Exception as e:
            return False
        return True

    @staticmethod
    def get_appointment_status(status: int):
        '''
        Converts the status from integer to string.
        '''
        if status == 0:
            return 'scheduled'
        elif status == 1:
            return 'done'
        return 'canceled'

if __name__ == '__main__':
    Database().create_schema()
