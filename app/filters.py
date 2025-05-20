from datetime import datetime

def number_format(value):
    """Форматирует число с разделителями тысяч"""
    return "{:,}".format(value).replace(",", " ")

def time_ago(dt):
    now = datetime.utcnow()
    diff = now - dt
    
    seconds = diff.total_seconds()
    intervals = (
        ('год', 31536000),
        ('месяц', 2592000),
        ('неделя', 604800),
        ('день', 86400),
        ('час', 3600),
        ('минута', 60),
        ('секунда', 1)
    )
    
    for unit, count in intervals:
        value = seconds // count
        if value >= 1:
            unit = pluralize_ru(value, unit)
            return f"{int(value)} {unit} назад"
    
    return "только что"

def pluralize_ru(value, unit):
    if unit == 'месяц':
        forms = ('месяц', 'месяца', 'месяцев')
    elif unit == 'день':
        forms = ('день', 'дня', 'дней')
    else:
        forms = {
            'год': ('год', 'года', 'лет'),
            'неделя': ('неделю', 'недели', 'недель'),
            'час': ('час', 'часа', 'часов'),
            'минута': ('минуту', 'минуты', 'минут'),
            'секунда': ('секунду', 'секунды', 'секунд')
        }.get(unit, (unit, unit, unit))
    
    if value % 10 == 1 and value % 100 != 11:
        return forms[0]
    elif 2 <= value % 10 <= 4 and (value % 100 < 10 or value % 100 >= 20):
        return forms[1]
    else:
        return forms[2]