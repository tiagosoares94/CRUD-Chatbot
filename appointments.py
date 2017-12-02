'''
Encapsulamento das consultas
'''
import datetime
import doctors as docs
from database import Database
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

def get_appointments (db:Database, patient_id):
    '''
    Return appointments
    '''
    appointments = db.get_appointments(patient_id)
    doctors_ids = [app['doctor_id'] for app in appointments]
    doctors = docs.get_doctors_by_id(db, doctors_ids)
    options = [InlineKeyboardButton(
        text = '{} at {} with {}'.format(
            app['address'],
            app['date'],
            '{} {}'.format(
                doctors[app['doctor_id']]['first_name'],
                doctors[app['doctor_id']]['last_name']
            )
        ),
        callback_data = 'view_appointment_{}'.format(app['id'])
    ) for app in appointments]
    if appointments:
        return InlineKeyboardMarkup(
            inline_keyboard=[[app] for app in options]
        )
    return None

def scheduleAt (db: Database, doctor_id, patient_id, year, month, day):
    # idealmente aqui deveríamos verificar se é possível agendar nesse dia
    # com este médico, porém por motivos de DEADLINE não será possível fazer
    # isso nesse proof of concept
    return db.create_appointment(doctor_id, patient_id, datetime.date(
        int(year),
        int(month),
        int(day)
    ))

def update_appointment_date(db: Database, appointment_id, new_date):
    return db.update_appointment_date(appointment_id, new_date)
