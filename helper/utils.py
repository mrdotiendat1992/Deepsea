from datetime import datetime
import calendar

def is_date(date):
    try:
        if isinstance(date, str):
            date = datetime.strptime(date, "%Y-%m-%d") or datetime.strptime(date, "%d/%m/%Y")
        return isinstance(date, datetime)
    except:
        return False
    
def is_integer(number):
    try:
        number = float(number)
        return number.is_integer()
    except ValueError:
        return False

def is_float(number):
    try:
        number = float(number)
        return number % 1 != 0
    except ValueError:
        return False

def is_number(number):
    return is_integer(number) or is_float(number)

def get_days_in_month(month, year):
    return calendar.monthrange(year, month)[1]