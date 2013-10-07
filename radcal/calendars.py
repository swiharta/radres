import calendar
#from django.contrib.auth.models import User
from django.template.loader import render_to_string
from dateutil.relativedelta import relativedelta
from datetime import date, timedelta
from itertools import groupby
from utils import get_conflict_ids, get_last_update_time
from templatetags.my_tags import humanize_timeuntil, humanize_timesince

class CallCalendar(calendar.HTMLCalendar):

    def __init__(self, shifts, user, residents, *args, **kw):
        super(CallCalendar, self).__init__()
        self.shifts = self.group_by_day(shifts)
        self.user = user
        if not residents:
          residents = []
        self.residents = residents
        self.conflict_ids = get_conflict_ids()
#        print self.conflict_ids
#
    def formatday(self, day, weekday):
        if day:
            cssclass = self.cssclasses[weekday]
            if date.today() == date(self.year, self.month, day):
                cssclass += ' today'
            elif date.today() + timedelta(days = 1) == date(self.year, self.month, day):
                cssclass += ' tomorrow'
#            elif date.today() - timedelta(days = 1) == date(self.year, self.month, day):
#                cssclass += ' yesterday'
#            elif date.today() + timedelta(days = 7) == date(self.year, self.month, day):
#                cssclass += ' week_forward'
#            elif date.today() - timedelta(days = 7) == date(self.year, self.month, day):
#                cssclass += ' week_back'
            if day in self.shifts:
                cssclass += ' filled'
                events = []
                for event in self.shifts[day]:
                    event.classes = ''
                    if event.id in self.conflict_ids:
                      event.conflict = True
                      event.classes += ' conflict'
                    if event.shift.cash:
                      event.classes += ' moon'
                    elif event.shift.abbr[:2] == "ED":
                      event.classes += ' ED'
                    elif event.shift.abbr == "Angio":
                      event.classes += ' IR'
                    elif event.shift.day_call:
                      event.classes += ' day'
                    # haven't figured out how to access the user object without generating 1 query per cycle, despite select_related()
#                    if event.user == self.user:
#                      event.classes += ' you'
                    if event.user_id in self.residents:
                      event.classes += ' selected'
#                    try:
#                      # moderation_status: rejected = 0, approved = 1, pending = 2
#                      if event.moderated_object.moderation_status == 2:
#                        event.classes += ' moderating'
#                    except ModeratedObject.DoesNotExist: pass
                    if event.pending:
                      event.classes += ' moderating'
                    events.append(event)
                d = {'events': events, 'day_number': day}
                body = render_to_string("radcal/day_cell.html", d)
                return self.day_cell(cssclass, '%s' % body)
            body = '<ul><li>' + str(day) + '</li></ul>'
            return self.day_cell(cssclass, body)
        return self.day_cell('noday', '&nbsp;')

    def formatweek(self, week, **kw):
        s = ''.join(self.formatday(d, wd) for (d, wd) in week)
        return '<tr class="week">%s</tr>' % s

    def formatweekheader(self):
        s = ''.join(self.formatweekday(i) for i in self.iterweekdays())
#        return '<tr>%s<td>&nbsp;</td></tr>' % s
        return '<tr>%s</tr>' % s
    
    def formatmonth(self, year, month, **kw):
        self.year, self.month = year, month
        return super(CallCalendar, self).formatmonth(year, month, **kw)

    def formatmonthname(self, year, month, withyear=True):
        first = date(year, month, 1)
        next_first = first + relativedelta(months=+1)
        prev_first = first - relativedelta(months=+1)
        if withyear:
            s = '%s %s' % (calendar.month_name[month], year)
        else:
            s = '%s' % calendar.month_name[month]
        p = '%s %s' % (calendar.month_name[prev_first.month], prev_first.year)
        n = '%s %s' % (calendar.month_name[next_first.month], next_first.year)
        pf = '%s %s' % (prev_first.month, prev_first.year)
        nf = '%s %s' % (next_first.month, next_first.year)
        sf = '%s %s' % (month, year)
