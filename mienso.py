import datetime
from dateutil import easter

from flask import Flask, abort, render_template

app = Flask(__name__)
app.debug = True

FRIDAY = 4

HARD_FEASTS_EASTER_OFFSETS = (
    datetime.timedelta(days=-46),  # Ash Wednesday
    datetime.timedelta(days=-2),   # Good Friday
)

SOLEMNITIES_EASTER_OFFSETS = (
    datetime.timedelta(days=5),
    datetime.timedelta(days=68),
)

SOLEMNITIES_NOT_MOVING = (
    (1, 1),
    (1, 6),
    (3, 19),
    (3, 25),
    (4, 23),
    (5, 3),
    (5, 8),
    (6, 24),
    (6, 29),
    (8, 15),
    (8, 26),
    (11, 1),
    (12, 8),
    (12, 25),
)


def can_eat_meat(date):
    easter_date = easter.easter(date.year)

    for offset in HARD_FEASTS_EASTER_OFFSETS:
        if easter_date + offset == date:
            return False, 'hard'

    if date.weekday() == FRIDAY:
        for offset in SOLEMNITIES_EASTER_OFFSETS:
            if easter_date + offset == date:
                return True, 'solemnity'

        for solemn_month, solemn_day in SOLEMNITIES_NOT_MOVING:
            if date.month == solemn_month and date.day == solemn_day:
                return True, 'solemnity'

        return False, 'friday'

    return True, 'normal'


@app.route('/<int:year>-<int:month>-<int:day>')
def day_page(year, month, day):
    try:
        date = datetime.date(year=year, month=month, day=day)
    except ValueError:
        abort(400)

    meat, reason = can_eat_meat(date)

    if not meat:
        return render_template('{0}.html'.format(reason), date=date)

    return render_template('meat.html', date=date)


@app.route('/about')
def about_page():
    return render_template('about.html')


@app.route('/')
def index_page():
    today = datetime.date.today()
    return day_page(today.year, today.month, today.day)


if __name__ == '__main__':
    app.run()
