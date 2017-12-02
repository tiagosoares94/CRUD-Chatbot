from telepot import namedtuple
import calendar

def create_calendar (month:int, year:int, command:str):
    markup = namedtuple.InlineKeyboardMarkup()
    options = []
    options.append([namedtuple.InlineKeyboardButton(
        text = calendar.month_name[month] + ' ' + str(year),
        callback_data = 'ignore'
    )])
    week_days = ["M","T","W","R","F","S","U"]
    options.append([
        namedtuple.InlineKeyboardButton(
            text = day,
            callback_data = 'ignore'
        ) for day in week_days
    ])
    my_calendar = calendar.monthcalendar(year, month)
    for week in my_calendar:
        row = []
        for day in week:
            if day == 0:
                row.append(namedtuple.InlineKeyboardButton(
                    text = ' ',
                    callback_data = 'ignore'
                ))
            else:
                row.append(namedtuple.InlineKeyboardButton(
                    text = str(day),
                    callback_data = '{}_{}-{}-{}'.format(
                        command,
                        year,
                        month,
                        day
                    )
                ))
        options.append(row)
    options.append([namedtuple.InlineKeyboardButton(
        text = "<",
        callback_data = "{}_calendar_previous-month".format(command)
    )])
    options.append([namedtuple.InlineKeyboardButton(
        text = " ",
        callback_data = "{}_calendar_ignore".format(command)
    )])
    options.append([namedtuple.InlineKeyboardButton(
        text = ">",
        callback_data = "{}_calendar_next-month".format(command)
    )])
    return namedtuple.InlineKeyboardMarkup(inline_keyboard=options)

def next_month (month:int, year:int):
    if month == 12:
        return {'month': 1, 'year': year + 1}
    return {'month': month + 1, 'year': year}

def previous_month (month:int, year:int):
    if month == 1:
        return {'month': 12, 'year': year - 1}
    return {'month': month - 1, 'year': year}
