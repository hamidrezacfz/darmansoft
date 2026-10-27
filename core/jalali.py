from datetime import date, datetime


PERSIAN_DIGITS = str.maketrans('0123456789', '۰۱۲۳۴۵۶۷۸۹')
ENGLISH_DIGITS = str.maketrans('۰۱۲۳۴۵۶۷۸۹', '0123456789')


def to_jalali(value, with_time=False):
    """Convert a Gregorian date/datetime to a Persian Jalali string."""
    if not value:
        return ''
    if isinstance(value, datetime):
        source = value
        value = value.date()
    else:
        source = None
    gy, gm, gd = value.year, value.month, value.day
    g_day_no = 365 * (gy - 1600) + ((gy - 1597) // 4) - ((gy - 1501) // 100) + ((gy - 1201) // 400)
    g_d_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    g_day_no += g_d_m[gm - 1] + gd - 1
    if gm > 2 and (gy % 4 == 0 and (gy % 100 != 0 or gy % 400 == 0)):
        g_day_no += 1
    j_day_no = g_day_no - 79
    j_np = j_day_no // 12053
    j_day_no %= 12053
    jy = 979 + 33 * j_np + 4 * (j_day_no // 1461)
    j_day_no %= 1461
    if j_day_no >= 366:
        jy += (j_day_no - 1) // 365
        j_day_no = (j_day_no - 1) % 365
    jm = 1 if j_day_no < 186 else 7
    jd = j_day_no + 1 if j_day_no < 186 else j_day_no - 185
    result = f'{jy:04d}/{jm:02d}/{jd:02d}'
    if with_time and source:
        result += f' {source.hour:02d}:{source.minute:02d}'
    return result.translate(PERSIAN_DIGITS)


def from_jalali(value):
    """Parse Jalali or Gregorian YYYY/MM/DD input as a Gregorian date."""
    value = (value or '').strip().translate(ENGLISH_DIGITS).replace('-', '/')
    year, month, day = map(int, value.split('/'))
    if year > 1700:
        return date(year, month, day)
    jy = year + 1595
    days = -355668 + (365 * jy) + (jy // 33 * 8) + (((jy % 33) + 3) // 4) + day
    days += (month - 1) * 31 if month < 7 else ((month - 7) * 30 + 186)
    gy = 400 * (days // 146097)
    days %= 146097
    if days > 36524:
        gy += 100 * ((days - 1) // 36524)
        days = (days - 1) % 36524
        if days >= 365:
            days += 1
    gy += 4 * (days // 1461)
    days %= 1461
    if days > 365:
        gy += (days - 1) // 365
        days = (days - 1) % 365
    gd = days + 1
    leap = gy % 4 == 0 and (gy % 100 != 0 or gy % 400 == 0)
    lengths = [31, 29 if leap else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    gm = 1
    for length in lengths:
        if gd <= length:
            break
        gd -= length
        gm += 1
    return date(gy, gm, gd)


def from_jalali_datetime(value):
    value = (value or '').strip().translate(ENGLISH_DIGITS)
    date_text, _, time_text = value.replace('T', ' ').partition(' ')
    parsed_date = from_jalali(date_text)
    if not time_text:
        return datetime.combine(parsed_date, datetime.min.time())
    hour, minute = map(int, time_text.strip().split(':')[:2])
    return datetime(parsed_date.year, parsed_date.month, parsed_date.day, hour, minute)
