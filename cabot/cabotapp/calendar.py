import requests
from django.conf import settings
from icalendar import Calendar
import dateutil.rrule as r
import time

def get_calendar_data():
    feed_url = settings.CALENDAR_ICAL_URL
    resp = requests.get(feed_url)
    cal = Calendar.from_ical(resp.content)
    return cal


def get_events():
    events = []
    for component in get_calendar_data().walk():
        if component.name == 'VEVENT':
            group = component.decoded('summary').split(' ', 1)[0]
            repeated = get_repeated(component, group)

            if not repeated:
                events.append({
                    'group': group,
                    'start': component.decoded('dtstart'),
                    'end': component.decoded('dtend'),
                    'attendee': component.get('attendee'),
                    'uid': component.decoded('uid'),
                })
            else:
                events += repeated
    return events

def get_repeated(event, group):
    rrule = event.get('rrule')
    events = []

    if rrule is None:
        return False

    kwargs = { 'dtstart': event.decoded('dtstart') }

    try:
        kwargs['count'] = rrule.get('count')[0]
    except TypeError:
        kwargs['until'] = rrule.get('until')[0]

    repeated = list(r.rrule(getattr(r, rrule.get('freq')[0]), **kwargs))

    for e in repeated:
        event_date = event.decoded('dtend') - event.decoded('dtstart') + e
        events.append({
            'group': group,
            'start': e,
            'end': event_date,
            'attendee': event.get('attendee'),
            'uid': '{0}_{1}'.format(int(time.mktime(event_date.timetuple())), event.decoded('uid')),
        })

    return events