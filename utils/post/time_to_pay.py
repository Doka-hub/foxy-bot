import datetime


def timedelta_to_hours(duration: datetime) -> int:
    # преобразование в часы, минуты и секунды
    days, seconds = duration.days, duration.seconds
    hours = days * 24 + seconds // 3600
    return hours
