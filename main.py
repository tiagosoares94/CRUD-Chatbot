import datetime
import sys
import time
import telepot
import doctors
import appointments
from context import UserContext
import inline_calendar
from database import Database

from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

USERS_CONTEXTS = {}

def greet_message(chat_id:int):
    BOT.sendMessage(
        chat_id,
        'What do you want to do?',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text='Schedule an appointment 🗓️',
                callback_data='schedule_appointment'
            )],
            [InlineKeyboardButton(
                text='Check my appointments 📑',
                callback_data='check_appointments'
            )],
            [InlineKeyboardButton(
                text='Cancel an appointment ❌',
                callback_data='cancel_appointment'
            )]
        ])
    )

def handle(msg):
    '''
    Handles the incoming messages.
    '''
    flavor = telepot.flavor(msg)

    if flavor == 'chat':
        # pylint: disable=W0612
        content_type, chat_type, chat_id = telepot.glance(msg)
        if content_type == 'text':
            greet_message(int(chat_id))
            if chat_id not in USERS_CONTEXTS:
                USERS_CONTEXTS[chat_id] = UserContext(chat_id)

    elif flavor == 'callback_query':
        # pylint: disable=W0612
        msg_id, chat_id, text = telepot.glance(msg, flavor=flavor)
        if text == 'schedule_appointment':
            doctor_options = doctors.get_doctors(BOT_DATABASE)
            if doctor_options is not None:
                BOT.sendMessage(
                    chat_id,
                    'These are the available doctors:',
                    reply_markup=doctor_options
                )
            else:
                BOT.sendMessage(chat_id, 'No doctors were found, sorry!')
        elif text == 'check_appointments':
            patient_record = BOT_DATABASE.get_patient_by_telegram_id(chat_id)
            if patient_record is not None:
                BOT.sendMessage(
                    chat_id,
                    'Your scheduled appointments:',
                    reply_markup=appointments.get_appointments(
                        BOT_DATABASE,
                        patient_record['id']
                    )
                )
        elif text == 'cancel_appointment':
            # cancel user's current appointments
            patient_record = BOT_DATABASE.get_patient_by_telegram_id(chat_id)
            BOT.sendMessage(
                chat_id,
                'DELETED',
                reply_markup = BOT_DATABASE.delete_appointments(patient_record['id'])
            )
        elif text.startswith('remove_appointment_'):
            # cancel a specific appointment
            pass
        elif text.startswith('doctor_'):
            if chat_id not in USERS_CONTEXTS:
                USERS_CONTEXTS[chat_id] = UserContext(chat_id)
            USERS_CONTEXTS[chat_id].selected_doctor = text.replace('doctor_', '')
            cal_msg = BOT.sendMessage(
                chat_id,
                'Available days',
                reply_markup=inline_calendar.create_calendar(
                    USERS_CONTEXTS[chat_id].selected_month,
                    USERS_CONTEXTS[chat_id].selected_year,
                    'selected_day'
                )
            )
            setLastCalendarMessageId(chat_id, cal_msg['message_id'])
        elif text.startswith('calendar_'):
            if text == 'calendar_previous-month':
                deleteLastCalendarMessage(chat_id)
                m = inline_calendar.previous_month(
                    USERS_CONTEXTS[chat_id].selected_month,
                    USERS_CONTEXTS[chat_id].selected_year
                )
                setNewDate(chat_id, m['month'], m['year'])
                cal_msg = BOT.sendMessage(
                    chat_id,
                    'This is the previous month:',
                    reply_markup=inline_calendar.create_calendar(
                        m['month'],
                        m['year'],
                        'selected_day'
                    )
                )
                setLastCalendarMessageId(chat_id, cal_msg['message_id'])
            elif text == 'calendar_next-month':
                deleteLastCalendarMessage(chat_id)
                m = inline_calendar.next_month(
                    USERS_CONTEXTS[chat_id].selected_month,
                    USERS_CONTEXTS[chat_id].selected_year
                )
                setNewDate(chat_id, m['month'], m['year'])
                cal_msg = BOT.sendMessage(
                    chat_id,
                    'This is the next month:',
                    reply_markup=inline_calendar.create_calendar(
                        m['month'],
                        m['year'],
                        'selected_day'
                    )
                )
                setLastCalendarMessageId(chat_id, cal_msg['message_id'])
        elif text.startswith('selected_day_'):
            # user selected a date to schedule
            if chat_id in USERS_CONTEXTS and USERS_CONTEXTS[chat_id].selected_doctor is not None:
                if 'calendar_next-month' in text:
                    deleteLastCalendarMessage(chat_id)
                    next_month = inline_calendar.next_month(
                        USERS_CONTEXTS[chat_id].selected_month,
                        USERS_CONTEXTS[chat_id].selected_year
                    )
                    USERS_CONTEXTS[chat_id].selected_month = next_month['month']
                    USERS_CONTEXTS[chat_id].selected_year = next_month['year']
                    cal_msg = BOT.sendMessage(
                        chat_id,
                        'This is the next month:',
                        reply_markup=inline_calendar.create_calendar(
                            USERS_CONTEXTS[chat_id].selected_month,
                            USERS_CONTEXTS[chat_id].selected_year,
                            'selected_day'
                        )
                    )
                    setLastCalendarMessageId(chat_id, cal_msg['message_id'])
                elif 'calendar_previous-month' in text:
                    deleteLastCalendarMessage(chat_id)
                    previous_month = inline_calendar.previous_month(
                        USERS_CONTEXTS[chat_id].selected_month,
                        USERS_CONTEXTS[chat_id].selected_year
                    )
                    USERS_CONTEXTS[chat_id].selected_month = previous_month['month']
                    USERS_CONTEXTS[chat_id].selected_year = previous_month['year']
                    cal_msg = BOT.sendMessage(
                        chat_id,
                        'This is the previous month:',
                        reply_markup=inline_calendar.create_calendar(
                            USERS_CONTEXTS[chat_id].selected_month,
                            USERS_CONTEXTS[chat_id].selected_year,
                            'selected_day'
                        )
                    )
                    setLastCalendarMessageId(chat_id, cal_msg['message_id'])
                else:
                    calendar_day = text.replace('selected_day_', '').split('-')
                    patient_id = BOT_DATABASE.get_patient_by_telegram_id(chat_id)['id']
                    schedule_result = appointments.scheduleAt(
                        BOT_DATABASE,
                        USERS_CONTEXTS[chat_id].selected_doctor,
                        patient_id,
                        calendar_day[0],
                        calendar_day[1],
                        calendar_day[2]
                    )
                    deleteLastCalendarMessage(chat_id)
                    if schedule_result:
                        BOT.sendMessage(
                            chat_id,
                            'Scheduled successfully! 👌'
                        )
                    else:
                        BOT.sendMessage(
                            chat_id,
                            'Sorry about that. 🙇 Something went wrong. Please try again in a few minutes.'
                        )
        elif text.startswith('view_appointment_'):
            if chat_id in USERS_CONTEXTS:
                patient_id = BOT_DATABASE.get_patient_by_telegram_id(chat_id)['id']
                appointment_id = int(text.replace('view_appointment_', ''))
                appointment = BOT_DATABASE.get_appointment(appointment_id)
                if (appointment['patient_id'] == patient_id):
                    BOT.sendMessage(
                        chat_id,
                        'Do you want to reschedule this appointment?',
                        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                            [
                                InlineKeyboardButton(
                                    text='Yes',
                                    callback_data='reschedule_{}'.format(appointment_id)
                                ),
                                InlineKeyboardButton(
                                    text='No',
                                    callback_data='do fucking nothing'
                                )
                            ]
                        ])
                    )
        elif text.startswith('do fucking nothing'):
            greet_message(int(chat_id))
        elif text.startswith('reschedule_'):
            deleteLastCalendarMessage(chat_id)
            today = datetime.date.today()
            USERS_CONTEXTS[chat_id].selected_month = today.month
            USERS_CONTEXTS[chat_id].selected_day = today.day
            cal_msg = BOT.sendMessage(
                chat_id,
                'Available days',
                reply_markup=inline_calendar.create_calendar(
                    USERS_CONTEXTS[chat_id].selected_month,
                    USERS_CONTEXTS[chat_id].selected_year,
                    'appointment_reschedule_{}'.format(
                        text.replace('reschedule_', '')
                    )
                )
            )
            setLastCalendarMessageId(chat_id, cal_msg['message_id'])
        elif text.startswith('appointment_reschedule_'):
            if 'calendar_next-month' in text:
                # show the next month
                deleteLastCalendarMessage(chat_id)
                next_month = inline_calendar.next_month(
                    USERS_CONTEXTS[chat_id].selected_month,
                    USERS_CONTEXTS[chat_id].selected_year
                )
                USERS_CONTEXTS[chat_id].selected_month = next_month['month']
                USERS_CONTEXTS[chat_id].selected_year = next_month['year']
                cal_msg = BOT.sendMessage(
                    chat_id,
                    'Available days',
                    reply_markup=inline_calendar.create_calendar(
                        USERS_CONTEXTS[chat_id].selected_month,
                        USERS_CONTEXTS[chat_id].selected_year,
                        'appointment_reschedule_{}'.format(
                            text.replace('appointment_reschedule_', '').replace('_calendar_next-month', '')
                        )
                    )
                )
                setLastCalendarMessageId(chat_id, cal_msg['message_id'])
            elif 'calendar_previous-month' in text:
                # show the previous month
                deleteLastCalendarMessage(chat_id)
                previous_month = inline_calendar.previous_month(
                    USERS_CONTEXTS[chat_id].selected_month,
                    USERS_CONTEXTS[chat_id].selected_year
                )
                USERS_CONTEXTS[chat_id].selected_month = previous_month['month']
                USERS_CONTEXTS[chat_id].selected_year = previous_month['year']
                cal_msg = BOT.sendMessage(
                    chat_id,
                    'Available days',
                    reply_markup=inline_calendar.create_calendar(
                        USERS_CONTEXTS[chat_id].selected_month,
                        USERS_CONTEXTS[chat_id].selected_year,
                        'appointment_reschedule_{}'.format(
                            text.replace('appointment_reschedule_', '').replace('calendar_previous-month', '')
                        )
                    )
                )
                setLastCalendarMessageId(chat_id, cal_msg['message_id'])
            else:
                # ex: appointment_reschedule_1_2017-11-25
                data = text.replace('appointment_reschedule_', '')
                appointment_id = data.split('_')[0]
                selected_date = data.split('_')[1]
                update_result = BOT_DATABASE.update_appointment_date(
                    appointment_id,
                    datetime.date(
                        int(selected_date.split('-')[0]),
                        int(selected_date.split('-')[1]),
                        int(selected_date.split('-')[2])
                    )
                )
                if update_result:
                    BOT.sendMessage(
                        chat_id,
                        'Rescheduled successfully!'
                    )
                else:
                    BOT.sendMessage(
                        chat_id,
                        'There was an error trying to reschedule your appointment. Sorry.'
                    )

def setNewDate (chat_id:int, month:int, year:int):
    if chat_id in USERS_CONTEXTS:
        USERS_CONTEXTS[chat_id].selected_month = month
        USERS_CONTEXTS[chat_id].selected_year = year

def deleteLastCalendarMessage(chat_id):
    if chat_id in USERS_CONTEXTS and USERS_CONTEXTS[chat_id].last_calendar_message is not None:
        try:
            BOT.deleteMessage((chat_id, USERS_CONTEXTS[chat_id].last_calendar_message))
        except telepot.exception.TelegramError as e:
            print('Erro ao apagar a mensagem. Provavelmente já foi apagada. Ignorando comando...')

def setLastCalendarMessageId(chat_id, message_id):
    if chat_id in USERS_CONTEXTS:
        USERS_CONTEXTS[chat_id].last_calendar_message = message_id

BOT_DATABASE = Database()
API_TOKEN = sys.argv[1]
BOT = telepot.Bot(API_TOKEN)
MessageLoop(BOT, handle).run_as_thread()
print('Working...')

while 1:
    time.sleep(10)
