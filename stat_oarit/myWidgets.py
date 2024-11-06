import tkinter as tk
from tkinter import ttk
from datetime import datetime
from tkinter import StringVar
from tkcalendar import Calendar, DateEntry
from datetime import datetime, timedelta, time, date
from ttkwidgets.autocomplete import AutocompleteCombobox
import locale
import calendar
from collections import namedtuple, defaultdict
from collections import Counter
from pprint import pprint




#locale.setlocale(locale.LC_ALL, "Russian_Russia.1251")

class ValidatedMixin:
    """Adds a validation functionality to an input widget"""
    def __init__(self,  *args, error_var=None, **kwargs):
        self.error = error_var or tk.StringVar()
        super().__init__(*args, **kwargs)

        vcmd = self.register(self._validate)
        invcmd = self.register(self._invalid)

        self.configure(
          validate='all',
          validatecommand=(vcmd, '%P', '%s', '%S', '%V', '%i', '%d'),
          invalidcommand=(invcmd, '%P', '%s', '%S', '%V', '%i', '%d')
        )

    def _toggle_error(self, on=False):
        self.configure(foreground=('red' if on else 'black'))

    def _validate(self, proposed, current, char, event, index, action):
        """The validation method.

        Don't override this, override _key_validate, and _focus_validate
        """
        self.error.set('')
        self._toggle_error()

        valid = True
        # if the widget is disabled, don't validate
        state = str(self.configure('state')[-1])
        if state == tk.DISABLED:
          return valid

        if event == 'focusout':
          valid = self._focusout_validate(event=event)
        elif event == 'key':
          valid = self._key_validate(
          proposed=proposed,
          current=current,
          char=char,
          event=event,
          index=index,
          action=action
        )
        return valid

    def _focusout_validate(self, **kwargs):
        return True

    def _key_validate(self, **kwargs):
        return True

    def _invalid(self, proposed, current, char, event, index, action):
        if event == 'focusout':
            self._focusout_invalid(event=event)
        elif event == 'key':
            self._key_invalid(
                proposed=proposed,
                current=current,
                char=char,
                event=event,
                index=index,
                action=action
              )

    def _focusout_invalid(self, **kwargs):
        """Handle invalid data on a focus event"""
        self._toggle_error(True)

    def _key_invalid(self, **kwargs):
        """Handle invalid data on a key event.  By default we want to do nothing"""
        pass

    def trigger_focusout_validation(self):
        valid = self._validate('', '', '', 'focusout', '', '')
        if not valid:
            self._focusout_invalid(event='focusout')
        return valid

class MyEntryFIO(ValidatedMixin, ttk.Entry):
    ''' Ввод ФИО пациента '''  
    def __init__(self,  *args, textvariable, disable_var=None, **kw):
        super().__init__(*args, textvariable=textvariable, disable_var=None, **kw)
        self.textvariable = textvariable
        self.disable_var = disable_var

    def _focusout_validate(self, **kwargs):
        valid = True
        if not self.get():
            self.error.set('Empty fields')
            valid = False
        return valid

    def _key_validate(self, proposed, current, char, index, action, **kwargs):
        valid = True
        if action == '0':
            valid = True

        if str.isalpha(char) or char in ' .' :
            valid = True
        else:
            valid = False
        return valid




class MyEntryInteger(ValidatedMixin, ttk.Entry):
    ''' Ввод только чисел '''  
    def __init__(self,   *args, dig_num = None, disable_var=None, **kw):
        super().__init__(*args, dig_num = None, disable_var=None,  **kw)
        self.dig_num = dig_num
        self.disable_var = disable_var
        

    def _focusout_validate(self, **kwargs):
        valid = True
        if not self.get():
            self.error.set('Empty fields')
            valid = False
        return valid

    def _key_validate(self, proposed, current, char, index, action, **kwargs):
        valid = True
        if action == '0':
            valid = True

        if str.isdigit(char) and len(proposed) <= self.dig_num:
            valid = True
        else:
            valid = False
        if proposed == '0':
            valid = False
        return valid
    

class MyDateEntry(DateEntry):
    ''' Установка даты с помощью клавиш <Up> <Down>'''  
    def __init__(self, master, textvariable, *args, **kw):
        self.textvariable = textvariable
        DateEntry.__init__(self, master,textvariable = textvariable, *args, **kw)
        # add label displaying today's date below
        tk.Label(self._top_cal,  bg='light blue', anchor='w',
            text='Сегодня: %s'
                 % Calendar.date.today().strftime("%d.%B.%Y")).pack(fill='x')

        super().bind('<Up>', self._next_day)
        super().bind('<Down>', self._prev_day)
        super().bind('<<MouseWheel>>', self._mouse_wheel)

    def _next_day(self, event):
        self.set_date(self.get_date() + timedelta(days = 1))
    
    def _prev_day(self, event):
        self.set_date(self.get_date() - timedelta(days = 1))

    def _mouse_wheel(self, event):
        if event.delta ==  -120:
            self._prev_day(event)
        if event.delta ==  120:
            self._next_day(event)


