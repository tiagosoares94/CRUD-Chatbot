'''
Unit tests for database.py
'''
import datetime

def test_assert_tables_were_created():
    '''
    Assert that every table was created.
    '''
    from database import Database
    # assert doctor table was created
    bot_database = Database(True)
    bot_database.new_doctor({
        'first_name' : 'Doc',
        'last_name' : 'McDoc',
        'telegram_id' : '1000'
    })
    result = bot_database.get_doctor(1)
    assert result['first_name'] == 'Doc'
    assert result['id'] != None

    # assert patient table was created
    bot_database.new_patient({
        'first_name' : 'Pat',
        'last_name' : 'McPat',
        'birth_date' : '',
        'telegram_id' : '1001'
    })
    result = bot_database.get_patient(1)
    assert result['first_name'] == 'Pat'
    assert result['id'] != None

    bot_database.new_appointment({
        'when' : str(datetime.datetime.now()),
        'address' : 'Fifth Street, 100 Block D',
        'doctor_id' : 1,
        'patient_id' : 1
    })
    result = bot_database.get_appointments(1)

    assert len(result) == 1
