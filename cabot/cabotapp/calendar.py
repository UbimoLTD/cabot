import requests
from django.conf import settings
from icalendar import Calendar


def get_calendar_data():
    feed_url = settings.CALENDAR_ICAL_URL
    resp = requests.get(feed_url)
    cal = Calendar.from_ical(resp.content)
    return cal


def get_events():
    events = []
    for component in get_calendar_data().walk():
        if component.name == 'VEVENT':
            gruop = component.decoded('summary').split(' ', 1)[0]
            events.append({
                'group': gruop,
                'start': component.decoded('dtstart'),
                'end': component.decoded('dtend'),
                'attendee': component.get('attendee'),
                'uid': component.decoded('uid'),
            })
    return events