class MyTimeEntry(ValidatedMixin, ttk.Combobox):
    "Ввод времени с валидацией"
    def __init__(self,  *args, disable_var=None, values = None, **kw):
        super().__init__(*args, values = values, **kw)
        self.values_time = values

        self.set('10:00')
        
    def _key_validate(self, proposed, current, index, action, char, **kwargs):
        valid = True
        if action == '0':
            self.set('')
            return True

        # Do a case-insensitive match against the entered text
        matching = [
            x for x in self.values_time
            if x.lower().startswith(proposed.lower())
        ]

        if len(matching) == 0:
            valid = False
        elif len(matching) == 1:
            self.set(matching[0])
            self.icursor(tk.END)
            valid = False

        elif len(matching) == 2:
            self.set(matching[0][:3])
            self.icursor(tk.END)
            valid = False

        return valid

    def _focusout_validate(self, **kwargs):
        valid = True
        if not self.get():
            self.error.set('Empty fields')
            valid = False
        return valid


class MyAutocompleteCombobox(ValidatedMixin, ttk.Combobox):
    def __init__(self, master, values=None, *args,
                 disable_var=None,  text_w =None, **kw):
        super().__init__(master,  *args, **kw)
        if values is None:
            self.values = []
        else:
            self.values = values
        self.text_w = text_w
        self.disable_var = disable_var
        if self.disable_var is False:
            self.configure(state = 'readonly')
        self.set_completion_list(self.values)
        
    def set_completion_list(self, completion_list):
        """
        Use the completion list as drop down selection menu, arrows move through menu.
        
        :param completion_list: completion values
        :type completion_list: list
        """
        completion_list_filtred = [
            el for el in completion_list if el is not None]
        self._completion_list = sorted(completion_list_filtred, key=str.lower)  # Work with a sorted list
        self['values'] = self._completion_list  # Setup our popup menu

    def _key_validate(self, proposed, current, index, event, action, char, **kwargs):    
        
        valid = True
        
        if action == '0':
            self.delete(index, tk.END)
            return True

        matching = [
            x for x in self._completion_list
            if x.lower().startswith(proposed.lower())
        ]
        if matching:
            self.delete(0, tk.END)
            self.insert(0, matching[0])
            self.select_range(str(int(index)+1), tk.END)
        else:
            return True
        return valid