#        updated = get_last_update_time()
        updated = humanize_timesince(get_last_update_time())
        return '<tr id="month_nav"><th id="%s" class="this_month" colspan="7"><span id="%s" class="new_month" title="%s" onclick=""><</span><span id="%s" class="new_month" title="%s" onclick="">></span>\
                &nbsp; %s</th></tr><tr><th colspan="7">updated %s</th></tr>' % (sf, pf, p, nf, n, s, updated)

    def group_by_day(self, shifts):
        field = lambda shift: shift.date.day
        return dict(
            [(day, list(items)) for day, items in groupby(shifts, field)]
        )

    def day_cell(self, cssclass, body):
        return '<td class="%s">%s</td>' % (cssclass, body)

class UserCalendar(calendar.HTMLCalendar):

    def __init__(self, shifts, *args, **kw):
        super(UserCalendar, self).__init__()
        self.shifts = self.group_by_day(shifts)
#
    def formatday(self, day, weekday):
        if day:
            cssclass = self.cssclasses[weekday]
            if date.today() == date(self.year, self.month, day):
                cssclass += ' today'
            if day in self.shifts:
                cssclass += ' filled'
                body = ['<ul>']
                for event in self.shifts[day]:
#                    moderating = ''
#                    try:
#                      # moderation_status: rejected = 0, approved = 1, pending = 2
#                      if event.moderated_object.moderation_status == 2:
#                          moderating = 'moderating'
#                    except ModeratedObject.DoesNotExist: pass
                    event.classes = ''
                    if event.shift.cash:
                      event.classes += ' moon'
                    elif event.shift.abbr[:2] == "ED":
                      event.classes += ' ED'
                    elif event.shift.abbr == "Angio":
                      event.classes += ' IR'
                    elif event.shift.day_call:
                      event.classes += ' day'
                    body.append('<li id=' + event.shift.abbr + '_' + str(event.date) + '_' +\
                                event.user.username + '_' + str(event.id) + ' class=' + event.classes + '>')
#                    body.append('<a href="%s">' % event.get_absolute_url())
                    start = event.shift.start_time.strftime('%I:%M %p').lstrip('0')
                    end = event.shift.end_time.strftime('%I:%M %p').lstrip('0')
                    cash = event.shift.cash
                    if cash:
                      title =  '%s<br />%s-%s<br />$%s' % (event.shift.name, start, end, cash)
                    else:
                      title =  '%s<br />%s-%s' % (event.shift.name, start, end)
                    body.append('<span class="shift" rel="tooltip" data-html="true" title="' + title + '">' + event.shift.initials + '</span>')
#                    body.append('</a>')
                    body.append('</li>')
                body.append('</ul>')
                return self.day_cell(cssclass, '%d %s' % (day, ''.join(body)))
            return self.day_cell(cssclass, day)
        return self.day_cell('noday', '&nbsp;')

    def formatmonth(self, year, month, **kw):
        self.year, self.month = year, month
        return super(UserCalendar, self).formatmonth(year, month, **kw)

    def formatmonthname(self, year, month, withyear=True):
        first = date(year, month, 1)
        next_first = first + relativedelta(months=+1)
        prev_first = first - relativedelta(months=+1)
        if withyear:
            s = '%s %s' % (calendar.month_name[month], year)
        else:
            s = '%s' % calendar.month_name[month]
        pf = '%s %s' % (prev_first.month, prev_first.year)
        nf = '%s %s' % (next_first.month, next_first.year)
        sf = '%s %s' % (month, year)
        return '<tr><th id="%s" class="new_month" onclick=""><<</th><th id="%s" class="this_month" colspan="5">%s</th>\
                <th id="%s" class="new_month" onclick="">>></th></tr>' % (pf, sf, s, nf)

    def group_by_day(self, shifts):
        field = lambda shift: shift.date.day
        return dict(
            [(day, list(items)) for day, items in groupby(shifts, field)]
        )

    def day_cell(self, cssclass, body):
        return '<td class="%s">%s</td>' % (cssclass, body)