'''
class related to doctors
'''
from database import Database
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

def get_doctors(_db: Database):
    '''
    Return buttons
    '''
    doctors = _db.get_doctors()
    options = [InlineKeyboardButton(
        text='{} {}'.format(doctor['first_name'], doctor['last_name']),
        callback_data='doctor_{}'.format(doctor['id'])
    ) for doctor in doctors]
    if doctors:
        return InlineKeyboardMarkup(
            inline_keyboard=[[doctor] for doctor in options]
        )
    return None

def get_doctors_by_id(_db: Database, doctor_ids):
    '''
    Return doctors by ids
    '''
    doctors = _db.get_doctors_by_id(doctor_ids)
    result = {}
    for record in doctors:
        result[record['id']] = record
    return result

def get_doctor_address(_db: Database, doctor_id):
    '''
    Return doctor address
    '''
    doctors = _db.get_doctors_by_id([doctor_id])
    for doc in doctors:
        return doc['address']
    return 'UNDEFINED_ADDRESS'