class MyCalendar(Calendar):
    """Установка дней дежурств""";

    def __init__(self, master,  *args, **kw):
        super().__init__(master, *args, **kw)
        self.master = master
        super().bind("<<CalendarSelected>>", self.date_entry_selected)
        super().bind("<<CalendarMonthChanged>>", self.month_selected)
        self.tag_config('morning',background='light green',foreground='yellow')
        self.tag_config('day_R',background='light blue',foreground='yellow')
        self.tag_config('day_A',background='red',foreground='yellow')
        self.DCT_MONTH = {('day_'+str(c)) : '' for c in range(1,32)}
        self.DCT_MONTH['work_hour']=''
        self.SCHEDULE_HEADERS = ['fio', 'month', 'year', *self.DCT_MONTH]
        self.FIO_SCHEDULE = namedtuple('fio_schedule', self.SCHEDULE_HEADERS,
                          defaults=('',)*len(self.DCT_MONTH))
        self.mindate_primary = Calendar.date(year=2024, month=1, day=1)
        self.crt_schedule = False
        self.work_schedule = {}

    def month_selected(self, event):
        self.event_generate('<<MonthSelected>>')
    
    def format_dt_keys(self, m_y):
        (d_month, d_year)=m_y
        _, last_day = calendar.monthrange(d_year, d_month)
        lst_fdk = []
        for day in range(1, last_day+1):
            bgn_work_day = datetime(d_year, d_month, day, hour=8)
            end_work_day = bgn_work_day + timedelta(hours=24)
            lst_fdk.append((bgn_work_day, end_work_day))
        return lst_fdk

    @property
    def get_schedule_all_days(self):
        return self.work_schedule
    @get_schedule_all_days.setter
    def get_schedule_all_days(self, schedule):
        days_of_month = defaultdict(list)
        month_year = list(set((int(dct['month']),int(dct['year']))
                              for dct in schedule))
        dct_sch_all = {}
        for m_y in month_year:
            lst = self.format_dt_keys(m_y)
            for dct in schedule:
                if (int(dct['month']),int(dct['year']))== m_y:
                    lst_schd = [(dct['fio'],dct[k]) for k in dct.keys()][3:34]
                    for d, key in enumerate(lst):
                        if lst_schd[d][1] !='':
                            days_of_month[key].append(lst_schd[d])
                        else:
                            days_of_month[key]


            dct_sch_all.update(days_of_month)
        self.work_schedule = dct_sch_all
        

    def date_entry_selected(self, event):
        w = event.widget
        date = w.selection_get()
        try:
            if self.get_calevents(date=date, tag='morning'):
                self.calevent_remove(date=date)
                self.calevent_create(date, 'Сутки реанимация','day_R')
            elif self.get_calevents(date=date, tag='day_R'):
                self.calevent_remove(date=date)
                self.calevent_create(date, 'Сутки анестезиология','day_A')
            elif self.get_calevents(date=date, tag='day_A'):
                self.calevent_remove(date=date)
            else:
                self.calevent_create(date, 'День','morning')

        except Exception as e:
            pass

    def reset_schedule(self):
        self.calevent_remove('all')
        mindate = self.mindate_primary
        self.configure(selectmode='none', cursor='hand1',
                       mindate=mindate, maxdate=None)
        self.crt_schedule = False


    def create_schedule(self):
        self.calevent_remove('all')
        (d_month, d_year)=self.get_displayed_month()
        _, last_day = calendar.monthrange(d_year, d_month)
        mindate = Calendar.date(year=d_year, month=d_month, day=1)
        maxdate = Calendar.date(year=d_year, month=d_month, day=last_day)
        if self.crt_schedule:
            self.reset_schedule()
        else:
            self.configure(selectmode='day', cursor='hand1',
                       mindate=mindate, maxdate=maxdate)
            self.crt_schedule = True

    def read_schedule(self, fio):
        month, year = self.get_displayed_month()
        gc = self.get_calevents()
        for count, value in enumerate(self.DCT_MONTH, start=1):
            for i in gc:
                d = self.calevent_cget(i, 'date').day
                t = self.calevent_cget(i, 'text')
                if count==d:
                    self.DCT_MONTH[value]=t
        f_s = self.FIO_SCHEDULE(fio, str(month), str(year), *self.DCT_MONTH.values())
        for k in self.DCT_MONTH:
            self.DCT_MONTH[k]=''
        return f_s


    def write_schedule(self, fio):
        self.calevent_remove('all')
        month, year = self.get_displayed_month()
        for row in self.SCHEDULE:
            if fio ==row['fio'] and (str(month)==row['month'] and str(year)==row['year']):
                for d, value in enumerate(row, start = -2):
                    if row[value]=='День':
                        date_ev=datetime(year, month, d)
                        self.calevent_create(date_ev,
                                             'День','morning')
                    elif row[value]=='Сутки реанимация':
                        date_ev=datetime(year, month, d)
                        self.calevent_create(date_ev,
                                             'Сутки реанимация','day_R')
                    elif row[value]=='Сутки анестезиология':
                        date_ev=datetime(year, month, d)
                        self.calevent_create(date_ev,
                                             'Сутки анестезиология','day_A')
            else:
                pass
                        
class Doctor(object):

    def __init__(self, name, schedule_doct,
                 anest_work_doct, rean_work_doct, deaths=None):
        self.name = name
        self.schedule_doct = schedule_doct
        self.anest_work_doct = anest_work_doct
        self.rean_work_doct = rean_work_doct
        self.deaths = deaths

    def night_job(self):

        time_night_s = time(22, 0, 0,0)
        time_night_e = time(6, 0, 0, 0)

        night_rean = []
        night_anest = 0

        for i in self._anest_work_doct:
            if (time_night_s <= i[1].time() or
                    time_night_e > i[1].time()):
                night_anest += 1
        for i in self._rean_work_doct:
            if (time_night_s <= i[1].time() or
                    time_night_e > i[1].time()):
                night_rean.append(i)
        return night_anest, night_rean

    def total_anest(self):
        lst_of_pair = [(x[0],x[2]) for x in self._anest_work_doct]
        cnt = Counter(lst_of_pair)
        return cnt

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def schedule_doct(self):
        return self._schedule_doct

    @schedule_doct.setter
    def schedule_doct(self, value):
        self._schedule_doct = value

    @property
    def anest_work_doct(self):
        return self._anest_work_doct

    @anest_work_doct.setter
    def anest_work_doct(self, value):
        self._anest_work_doct = value

    @property
    def rean_work_doct(self):
        return self._rean_work_doct

    @rean_work_doct.setter
    def rean_work_doct(self, value):
        self._rean_work_doct = value

    @property
    def deaths(self):
        return self._deaths

    @deaths.setter
    def deaths(self, value):
        self._deaths = value

