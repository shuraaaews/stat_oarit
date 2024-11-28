"""The view stat_oarit"""

import os
import sys
import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
from tkinter import messagebox
from tkinter import filedialog
from tkinter import Menu
from tkcalendar import Calendar, DateEntry
import locale
from collections import namedtuple, defaultdict
from collections import Counter
import csv
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import matplotlib.dates
from . import images





from . import myWidgets as w
from ttkwidgets.autocomplete import AutocompleteCombobox


REAN_HEAD = ['#0', '№', 'Ф.И.О. больного', 'Возраст', 'Дата поступления',
             'Длительность', 'Диагноз при поступлении', 'Перевод', 'Смерть', 'Реаниматолог']
ANEST_HEAD = ['#0', '№', 'Ф.И.О. больного', 'Возраст', 'Дата поступления',
              'Отделение', 'Операция', 'Анестезиолог', 'Вр_опер']
COMMON_HEAD = ['#0', '№', 'Профиль', 'Ф.И.О. больного', 'Возраст',
               'Дата поступления', 'Длительность', 'Диагноз при поступлении',
               'Отделение', 'Перевод', 'Смерть', 'Операция', 'Реаниматолог',
               'Анестезиолог', 'Вр_опер']

DCT_MONTH = {('day_'+str(c)) : '' for c in range(1,32)}
DCT_MONTH['work_hour']=''
SCHEDULE_HEADERS = ['fio', 'month', 'year', *DCT_MONTH]
FIO_SCHEDULE = namedtuple('fio_schedule', SCHEDULE_HEADERS,
                          defaults=('',)*len(DCT_MONTH))
SCHEDULE=[]

class ToolBar(tk.Frame):
    
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.text_info_1 = tk.StringVar()
        self.text_info_2 = tk.StringVar()
        self.text_info_5 = tk.StringVar()
        self.text_info_6 = tk.StringVar()
        
        self.text_info_1.set('0')
        self.text_info_2.set('0')
        self.text_info_5.set('')
        self.text_info_6.set('')

        self.master = master
        self.create_info_bar()

    def _item_select(self):
        self.infobar_frame.event_generate('<<ToolButton>>')

    def create_info_bar(self):
        self.infobar_frame = ttk.Frame(self.master, relief = 'sunken', height=55)
        self.infobar_frame.grid(row=0, column=0, sticky=('W,E'))

        self.toolbar_images = []
        self.value_item = tk.StringVar(value='GrafForm')
        for image, value in (
            (images.IDCARD, 'DataRecordForm'),
            (images.MEDICALFOLD, 'DataListForm'),
            (images.SYMPTOM, 'CalendarForm'),
            (images.DOCTOR, 'GrafForm')):
            image = os.path.join(os.path.dirname(__file__), image)
            try:
                image = tk.PhotoImage(file=image)
                self.toolbar_images.append(image)
                button = ttk.Radiobutton(self.infobar_frame, style= 'main1.Toolbutton',
                                       image=image, command=self._item_select, value=value,
                                        variable=self.value_item, compound='image',)
                button.grid(row=0, rowspan=2, padx=10, ipadx = 10, pady=10,
                            sticky=("W,E,N,S"), column=len(self.toolbar_images) - 1)
            except tk.TclError as err:
                pass

        ttk.Label(self.infobar_frame,
                  text='Все записи: ', font=("Arial", 12)).grid(
            row=0, column=7, padx=10, pady=10, sticky=('W'))
        ttk.Label(self.infobar_frame,
                  textvariable = self.text_info_1, width = 7, anchor = 'e', font=("Arial", 12)).grid(
            row=0, column=8, padx=10, pady=10)

        ttk.Label(self.infobar_frame,
                  text='Добавлено запись: ', font=("Arial", 12)).grid(
            row=1, column=7, padx=10, pady=10, sticky=('W'))
        ttk.Label(self.infobar_frame,
                  textvariable = self.text_info_2, width = 7, anchor = 'e', font=("Arial", 12)).grid(
            row=1, column=8,  padx=10, pady=10, sticky=('E'))


        ttk.Label(self.infobar_frame,
                  text='Файл:', font=("Arial", 12)).grid(
            row=0, column= 10, padx=10, pady=10, sticky=('W'))
        ttk.Label(self.infobar_frame,
                  textvariable = self.text_info_5, width = 22, anchor = 'e',font=("Arial", 12)).grid(
            row=0, column=11, padx=5, pady=10, sticky=('E'))

        ttk.Label(self.infobar_frame,
                  text='Ближайший день рождения: ', font=("Arial", 12)).grid(
            row=0, column= 13, padx=10, pady=10, sticky=('W'))
        ttk.Label(self.infobar_frame,
                  textvariable = self.text_info_6, foreground='red', font=("Arial", 12)).grid(
            row=1, column=13, padx=5, pady=10, sticky=('W'))


        self.separator_info1 = ttk.Separator(self.infobar_frame, orient = "vertical")
        self.separator_info2 = ttk.Separator(self.infobar_frame, orient = "vertical")
        self.separator_info3 = ttk.Separator(self.infobar_frame, orient = "vertical")        

        self.separator_info1.grid(row=0, rowspan=3, column=6, pady=5, sticky=("S, N"))
        self.separator_info2.grid(row=0, rowspan=3, column=9, pady=5, sticky=("S, N"))
        self.separator_info3.grid(row=0, rowspan=3, column=12, pady=5, sticky=("S, N"))







class StatusBar(tk.Frame):

    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.master = master
        self.status_message = tk.StringVar()
        self.frame_message_bar = ttk.Frame(self.master, relief = 'sunken')
        self.frame_message_bar.grid(sticky=("E, W, S"), row=2, column=0, columnspan=2)
        self.frame_message_bar.columnconfigure(0, weight = 1)
        self.frame_message_bar.rowconfigure(2, weight = 0)
        self.frame_message_bar.columnconfigure(1, weight = 1)

        self.statusbar = ttk.Label(self.frame_message_bar,
                        textvariable = self.status_message)
        self.statusbar.grid(sticky=("W,E"), row=0, column=0, padx = 10, pady=5)

        sgp = ttk.Sizegrip(self.frame_message_bar)
        sgp.grid(sticky=("ES"), row=0, column=1)
    
    
    def clearStatusBar(self):
        self.status_message.set('')

    def setStatusBar(self, textstatus, timeout = 5000):
        if textstatus.startswith('Ошибка'):
            self.statusbar.config(foreground='red')
        else:
            self.statusbar.config(foreground='black')
        self.status_message.set(textstatus)
        if timeout:
            self.statusbar.after(timeout, self.clearStatusBar) 

    @property
    def status_text(self):
        return self._status_text
    @status_text.setter
    def status_text(self, text):
        self._status_text = text

class CalendarForm(tk.Frame):
    """The input form for our widgets"""
    

    def __init__(self, master, filename, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.master = master
        self.filename_schd, self.filename_empl = filename
        self.master.grid(row=1, column=0, sticky=("W, E, N, S"))

        self.text_FIO = tk.StringVar()

        self.calendar_frame = ttk.Frame(self, relief = 'sunken')
        self.calendar_frame.grid(row=0, column=0, sticky=("W, E, N, S"))

        self.calendar_frame.columnconfigure(0, weight = 1)
        self.calendar_frame.rowconfigure(1, weight = 1)
        self.calendar_frame_info = ttk.Frame(self.calendar_frame, relief = 'sunken')
        self.calendar_frame_info.grid(row=0, column=0, sticky=("W, E, N, S"))

        self.calendar_frame_cal = ttk.Frame(self.calendar_frame, relief = 'sunken')
        self.calendar_frame_cal.grid(row=1, column=0, sticky=("W, E, N, S"))



        self._vars_dl_profil = {
            'Реанимация' : tk.StringVar(),
            'Анестезиология' : tk.StringVar() }
        self._vars_dl_profil['Реанимация'].set('1')
        self._vars_dl_profil['Анестезиология'].set('1')
        self._vars_find_date = tk.StringVar()
        
        self.text_FIO = tk.StringVar()
        self.sum_hour = tk.StringVar()
        self.sum_day = tk.StringVar()
        self.sum_stavka = tk.StringVar()
        self.sum_hour.set('')
        self.sum_day.set('')
        self.sum_stavka.set('')
        self._vars_anest = tk.StringVar()
        self._vars_twork = tk.StringVar()
        EMPLOYEES_HEADERS = ['famili', 'first_name', 'last_name',
          'phone', 'status', 'birthday', 'famili_IO']

        with open(self.filename_empl, 'r', encoding='cp1251', newline='') as f:
            f_s = csv.DictReader(f,EMPLOYEES_HEADERS)
            empl = list(dct['famili_IO'] for dct in f_s if dct['status']=='Врач')


        image = os.path.join(os.path.dirname(__file__), images.MAGNIFER)
        self.find_FIO_image = tk.PhotoImage(file=image)

        mindate = Calendar.date(year=2024, month=1, day=1)

        self.cal = w.MyCalendar(self.calendar_frame_cal, state='normal',selectmode='none', font="Arial 14",
                 style="my.Calendar", locale='ru_RU',
                   mindate=mindate, borderwidth=20, disabledforeground='red',showothermonthdays=False,
                   cursor="arrow")

        
        ttk.Button(self.calendar_frame_info, text="График... иницилизация",
                   command=self.cal.create_schedule, style= 'main2.Toolbutton').grid(
            row=0, column=0, sticky=("W"), padx=10, pady=10)


        ttk.Button(self.calendar_frame_info, text="График... сохранить",
           command=self.read_toggle, style= 'main2.Toolbutton').grid(
            row=1, column=0, sticky=("W"), padx=10, pady=10)

        self.separator_dl1 = ttk.Separator(self.calendar_frame_info, orient = "vertical")
        self.separator_dl1.grid(row=0, rowspan=2, column=5, pady=5, sticky=("S, N"))


        ttk.Label(self.calendar_frame_info, text = "ФИО Врача: ", font=("Arial", 12)).grid(
            row=0, column=6, sticky=("E"), padx=10, pady=10)

        w.MyAutocompleteCombobox(
          self.calendar_frame_info, textvariable=self._vars_anest,
            values = empl, 
          ).grid(row=1, column=6, padx=20, pady=(0, 10), sticky=(tk.W + tk.E))

        ttk.Button(
          self.calendar_frame_info, text = "Просмотр", image = self.find_FIO_image, compound = tk.LEFT,
          style= 'main2.Toolbutton', command=self.write_toggle).grid(
              row=1, column=7, padx=20, pady=(0, 10),sticky=(tk.W + tk.E))

        self.separator_dl2 = ttk.Separator(self.calendar_frame_info, orient = "vertical")
        self.separator_dl2.grid(row=0, rowspan=2, column=8, pady=5, sticky=("S, N"))


        self.separator_dl2 = ttk.Separator(self.calendar_frame_info, orient = "vertical")
        self.separator_dl2.grid(row=0, rowspan=2, column=8, pady=5, sticky=("S, N"))

        ttk.Label(self.calendar_frame_info, text='Рабочее время', font=("Arial", 12)).grid(row=0, column=9, columnspan=2,
                                                            padx=15, sticky=(tk.W + tk.E))

        w.MyEntryInteger(
            self.calendar_frame_info, width=5, dig_num=3, font=("Arial", 12), textvariable=self._vars_twork
        ).grid(row=1, column=9, columnspan=2, padx=15, pady=(0, 10), sticky=(tk.W))

        

        ttk.Button(
          self.calendar_frame_info, text = "Сохранить", 
          style= 'main2.Toolbutton', command=self.write_work_hour).grid(
              row=1, column=11, padx=10, pady=(0, 10),sticky=(tk.W))



        self.separator_dl3 = ttk.Separator(self.calendar_frame_info, orient = "vertical")
        self.separator_dl3.grid(row=0, rowspan=2, column=14, pady=5, sticky=("S, N"))
        text_day = "08:00 - 16:00"
        text_sutki = "08:00 - 08:00"
        ttk.Label(self.calendar_frame_cal, text = f'День{text_day:>46}',
                  background='light green', foreground='black',font=("Arial", 12)).grid(
            row=0, column=0, padx=55, pady=5,sticky=(tk.W))
        ttk.Label(self.calendar_frame_cal, text = f'Сутки реанимация{text_sutki:>21}',
                  background='light blue', foreground='black',font=("Arial", 12)).grid(
            row=1, column=0, padx=55, pady=5,sticky=(tk.W))
        ttk.Label(self.calendar_frame_cal, text = f'Сутки анестезиология{text_sutki:>15}',
                  background='red', foreground='black',font=("Arial", 12)).grid(
            row=2, column=0, padx=55, pady=5,sticky=(tk.W))

        ttk.Label(self.calendar_frame_cal, text = f'Общее количество часов: ',
                  foreground='black',font=("Arial", 14)).grid(
            row=0, column=3, padx=55, pady=5,sticky=(tk.W))
        ttk.Label(self.calendar_frame_cal, textvariable=self.sum_hour,
                  foreground='black',font=("Arial", 14)).grid(
            row=0, column=4, padx=55, pady=5,sticky=(tk.E))

        ttk.Label(self.calendar_frame_cal, text = f'Общее количество суток: ',
                  foreground='black',font=("Arial", 14)).grid(
            row=1, column=3, padx=55, pady=5,sticky=(tk.W))

        ttk.Label(self.calendar_frame_cal, textvariable=self.sum_day,
                  foreground='black',font=("Arial", 14)).grid(
            row=1, column=4, padx=55, pady=5,sticky=(tk.E))


        ttk.Label(self.calendar_frame_cal, text = f'Время по ставкам: ',
                  foreground='black',font=("Arial", 14)).grid(
            row=2, column=3, padx=55, pady=5,sticky=(tk.W))

        ttk.Label(self.calendar_frame_cal, textvariable=self.sum_stavka,
                  foreground='black',font=("Arial", 14)).grid(
            row=2, column=4, padx=55, pady=5,sticky=(tk.E))



        self.cal.grid(row=3, column=0, padx=55, pady=5,sticky=(tk.W))

        with open(self.filename_schd, 'r', encoding='cp1251', newline='') as f:
            f_s = csv.DictReader(f, SCHEDULE_HEADERS)
            head =next(f_s)
            SCHEDULE = list(f_s)

        self.cal.SCHEDULE = SCHEDULE
        self.SCHEDULE = SCHEDULE
        self.month_year = list((int(dct['month']),int(dct['year'])) for dct in self.SCHEDULE)
        self.dct_work_hour = {}
        for row in self.SCHEDULE:
            if row['work_hour'] !='':
                self.dct_work_hour[(int(row['month']),int(row['year']))] = row['work_hour']
        self.WORK_SCHEDULE = {}
        

        self.cal.bind('<<MonthSelected>>', self.work_hour_view)
        self.work_hour_view()
        self.set_schedule_all_days()
        
    def work_hour_view(self, *_):
        h =self.cal.get_displayed_month()
        if h in self.dct_work_hour:
            self._vars_twork.set(self.dct_work_hour[h])
        else:
            self._vars_twork.set('')

    def write_work_hour(self):
        if self._vars_twork.get():
            work_h = self._vars_twork.get()
        else:
            return False
            
        display_m_y = self.cal.get_displayed_month()
        if display_m_y not in self.dct_work_hour:
            self.dct_work_hour[display_m_y] = work_h
        else:
            result = messagebox.askyesno(
            title='Внимание !',
            message='Рабочее время на этот месяц уже есть !     \
                    Уверены, что хотите перезаписать данные ?')
            if result:
                self.dct_work_hour[display_m_y] = work_h
            else:
                return
        new_sch_lst = []            
        for row in self.SCHEDULE:
            tpl = (int(row['month']),int(row['year']))
            if tpl in self.dct_work_hour:
                row['work_hour'] = self.dct_work_hour[tpl]
            new_sch_lst.append(row)
        with open(self.filename_schd, 'w', encoding='cp1251', newline='') as f:
            writer = csv.DictWriter(f, SCHEDULE_HEADERS)
            writer.writeheader()
            writer.writerows(new_sch_lst)
            self.SCHEDULE.clear()
            self.SCHEDULE.extend(new_sch_lst)


    def read_toggle(self):
        if not self.cal.crt_schedule:
            return False
        if self._vars_anest.get():
            s = self.cal.read_schedule(self._vars_anest.get())
        else:
            messagebox.showerror('Warning !!!','Не выбран доктор !!!')
            return False
            
        flag = False
        new_sch_lst = []
        for row in self.SCHEDULE:
            if (s.fio ==row['fio'] and (s.month==row['month'] and s.year==row['year'])):
                result = messagebox.askyesno(
                title='Внимание !',
                message='График на этот месяц у данного врача есть !\
                        Вы уверены, что хотите перезаписать данные ?')
                if result:
                    new_sch_lst.append(s._asdict())
                    flag = True
                else:
                    return
            else:
                new_sch_lst.append(row)
        if flag:
            with open(self.filename_schd, 'w', encoding='cp1251', newline='') as f:
                writer = csv.DictWriter(f, SCHEDULE_HEADERS)
                writer.writeheader()
                writer.writerows(new_sch_lst)
                self.SCHEDULE.clear()
                self.SCHEDULE.extend(new_sch_lst)
        else:    
            with open(self.filename_schd, 'a', encoding='cp1251', newline='') as f:
                writer = csv.DictWriter(f, SCHEDULE_HEADERS)
                writer.writerow(s._asdict())
                self.SCHEDULE.append(s._asdict())

        self.cal.reset_schedule()

    def show_work_time(self):
        month, year = self.cal.get_displayed_month()
        s = self.SCHEDULE
        fio = self._vars_anest.get()
        s_h = 0
        s_d = 0
        for row in s:
            if fio ==row['fio'] and (str(month)==row['month'] and str(year)==row['year']):
                for d, value in enumerate(row, start = -2):
                    if row[value]=='День':
                        s_h += 8
                    elif row[value]=='Сутки реанимация':
                        s_h += 24
                        s_d +=1
                    elif row[value]=='Сутки анестезиология':
                        s_h += 24
                        s_d += 1
        self.sum_hour.set(str(s_h))
        self.sum_day.set(str(s_d))
        if self._vars_twork.get() !='':
            s_s = s_h/int(self._vars_twork.get())
            self.sum_stavka.set('%.1f' % s_s)

    def write_toggle(self):
        self.show_work_time()
        self.cal.write_schedule(self._vars_anest.get())

    def set_schedule_all_days(self):
        self.cal.get_schedule_all_days =self.SCHEDULE
    def get_schedule_all_days(self):
        s = self.cal.get_schedule_all_days
        return s


class GrafForm(tk.Frame):

    def __init__(self, master, model, filename, lst_data_common, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.master = master
        self.model = model
        self.filename_schd, self.filename_empl = filename
        self.lst_data_common = lst_data_common
        self.master.grid(row=1, column=0, sticky=("W, E, N, S"))
        self.graf_frame = ttk.Frame(self, relief = 'sunken')
        self.graf_frame.grid(row=0, column=0, sticky=("W, E, N, S"))

        self.graf_frame.columnconfigure(0, weight = 1)
        self.graf_frame.rowconfigure(1, weight = 1)
        self.graf_frame_info = ttk.Frame(self.graf_frame, relief = 'sunken')
        self.graf_frame_info.grid(row=0, column=0, sticky=("W, E, N, S"))

        self._vars_profil = tk.StringVar()
        self._vars_profil.set('Реанимация')

        self._vars_anest = tk.StringVar()
        self._var_otd = tk.StringVar()
        self.otd_l = []
        
        self.text_string_1 = tk.StringVar()
        self.text_string_2 = tk.StringVar()
        self.text_string_3 = tk.StringVar()
        self.text_string_4 = tk.StringVar()
        self.text_string_5 = tk.StringVar()
        self.text_string_6 = tk.StringVar()


        self.text_data_1 = tk.StringVar()
        self.text_data_2 = tk.StringVar()
        self.text_data_3 = tk.StringVar()
        self.text_data_4 = tk.StringVar()
        self.text_data_5 = tk.StringVar()
        self.text_data_6 = tk.StringVar()

        EMPLOYEES_HEADERS = ['famili', 'first_name', 'last_name',
          'phone', 'status', 'birthday', 'famili_IO']


        with open(self.filename_empl, 'r', encoding='cp1251', newline='') as f:
            f_s = csv.DictReader(f,EMPLOYEES_HEADERS)
            self.empl = list(dct['famili_IO'] for dct in f_s if dct['status']=='Врач')


        rb1 = ttk.Radiobutton(
            self.graf_frame_info, variable=self._vars_profil,
            value = 'Реанимация', text=f'Реанимация:         ', style= 'main2.Toolbutton',
            command = self.toggle_rean)
        rb1.grid(
            row=0, column=0, sticky=("W"), padx=10, pady=10)

        rb2 = ttk.Radiobutton(
            self.graf_frame_info, variable=self._vars_profil,
            value = 'Анестезиология', text=f'Анестезиология: ', style= 'main2.Toolbutton',
            command = self.toggle_anest)
        rb2.grid(
            row=1, column=0, sticky=("W"), padx=10, pady=10)


        self.separator_dl1 = ttk.Separator(self.graf_frame_info, orient = "vertical")
        self.separator_dl1.grid(row=0, rowspan=2, column=5, pady=5, sticky=("S, N"))


        ttk.Label(self.graf_frame_info, text = "Поиск по ФИО: ", font=("Arial", 12)).grid(
            row=0, column=6, sticky=("E"), padx=10, pady=10)

        self.anest_lst  = w.MyAutocompleteCombobox(
          self.graf_frame_info, textvariable=self._vars_anest,
            values = self.empl, 
          ).grid(row=1, column=6, padx=20, pady=(0, 10), sticky=(tk.W + tk.E))

        self.separator_dl2 = ttk.Separator(self.graf_frame_info, orient = "vertical")
        self.separator_dl2.grid(row=0, rowspan=2, column=8, pady=5, sticky=("S, N"))

        ttk.Label(self.graf_frame_info, text = "Отделение: ", font=("Arial", 12)).grid(
            row=0, column=10, sticky=("E"), padx=10, pady=10)

        self.otd_lst = w.MyAutocompleteCombobox(
          self.graf_frame_info, textvariable=self._var_otd,
            values = self.otd_l)
        self.otd_lst.grid(row=1, column=10, padx=20, pady=(0, 10), sticky=(tk.W + tk.E))


        self.separator_dl3 = ttk.Separator(self.graf_frame_info, orient = "vertical")
        self.separator_dl3.grid(row=0, rowspan=2, column=12, pady=5, sticky=("S, N"))


        self.graf_frame_view = ttk.Frame(self.graf_frame, relief = 'sunken')
        self.graf_frame_view.grid(row=1, column=0, sticky=("W, E, N, S"))

        self.graf_frame_data = ttk.Frame(self.graf_frame_view, relief = 'sunken')
        self.graf_frame_data.grid(row=0, column=0, sticky=("W, E, N, S"))

        self.graf_frame_data.columnconfigure(0, weight = 0)
        self.graf_frame_data.rowconfigure(0, weight = 0)

        self.graf_frame_graf = ttk.Frame(self.graf_frame_view, relief = 'sunken')
        self.graf_frame_graf.grid(row=0, column=1, sticky=("W, E, N, S"))


        self.figure = Figure(figsize=(7, 4.2), dpi=100)

        self.ax = self.figure.add_subplot(1,1,1)

        self.start_date = datetime(2024,1,1).date()
        self.now_date = datetime.now().date()

        self.ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%d.%m.%Y"))
        locator = matplotlib.dates.MonthLocator()
        locator_d = matplotlib.dates.DayLocator()
        self.ax.tick_params(axis='x', labelrotation=15, labelsize = 8)
        self.ax.xaxis.set_major_locator(locator)
        self.ax.xaxis.set_minor_locator(locator_d)
        formatter = matplotlib.ticker.FormatStrFormatter('%d')
        self.ax.yaxis.set_major_formatter(formatter)
        self.ax.set_xlim(self.start_date, self.now_date)
        self.ax.set_ylim(-7, 7)

        self.canvas_tkagg = FigureCanvasTkAgg(self.figure, master=self.graf_frame_view)
        self.canvas = self.canvas_tkagg.get_tk_widget()
        self.canvas.grid(row=0, column=1, sticky=("W, E, N, S"))

        self.m_toolbar = tk.Frame(master=self.graf_frame_view)
        self.m_toolbar.grid(row=20, column=1, sticky=("W, E"))
        self.m_toolbar = NavigationToolbar2Tk(self.canvas_tkagg, self.m_toolbar)        
    

        rb2.invoke()

        with open(self.filename_schd, 'r', encoding='cp1251', newline='') as f:
            f_s = csv.DictReader(f, SCHEDULE_HEADERS)
            head =next(f_s)
            self.SCHEDULE = list(f_s)
        x, y = self.model.current_model

    def toggle_rean(self):

        self.text_string_1.set("Общее количество принятых больных: ")
        self.text_string_2.set("Количество принятых больных в ночное время с 22:00 по 06:00 : ")
        self.text_string_3.set("Количество смертей на смене:  ")
        self.text_string_4.set("")
        self.text_string_5.set("")
        self.text_string_6.set("")

        self.text_data_1.set("")
        self.text_data_2.set("")
        self.text_data_3.set("")
        self.text_data_4.set("")
        self.text_data_5.set("")
        self.text_data_6.set("")

        r_w_d = 0
        n_j = 0
        death = 0

        pat_cnt_graf = defaultdict(list)
        nigth_graf = defaultdict(list)
        death_graf = defaultdict(list)


        
        for d in self.lst_data_common:
            if self._vars_anest.get():
                if d.name == self._vars_anest.get():
                    r_w_d = len(d.rean_work_doct)
                    n_j = len(d.night_job()[1])
                    death = len(d.deaths)
                    for i in d.rean_work_doct:
                        pat_cnt_graf[i[1].date()].append(i[0])
                    for i in d.night_job()[1]:
                        nigth_graf[i[1].date()].append(i[0])
                    for i in d.deaths:
                        death_graf[i.date()].append(1)
            else:
                r_w_d += len(d.rean_work_doct)
                n_j += len(d.night_job()[1])
                death += len(d.deaths)
                for i in d.rean_work_doct:
                    pat_cnt_graf[i[1].date()].append(i[0])
                for i in d.night_job()[1]:
                    nigth_graf[i[1].date()].append(i[0])
                for i in d.deaths:
                    death_graf[i.date()].append(1)



        if r_w_d:
            centil_death = round(death/r_w_d*100)
            common_death = str(death) + ' (' +str(centil_death) + '%)'
        else:
            common_death = 0

        self.text_data_1.set(r_w_d)
        self.text_data_2.set(n_j)
        self.text_data_3.set(common_death)

        self.update_text()
        self.plot_graf_rean(pat_cnt_graf, nigth_graf, death_graf)


    def toggle_anest(self):

        self.text_string_1.set("Общее количество анестезий: ")
        self.text_string_2.set("Количество анестезий в ночное время с 22:00 по 06:00 : ")
        self.text_string_3.set("")
        self.text_string_4.set("Плановые операции: ")
        self.text_string_5.set("Экстренные операции: ")
        self.text_string_6.set("Виды анестезиий: ")
        self.text_data_1.set("")
        self.text_data_2.set("")
        self.text_data_3.set("")
        self.text_data_4.set("")
        self.text_data_5.set("")
        self.text_data_6.set("")
        
        

        a_w_d = 0
        n_j = 0
        pl_an = 0
        ex_an = 0
        an_t_c = 0
        total_an = Counter()
        total_t_a_w_d =[]
        plan_graf = defaultdict(list)
        extr_graf = defaultdict(list)
        an_typ_cnt = Counter()


        for d in self.lst_data_common:
            if self._vars_anest.get():
                if d.name == self._vars_anest.get():
                    a_w_d = len(d.anest_work_doct)
                    n_j = d.night_job()[0]
                    t_a = d.total_anest().items()
                    plan_an = [(x[0][0], x[1]) for x in t_a if x[0][1] == 'план']
                    pl_an_extd = [(x[0], x[1].date()) for x in d.anest_work_doct
                                  if x[2] == 'план']
                    plan_an.sort(key=lambda x: x[1], reverse=True)
                    extr_an = [(x[0][0], x[1]) for x in t_a if x[0][1] == 'экстр']
                    ex_an_extd = [(x[0], x[1].date()) for x in d.anest_work_doct
                                  if x[2] == 'экстр']
                    extr_an.sort(key=lambda x: x[1], reverse=True)
    
                    for c in [x[3] for x in d.anest_work_doct]:
                        an_typ_cnt[c] += 1        

            else:
                a_w_d += len(d.anest_work_doct)
                n_j += d.night_job()[0]
                t_a = d.total_anest()
                total_an += t_a
                t_a_w_d  = d.anest_work_doct
                total_t_a_w_d += t_a_w_d
                for c in [x[3] for x in d.anest_work_doct]:
                    an_typ_cnt[c] += 1        

        if self._vars_anest.get():
            pl_an = "{}".format('\n'.join([x[0]+'    '+str(x[1]) for x in plan_an]))
            ex_an = "{}".format('\n'.join([x[0]+'    '+str(x[1]) for x in extr_an]))
            an_t_c = "{}".format('\n'.join([x[0]+'    '+str(x[1]) for x in an_typ_cnt.most_common()]))
            for x in pl_an_extd:
                plan_graf[x[0]].append(x[1])
            for x in ex_an_extd:
                extr_graf[x[0]].append(x[1])
        else:
            plan_an = [(x[0][0], x[1]) for x in total_an.items() if x[0][1] == 'план']
            extr_an = [(x[0][0], x[1]) for x in total_an.items() if x[0][1] == 'экстр']
            plan_an.sort(key=lambda x: x[1], reverse=True)
            extr_an.sort(key=lambda x: x[1], reverse=True)
            pl_an = "\n{}".format('\n'.join([x[0]+'    '+str(x[1]) for x in plan_an]))
            ex_an = "\n{}".format('\n'.join([x[0]+'    '+str(x[1]) for x in extr_an]))
            an_t_c = "\n{}".format('\n'.join([x[0]+'    '+str(x[1]) for x in an_typ_cnt.most_common()]))
            for x in total_t_a_w_d:
                if x[2] == 'план':
                    plan_graf[x[0]].append(x[1].date())
                else:
                    extr_graf[x[0]].append(x[1].date())
            
        self.text_data_1.set(a_w_d)
        self.text_data_2.set(n_j)
        self.text_data_3.set("")
        self.text_data_4.set(pl_an)
        self.text_data_5.set(ex_an)
        self.text_data_6.set(an_t_c)



        self.plot_graf_anest(plan_graf, extr_graf)
                
        self.update_text()

    def clear_widget(self):   

        for widg in self.graf_frame_data.winfo_children():
            widg.destroy()
    

    def update_text(self):
        self.clear_widget()

        ttk.Label(self.graf_frame_data,
                  text = f"{self.text_string_1.get()}",
                  font=("Arial", 12), width = 55, anchor = 'w', justify='left' ).grid(
                      row=0,  columnspan=2, sticky=("WE"), padx=10, pady=10)
        ttk.Label(self.graf_frame_data,
                  text = f'{self.text_data_1.get()}',
                  font=("Arial", 12), width = 20, anchor = 'e', justify='right' ).grid(
                      row=0, column=2, sticky=("W"), padx=10, pady=10)

        ttk.Label(self.graf_frame_data,
                  text = f"{self.text_string_2.get()}",
                  font=("Arial", 12), width = 55, anchor = 'w',  justify='left' ).grid(
                      row=1,  columnspan=2, sticky=("WEs"), padx=10, pady=10)
        ttk.Label(self.graf_frame_data,
                  text = f'{self.text_data_2.get()}',
                  font=("Arial", 12), width = 20, anchor = 'e', justify='right' ).grid(
                      row=1, column=2, sticky=("W"), padx=10, pady=10)

        ttk.Label(self.graf_frame_data,
                  text = f"{self.text_string_3.get()}",
                  font=("Arial", 12), width = 55, anchor = 'w', justify='left' ).grid(
                      row=2, columnspan=2, sticky=("W"), padx=10, pady=10)
        ttk.Label(self.graf_frame_data,
                  text = f'{self.text_data_3.get()}',
                  font=("Arial", 12), width = 20, anchor = 'e', justify='right' ).grid(
                      row=2, column=2, sticky=("W"), padx=10, pady=10)

        ttk.Label(self.graf_frame_data,
                  text = f"{self.text_string_4.get()}",
                  font=("Arial", 12), anchor = 'w', justify='left' ).grid(
                      row=3, column=0, sticky=("W"), padx=10, pady=10)
        ttk.Label(self.graf_frame_data,
                  text = f'{self.text_data_4.get()}',
                  font=("Arial", 12),  anchor = 'nw', justify='right' ).grid(
                      row=4, column=0, sticky=("SN"), padx=10, pady=10)

        ttk.Label(self.graf_frame_data,
                  text = f"{self.text_string_5.get()}",
                  font=("Arial", 12), anchor = 'w', justify='left' ).grid(
                      row=3, column=1, sticky=("W"), padx=10, pady=10)
        ttk.Label(self.graf_frame_data,
                  text = f'{self.text_data_5.get()}',
                  font=("Arial", 12),  anchor = 'nw', justify='right' ).grid(
                      row=4, column=1, sticky=("SN"), padx=10, pady=10)

        ttk.Label(self.graf_frame_data,
                  text = f"{self.text_string_6.get()}",
                  font=("Arial", 12), anchor = 'w', justify='left' ).grid(
                      row=3, column=2, sticky=("W"), padx=10, pady=10)
        ttk.Label(self.graf_frame_data,
                  text = f'{self.text_data_6.get()}',
                  font=("Arial", 12), anchor = 'nw', justify='right' ).grid(
                      row=4, column=2, sticky=("SN"), padx=10, pady=10)


    def plot_graf_anest(self, plan_graf, extr_graf):
        plg = defaultdict(list)
        otd_l = []
        for key, value in plan_graf.items():
            v = Counter(value)
            plg[key].append(v)
        exg = defaultdict(list)
        for key, value in extr_graf.items():
            v = Counter(value)
            exg[key].append(v)
        pl_k = list(plg.keys())
        ex_k = list(exg.keys())
        pl_k.extend(ex_k)
        self.otd_l = list(set(pl_k))

        self.otd_lst.configure(values = self.otd_l)

        if ((self._var_otd.get()=="" and self._vars_anest.get()=="") or
                    (self._var_otd.get()=="")):
            self.ax.clear()
            self.ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%d.%m.%y"))
            locator = matplotlib.dates.AutoDateLocator()
            locator.intervald[matplotlib.dates.DAILY] = [1]
            self.ax.tick_params(axis='x', labelrotation=15, labelsize = 8)
            self.ax.xaxis.set_major_locator(locator)
            formatter = matplotlib.ticker.FormatStrFormatter('%d')
            self.ax.yaxis.set_major_formatter(formatter)
            self.ax.set_xlim(self.start_date, self.now_date)
            self.ax.set_ylim(-7, 7)
            self.canvas_tkagg.draw()

        self.ax.clear()
        self.ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%d.%m.%y"))
        locator = matplotlib.dates.AutoDateLocator()
        locator.intervald[matplotlib.dates.DAILY] = [1]
        self.ax.tick_params(axis='x', labelrotation=15, labelsize = 8)
        self.ax.xaxis.set_major_locator(locator)
        formatter = matplotlib.ticker.FormatStrFormatter('%d')
        self.ax.yaxis.set_major_formatter(formatter)
        self.ax.set_xlim(self.start_date, self.now_date)
        self.ax.set_ylim(-7, 7)
        
        for k, v in plg.items():
            xdata = []
            ydata = []
            if self._var_otd.get() == k:
                for x, y in sorted(v[0].items()): 
                    xdata.append(x)
                    ydata.append(y)
                self.ax.bar(xdata, ydata, label = f' План  {self._var_otd.get()}' )
                self.ax.legend(fontsize=10)
                self.canvas_tkagg.draw()

        for k, v in exg.items():
            xdata = []
            ydata = []
            if self._var_otd.get() == k:
                for x, y in sorted(v[0].items()): 
                    xdata.append(x)
                    ydata.append(-y)
        
                self.ax.bar(xdata, ydata, label = f'Экстр {self._var_otd.get()}')
                self.ax.legend(fontsize=10)
                self.canvas_tkagg.draw()
        

    def plot_graf_rean(self, pat_cnt_graf, nigth_graf, death_graf):

        self._var_otd.set("")
        self.otd_lst.configure(values = [])
        self.ax.clear()
        self.ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%d.%m.%y"))
        locator = matplotlib.dates.AutoDateLocator()
        locator.intervald[matplotlib.dates.DAILY] = [1]
        self.ax.tick_params(axis='x', labelrotation=15, labelsize = 8)
        self.ax.xaxis.set_major_locator(locator)
        formatter = matplotlib.ticker.FormatStrFormatter('%d')
        self.ax.yaxis.set_major_formatter(formatter)
        self.ax.set_xlim(self.start_date, self.now_date)
        self.ax.set_ylim(-7, 7)

        pat_cnt_graf = {k:len(v) for k,v in pat_cnt_graf.items()}
        nigth_graf = {k:len(v) for k,v in nigth_graf.items()}
        death_graf = {k:len(v) for k,v in death_graf.items()}
        
        xdata = []
        ydata = []
        for k, v in pat_cnt_graf.items():
            xdata.append(k)
            ydata.append(v)
        self.ax.bar(xdata, ydata, label = f' Общее количество ' )
        self.ax.legend(fontsize=10)
        self.canvas_tkagg.draw()

        xdata.clear()
        ydata.clear()
        
        for k, v in nigth_graf.items():
            xdata.append(k)
            ydata.append(v)
        self.ax.bar(xdata, ydata, label = f' Ночное поступление ')
        self.ax.legend(fontsize=10)
        self.canvas_tkagg.draw()

        xdata.clear()
        ydata.clear()
        
        for k, v in death_graf.items():
            xdata.append(k)
            ydata.append(-v)
        self.ax.bar(xdata, ydata, label = f' Смерть ')
        self.ax.legend(fontsize=10)
        self.canvas_tkagg.draw()


  

class DataListForm(tk.Frame):
    """The input form for our widgets"""

    def __init__(self, master, model, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.model = model
        self.master = master
        self.master.grid(row=1, column=0, sticky=("W, E, N, S"))
        self.list_frame = ttk.Frame(self, relief = 'sunken')
        self.list_frame.grid(row=0, column=0, sticky=("W, E, N, S"))

        self.list_frame.columnconfigure(0, weight = 1)
        self.list_frame.rowconfigure(1, weight = 1)
        self.list_frame_info = ttk.Frame(self.list_frame, relief = 'sunken')
        self.list_frame_info.grid(row=0, column=0, sticky=("W, E, N, S"))

        self._vars_dl_profil = {
            'Реанимация' : tk.StringVar(),
            'Анестезиология' : tk.StringVar() }
        self._vars_dl_profil['Реанимация'].set('1')
        self._vars_dl_profil['Анестезиология'].set('1')
        self._vars_find_date = tk.StringVar()
        
        self.text_FIO = tk.StringVar()
        self.text_info_3 = tk.StringVar()
        self.text_info_4 = tk.StringVar()
        self.text_info_6 = tk.StringVar()
        
        self.text_info_3.set(self.model._model_data['Реанимация'].get())
        self.text_info_4.set(self.model._model_data['Анестезиология'].get())
        self.text_info_6.set('')
        self.list_tree_data = RecordList(self.list_frame, header = COMMON_HEAD)
        image = os.path.join(os.path.dirname(__file__), images.MAGNIFER)
        self.find_FIO_image = tk.PhotoImage(file=image)

        ttk.Checkbutton(
            self.list_frame_info, variable=self._vars_dl_profil['Реанимация'],
                        text=f'Реанимация:         ', style= 'main2.Toolbutton',
            command = self.toggle_profile).grid(
            row=0, column=0, sticky=("W"), padx=10, pady=10)

        ttk.Label(self.list_frame_info, textvariable = self.text_info_3, font=("Arial", 12), width=6,
                  anchor='e').grid(
            row=0, column=1, sticky=("E"), padx=10, pady=10)


        ttk.Checkbutton(
            self.list_frame_info, variable = self._vars_dl_profil['Анестезиология'],
            text=f'Анестезиология: ', style= 'main2.Toolbutton',
            command = self.toggle_profile).grid(
            row=1, column=0, sticky=("W"), padx=10, pady=10)

        ttk.Label(self.list_frame_info, textvariable = self.text_info_4, font=("Arial", 12), width=6,
                  anchor='e').grid(
            row=1, column=1, sticky=("E"), padx=10, pady=10)


        self.separator_dl1 = ttk.Separator(self.list_frame_info, orient = "vertical")
        self.separator_dl1.grid(row=0, rowspan=2, column=5, pady=5, sticky=("S, N"))


        ttk.Label(self.list_frame_info, text = "Поиск по ФИО: ", font=("Arial", 12)).grid(
            row=0, column=6, sticky=("E"), padx=10, pady=10)

        self.find_FIO = w.MyEntryFIO(
            self.list_frame_info, textvariable=self.text_FIO)
        self.find_FIO.grid(row=1, column=6, padx=20, pady=(0, 10), sticky=(tk.W + tk.E))

        ttk.Button(
          self.list_frame_info, text = "Найти", image = self.find_FIO_image, compound = tk.LEFT,
          style= 'main2.Toolbutton', command=self.find_FIO_event).grid(
              row=1, column=7, padx=20, pady=(0, 10),sticky=(tk.W + tk.E))

        self.separator_dl2 = ttk.Separator(self.list_frame_info, orient = "vertical")
        self.separator_dl2.grid(row=0, rowspan=2, column=8, pady=5, sticky=("S, N"))


        self.separator_dl2 = ttk.Separator(self.list_frame_info, orient = "vertical")
        self.separator_dl2.grid(row=0, rowspan=2, column=8, pady=5, sticky=("S, N"))

        ttk.Label(self.list_frame_info, text='Сортировка по дате', font=("Arial", 12)).grid(row=0, column=9, columnspan=2,
                                                            padx=15, sticky=(tk.W + tk.E))

        self.date_find = w.MyDateEntry(self.list_frame_info,
                                       textvariable=self._vars_find_date,
                                     style = 'my.DateEntry', date_pattern = 'dd.mm.yy',
                      locale = 'ru_RU', state = "readonly",
                      mindate=None, maxdate = w.Calendar.date.today())

        self.date_find.grid(row=1, column=9, columnspan=2, padx=15, pady=(0, 10), sticky=(tk.W))

        ttk.Button(
          self.list_frame_info, text = "Найти", image = self.find_FIO_image, compound = tk.LEFT,
          style= 'main2.Toolbutton', command=self.find_date_event).grid(
              row=1, column=11, padx=10, pady=(0, 10),sticky=(tk.W))



        self.separator_dl3 = ttk.Separator(self.list_frame_info, orient = "vertical")
        self.separator_dl3.grid(row=0, rowspan=2, column=14, pady=5, sticky=("S, N"))

        
        self.list_tree_data.grid(row=1, column=0, sticky=("W, E, N, S"))               
        self.list_tree_data.columnconfigure(0, weight = 1)

    def populate_data_list(self, rows):
            self.list_tree_data.populate(rows)

    def find_date_event(self):
        date = self._vars_find_date.get()
        self.list_tree_data.show_date(date)

    def find_FIO_event(self):
        text = self.text_FIO.get()
        self.list_tree_data.show_FIO(text, True)

    def open_record_tree(self):
        rowkey = self.list_tree_data.selected_id
        return rowkey

    def add_tagged(self, data, update_data):
        if update_data == 'new_data':
            self.list_tree_data.add_inserted_row(data)
            
        elif update_data == 'upd_data':
            self.list_tree_data.add_updated_row(data)

    def get_tagged(self):
        insert = self.list_tree_data._inserted
        update = self.list_tree_data._updated
        if insert and update:
            return True
        else:
            return False
        


    def clear_tagged(self):
        self.list_tree_data.clear_tags()

    def toggle_profile(self):
        if (self._vars_dl_profil['Анестезиология'].get()=='1' and
            self._vars_dl_profil['Реанимация'].get()=='1'):
            self.list_tree_data.show_profile(anest = 'Анестезиология', rean = 'Реанимация')

        elif self._vars_dl_profil['Анестезиология'].get()=='1':
            self.list_tree_data.show_profile(anest = 'Анестезиология')
        elif self._vars_dl_profil['Реанимация'].get()=='1':
             self.list_tree_data.show_profile(rean = 'Реанимация')
        else:
            self.list_tree_data.show_profile()



class DataRecordForm(tk.Frame):
    """The input form for our widgets"""


    def __init__(self, master, model, filename, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.model = model
        self.filename_empl = filename
        self.master = master
        self.current_record = None
        self.master.grid(row=1, column=0, sticky=("W, E, N, S"))

        self._vars_common = {
                    'Профиль': tk.StringVar(),
                    'Номер истории': tk.StringVar(),
                    'Ф.И.О. больного': tk.StringVar(),
                    'Пол': tk.StringVar(),
                    'Возраст': tk.StringVar()}

        self._vars_date = {
                    'Дата поступления': tk.StringVar(),
                    'Время поступления': tk.StringVar(),
                    'Дата выписки': tk.StringVar(),
                    'Время выписки': tk.StringVar(),
                    'Длительность': tk.StringVar()}

        self._vars_rean = {
                    'Адрес': tk.StringVar(),
                    'Место работы': tk.StringVar(),
                    'Диагноз при поступлении': tk.StringVar(),
                    'Кем направлен': tk.StringVar(),
                    'Перевод': tk.StringVar(),
                    'Смерть': tk.StringVar(),
                    'ХАИ': tk.StringVar(),
                    'Covid19': tk.StringVar(),
                    'ВИЧ': tk.StringVar()}

        self._vars_anest = {
                    'Отделение': tk.StringVar(),
                    'Ангиооперационная': tk.StringVar(),
                    'Операция': tk.StringVar(),
                    'Вид обезболивания': tk.StringVar(),
                    'Анестезиолог': tk.StringVar(),
                    'Вр_опер': tk.StringVar()}

        self.values_time = ["н/д", "08:00", "08:30", "09:00", "09:30", "10:00", "10:30", "11:00", "11:30",
                            "12:00", "12:30", "13:00", "13:30", "14:00", "14:30", "15:00", "15:30",
                            "16:00", "16:30", "17:00", "17:30", "18:00",  "18:30", "19:00", "19:30",
                            "20:00", "20:30", "21:00", "21:30", "22:00", "22:30", "23:00", "23:30",
                            "00:00", "00:30", "01:00", "01:30", "02:00", "02:30", "03:00", "03:30",
                            "04:00", "04:30", "05:00", "05:30", "06:00", "06:30", "07:00", "07:30"]
        
        EMPLOYEES_HEADERS = ['famili', 'first_name', 'last_name',
          'phone', 'status', 'birthday', 'famili_IO']

        with open(self.filename_empl, 'r', encoding='cp1251', newline='') as f:
            f_s = csv.DictReader(f,EMPLOYEES_HEADERS)
            empl = list(dct['famili_IO'] for dct in f_s if dct['status']=='Врач')


        # Форма записи реанимации
        self.data_frame = ttk.Frame(self, relief = 'sunken')
        self.data_frame.grid(row=0, column=0, sticky=("W, E, N, S"))

        self.data_frame.columnconfigure(0, weight = 0)
        self.data_frame.columnconfigure(1, weight = 1)
        self.data_frame.rowconfigure(0, weight = 1)


        self.left_frame = ttk.Frame(self.data_frame, relief = 'sunken')
        self.left_frame.grid(row=0, column=0, sticky=("W, E, N, S"))


        # Запись общей информации
        self.common_info = ttk.LabelFrame(self.left_frame, text="Общая информация",
                                     borderwidth=5, relief='sunken', labelanchor='n')

        for i in range(4):
          self.common_info.columnconfigure(i, weight=1)

        ttk.Label(self.common_info, text='Номер истории').grid(row=0, column=0, padx=20,
                                                     sticky=(tk.W + tk.E))
        w.MyEntryInteger(
            self.common_info, width=10, dig_num=6, textvariable=self._vars_common['Номер истории']
        ).grid(row=1, column=0, padx=20, pady=(0, 10), sticky=(tk.W))

        ttk.Label(self.common_info, text='Ф.И.О. больного').grid(row=0, column=1, padx=20,
                                                       sticky=(tk.W + tk.E))
        w.MyEntryFIO(
            self.common_info, textvariable=self._vars_common['Ф.И.О. больного'], disable_var=False,
        ).grid(row=1, column=1, padx=20, pady=(0, 10), sticky=(tk.W + tk.E))

        ttk.Label(self.common_info, text='Пол').grid(row=0, column=2, padx=5,
                                           sticky=(tk.W + tk.E))
        gendframe = ttk.Frame(self.common_info)
        ttk.Radiobutton(gendframe, value='Муж', text='Муж', variable=self._vars_common['Пол']
                        ).pack(side=tk.LEFT, padx=15, pady=(0, 10), expand=True)
        ttk.Radiobutton(gendframe, value='Жен', text='Жен', variable=self._vars_common['Пол']
                        ).pack(side=tk.LEFT, padx=15, pady=(0, 10), expand=True)
        self._vars_common['Пол'].set('Муж')
        gendframe.grid(row=1, column=2, sticky=(tk.W + tk.E), padx=15)

        ttk.Label(self.common_info, text=' Возраст\n(полных лет)').grid(row=0, column=3, padx=20,
                                                            sticky=(tk.W + tk.E))
        w.MyEntryInteger(
            self.common_info, width=3, dig_num=3, textvariable=self._vars_common['Возраст']
        ).grid(row=1, column=3, padx=20, pady=(0, 10), sticky=(tk.W))

        self.common_info.grid(sticky=("W, E, S, N"),column=0, row=0)
        
        self.common_info.focus_set()


        #Запись движения(дата и время)

        self.dtime_info = ttk.LabelFrame(self.left_frame, text="Движение пациента",
                                     borderwidth=5, relief='sunken', labelanchor='n')

        for i in range(9):
          self.dtime_info.columnconfigure(i, weight=1)

        ttk.Label(self.dtime_info, text='Поступление\nдата').grid(row=0, column=0, columnspan=2,
                                                            padx=15, sticky=(tk.W + tk.E))

        self.date_in = w.MyDateEntry(self.dtime_info, textvariable=self._vars_date['Дата поступления'],
                                     style = 'my.DateEntry', date_pattern = 'dd.mm.yy',
                      locale = 'ru_RU', state = "readonly",
                      mindate=None, maxdate = w.Calendar.date.today())
        self.date_in.bind('<FocusOut>',
                            lambda event: self.upd_date(self.date_in.get_date()))

        self.date_in.grid(row=1, column=0, columnspan=2, padx=15, pady=(0, 10), sticky=(tk.W))
        
        ttk.Label(self.dtime_info, text=' \nвремя').grid(row=0, column=2, columnspan=2,
                                                             padx=15, sticky=(tk.W + tk.E))
        w.MyTimeEntry(
          self.dtime_info, width=12, values=self.values_time,  textvariable=self._vars_date['Время поступления']
            ).grid(row=1, column=2, columnspan=2, padx=15, pady=(0, 10), sticky=(tk.W))
        
        ttk.Label(self.dtime_info, text='Выписка\nдата').grid(row=0, column=4, columnspan=2,
                                                        padx=15, sticky=(tk.W + tk.E))


        self.date_out = w.MyDateEntry(self.dtime_info, textvariable=self._vars_date['Дата выписки'],
                                      style = 'my.DateEntry', date_pattern = 'dd.mm.yy',
                        locale = 'ru_RU', state = "readonly",
                       mindate=None, maxdate = w.Calendar.date.today())

        self.date_out.grid(row=1, column=4, columnspan=2, padx=15, pady=(0, 10), sticky=(tk.W))

        ttk.Label(self.dtime_info, text=' \nвремя').grid(row=0, column=6, columnspan=2,
                                                         padx=15, sticky=(tk.W + tk.E))
        w.MyTimeEntry(
          self.dtime_info, width=12, values=self.values_time, textvariable=self._vars_date['Время выписки']
            ).grid(row=1, column=6, columnspan=2, padx=15, pady=(0, 10), sticky=(tk.W))

        ttk.Label(self.dtime_info, text='Длительность').grid(row=0, column=8, columnspan=2,
                                                      padx=15, sticky=(tk.W + tk.E))

        self.delta_date_common = ttk.Entry(
          self.dtime_info, state = "readonly",  width=15, textvariable=self._vars_date['Длительность']
            )
        
        self.delta_date_common.bind('<FocusIn>',
                                    lambda event: self._delta_date_common_get())

        self.delta_date_common.grid(row=1, column=8, columnspan=2, padx=15, pady=(0, 10), sticky=(tk.W))

        self.dtime_info.grid(sticky=("W, E, S, N"),column=0, row=1)

        
        # Запись данных Реанимация
        
        self.rean_info = ttk.LabelFrame(self.left_frame, text="Реанимация",
                                     borderwidth=5, relief='sunken', labelanchor='n')

        for i in range(9):
          self.rean_info.columnconfigure(i, weight=1)

        ttk.Label(self.rean_info, text='Адрес').grid(row=0, column=0, columnspan=2, padx=10,
                                             sticky=(tk.W + tk.E))
        w.MyAutocompleteCombobox(
          self.rean_info, textvariable=self._vars_rean['Адрес'],
            values=None, text_w='Адрес'
            ).grid(row=1, column=0, columnspan=2, padx=10, pady=(0, 10), sticky=(tk.W + tk.E))

        ttk.Label(self.rean_info, text='Место работы').grid(row=0, column=2,columnspan=2, padx=10,
                                                    sticky=(tk.W + tk.E))
        w.MyAutocompleteCombobox(self.rean_info, textvariable=self._vars_rean['Место работы'],
                             values=None, text_w='Место работы'
                                 ).grid(row=1, column=2, columnspan=2,
                                padx=10, pady=(0, 10), sticky=(tk.W + tk.E))

        ttk.Label(self.rean_info, text='Кем направлен').grid(row=0, column=4,columnspan=2,
                                                         padx=10, sticky=(tk.W + tk.E))
        w.MyAutocompleteCombobox(
          self.rean_info, textvariable=self._vars_rean['Кем направлен'],
            values=None, text_w='Кем направлен'
            ).grid(row=1, column=4, columnspan=2, padx=10, pady=(0, 10), sticky=(tk.W + tk.E))

        ttk.Label(self.rean_info, text='Перевод').grid(row=0, column=6,columnspan=2,
                                                   padx=10, sticky=(tk.W + tk.E))
        w.MyAutocompleteCombobox(
          self.rean_info, textvariable=self._vars_rean['Перевод'],
            values=None, text_w='Перевод'
            ).grid(row=1, column=6, columnspan=2, padx=10, pady=(0, 10), sticky=(tk.W + tk.E))

        ttk.Label(self.rean_info, text='Диагноз').grid(row=2, column=0,columnspan=2,
                                                                   padx=10, sticky=(tk.W + tk.E))
        w.MyAutocompleteCombobox(
          self.rean_info, textvariable=self._vars_rean['Диагноз при поступлении'],
            values=None, text_w='Диагноз при поступлении'
            ).grid(row=3, column=0, columnspan=4, padx=10, pady=(0, 10), sticky=(tk.W + tk.E))

        ttk.Checkbutton(
                      self.rean_info, variable=self._vars_rean['Смерть'], text='Смерть'
                      ).grid(row=3, column=4, padx=10, pady=(0, 10), sticky=(tk.W))
        self._vars_rean['Смерть'].set('')
        
        ttk.Checkbutton(
                      self.rean_info, variable=self._vars_rean['ХАИ'], text='ХАИ'
                      ).grid(row=3, column=5, padx=10, pady=(0, 10), sticky=(tk.W))
        self._vars_rean['ХАИ'].set('')
        
        ttk.Checkbutton(
                      self.rean_info, variable=self._vars_rean['Covid19'], text='Covid19'
                      ).grid(row=3, column=6, padx=10, pady=(0, 10), sticky=(tk.W))
        self._vars_rean['Covid19'].set('')

        ttk.Checkbutton(
                      self.rean_info, variable=self._vars_rean['ВИЧ'], text='ВИЧ'
                      ).grid(row=3, column=7, padx=10, pady=(0, 10), sticky=(tk.W))
        self._vars_rean['ВИЧ'].set('')

        self.rean_info.grid(sticky=("W, E, S, N"),column=0, row=2)

        # Запись данных Анестезиология        

        self.anest_info = ttk.LabelFrame(self.left_frame, text="Анестезиология",
                                     borderwidth=5, relief='sunken', labelanchor='n')
        for i in range(4):
          self.anest_info.columnconfigure(i, weight=1)

        ttk.Label(self.anest_info, text='Отделение').grid(row=0, column=0, padx=10, sticky=(tk.W + tk.E))

        w.MyAutocompleteCombobox(
          self.anest_info, textvariable=self._vars_anest['Отделение'],
            values = None, text_w='Отделение'
        ).grid(row=1, column=0, padx=10, pady=(0, 10), sticky=(tk.W))

        ttk.Checkbutton(
                      self.anest_info, variable=self._vars_anest['Ангиооперационная'],
                      text='Ангиооперационная').grid(row=1, column=1,  pady=(0, 10), sticky=(tk.W))

        ttk.Label(self.anest_info, text='Операция').grid(row=0, column=2, columnspan=3, padx=10,sticky=(tk.W + tk.E))
        w.MyAutocompleteCombobox(self.anest_info, textvariable=self._vars_anest['Операция'],
                                    values = None, text_w='Операция'
                                 ).grid(row=1, column=2, columnspan=2,
                                            padx=10, pady=(0, 10), sticky=(tk.W + tk.E))

        ttk.Label(self.anest_info, text='Вид обезболивания').grid(row=2, column=0, padx=10, sticky=(tk.W ))
        w.MyAutocompleteCombobox(
          self.anest_info, textvariable=self._vars_anest['Вид обезболивания'],
          values = None, text_w='Вид обезболивания'
            ).grid(row=3, column=0, padx=10, pady=(0, 10), sticky=(tk.W))

        ttk.Label(self.anest_info, text='Анестезиолог').grid(row=2, column=1,padx=10, sticky=(tk.W + tk.E ))
        w.MyAutocompleteCombobox(
          self.anest_info, textvariable=self._vars_anest['Анестезиолог'],
            values = empl).grid(row=3, column=1, padx=10, pady=(0, 10), sticky=(tk.W ))

        ttk.Label(self.anest_info, text='Ургентность').grid(row=2, column=2, padx=10,
                                           sticky=(tk.W + tk.E))

        emergyframe = ttk.Frame(self.anest_info)
        ttk.Radiobutton(emergyframe, value='план', text='План', variable=self._vars_anest['Вр_опер']
            ).pack(side=tk.LEFT, padx=10, pady=(0, 10), expand=True)
        ttk.Radiobutton(emergyframe, value='экстр', text='Экстр', variable=self._vars_anest['Вр_опер']
            ).pack(side=tk.LEFT, padx=10, pady=(0, 10), expand=True)
        self._vars_anest['Вр_опер'].set('план')
        emergyframe.grid(row=3, column=2, columnspan=2, sticky=(tk.W+ tk.E ))

        self.anest_info.grid(sticky=("W, E, S, N"),column=0, row=3)
        

        frame_buttons = ttk.LabelFrame(self.left_frame, text="Действия",
                                     borderwidth=5, relief='sunken', labelanchor='n')

        self.savebutton = ttk.Button(
          frame_buttons, text="Новая запись", command=self._new_record)
        self.savebutton.pack(side=tk.RIGHT, padx=10, pady=5)

        self.resetbutton = ttk.Button(
          frame_buttons, text="Очистить", command=self._reset)
        self.resetbutton.pack(side=tk.LEFT, padx=10, pady=5)


        frame_buttons.grid(sticky=("W, E, S, N"),column=0, row=6, rowspan=2)

        self.commom_info_list_widget = [_ for _ in self.common_info.winfo_children()]

        self.date_list_widget = [_ for _ in self.dtime_info.winfo_children()]


        self.text_info_3 = tk.StringVar()
        self.text_info_4 = tk.StringVar()
        self.text_info_6 = tk.StringVar()
        
        self.text_info_3.set(self.model._model_data['Реанимация'].get())
        self.text_info_4.set(self.model._model_data['Анестезиология'].get())
        self.text_info_6.set('')


        self.right_frame = ttk.Frame(self.data_frame, relief = 'sunken')
        self.right_frame.grid(row=0, column=1, sticky=("W, E, N, S"))

        self.right_frame.columnconfigure(0, weight = 1)
        self.right_frame.rowconfigure(1, weight=1)

        self.right_frame_info = ttk.Frame(self.right_frame, relief = 'sunken')
        self.right_frame_info.grid(row=0, column=0, sticky=("W, E, N, S"))

        ttk.Label(self.right_frame_info, text='id записи: ', font=("Arial", 12)).grid(
            row=0, column=0, sticky=("W"), padx=10, pady=10)
        ttk.Label(self.right_frame_info, textvariable = self.text_info_6, width = 7, font=("Arial", 12)).grid(
            row=0, column=1, sticky=("E"), padx=10, pady=10)


        ttk.Label(self.right_frame_info, text='Реанимация: ', font=("Arial", 12)).grid(
            row=0, column=2, sticky=("W"), padx=10, pady=10)
        ttk.Label(self.right_frame_info, textvariable = self.text_info_3, font=("Arial", 12)).grid(
            row=0, column=3, sticky=("E"), padx=10, pady=10)


        ttk.Label(self.right_frame_info, text='Анестезиология: ', font=("Arial", 12)).grid(
            row=1, column=2, sticky=("W"), padx=10, pady=10)
        ttk.Label(self.right_frame_info, textvariable = self.text_info_4, font=("Arial", 12)).grid(
            row=1, column=3, sticky=("E"), padx=10, pady=10)
       

        self.tab_rean_anest = ttk.Notebook(self.right_frame)
        self.tab_rean_anest.grid(row=1, column=0, sticky=("W, E, N, S"))
        self.tab_rean_anest.columnconfigure(0, weight=1)
        self.tab_rean_anest.rowconfigure(0, weight=1)
 
        self.tab_rean_anest.bind('<<NotebookTabChanged>>', self._notebook_change)
     

        self.recordlist_rean = RecordList(self.tab_rean_anest,
                                          header = REAN_HEAD)

        self.recordlist_rean.grid(row=0, column=0, sticky=("W, E, N, S"))

        self.recordlist_anest = RecordList(self.tab_rean_anest,
                                           header = ANEST_HEAD)

        self.recordlist_anest.grid(row=0, column=0, sticky=("W, E, N, S"))
        self.tab_rean_anest.add(self.recordlist_rean, text = f'{" "*15}Реанимация{" "*15}')
        self.tab_rean_anest.add(self.recordlist_anest, text = f'{" "*15}Анестезиология{" "*15}')

    #### List widgets
        self.anest_list_widget = list(self.get_all_widgets(self.anest_info))
        self.rean_list_widget = list(self.get_all_widgets(self.rean_info))
        self.rean_anest_list_widget = [*self.rean_list_widget,
                                       *self.anest_list_widget]
        self.autocomplet_combo_w_list = [aw for aw in
                                         self.rean_anest_list_widget if
                                         isinstance(aw, ttk.Combobox)]


    # Get autocomlet widget data from model
    def get_autocompect_data(self, rows):
        autocomplet = ['Адрес', 'Место работы', 'Диагноз при поступлении',
                       'Кем направлен', 'Перевод', 'Отделение', 'Операция',
                       'Вид обезболивания', 'Анестезиолог']
        self.autocomplet_dict = {}

        if rows == []:
            return False
        for cur_row in rows:
            current_row = {key: value for key, value in cur_row.items()
                           if key in autocomplet}
            for k, v in current_row.items():
                if v is None: v =''
                self.autocomplet_dict.setdefault(k, set()).add(v)

    # Get all widgets in frame
    def get_all_widgets(self, parent_widget):
        yield parent_widget
        for chld_w in parent_widget.winfo_children():
            if chld_w.winfo_children():
                yield from chld_w.winfo_children()
            else:
                yield chld_w


    def _notebook_change(self, *_, notebook_index=None):

        if notebook_index is None:
            notebook_index = self.tab_rean_anest.index("current")
        if notebook_index == 0:
            self.tab_rean_anest.select(0)
            [self._vars_anest[key].set('') for key in self._vars_anest.keys()]
            for w in self.anest_list_widget:
                w.state(['disabled'])
            for w in self.rean_list_widget:
                w.state(['!disabled'])
        else:
            self.tab_rean_anest.select(1)
            self._vars_anest['Вр_опер'].set('план')
            for w in self.anest_list_widget:
                w.state(['!disabled'])
            [self._vars_rean[key].set('') for key in self._vars_rean.keys()]
            for w in self.rean_list_widget:
                w.state(['disabled'])

        self._delta_date_common_get()        


    def _delta_date_common_get(self, *_):

        
        notebook_index = self.tab_rean_anest.index("current")

        if (self._vars_date['Время поступления'].get()=="н/д" or
            self._vars_date['Время выписки'].get()=="н/д"):
            self._vars_date['Длительность'].set('')
            return False

        time_in = datetime.strptime(self._vars_date['Дата поступления'].get() +
                                    ' ' + self._vars_date['Время поступления'].get(), '%d.%m.%y %H:%M')
        time_out = datetime.strptime(self._vars_date['Дата выписки'].get() +
                                     ' ' + self._vars_date['Время выписки'].get(), '%d.%m.%y %H:%M')
        k_day = time_out - time_in

        if k_day.days >= 0:
            if notebook_index == 0:
                self._vars_date['Длительность'].set(f' {k_day.days} к/день')
            else:
                self._vars_date['Длительность'].set(f' {(k_day.days*86400 + k_day.seconds)/3600:.1f} час')
        else:
            self._vars_date['Длительность'].set(' ERROR !!!')
            StatusBar.status_text = 'Ошибка ! Время окончания раньше начала'
            self.event_generate('<<Status_set>>')


    # Установка границ даты выписки
    def upd_date(self, cur_day):
        self.date_out.config(mindate=cur_day)
        self.date_out.set_date(cur_day)

    def _new_record(self):
        self.event_generate('<<NewRecord>>')

    def _get(self):
        """Retrieve data from form as a dict"""
        notebook_index = self.tab_rean_anest.index("current")
        self.data= dict()
        errors = []
        if notebook_index ==0:
            self._vars_common['Профиль'].set('Реанимация')
            self.data = {**self._vars_common, **self._vars_date, **self._vars_rean}
        else:
            self._vars_common['Профиль'].set('Анестезиология')
            self.data = {**self._vars_common, **self._vars_date, **self._vars_anest}

        not_err_val = ('Смерть','ХАИ','Covid19','ВИЧ','Вр_опер','Ангиооперационная')
        for key, var in self.data.items():
            try:
                self.data[key] = var.get()
                if self.data[key] == '':
                    if key not in not_err_val:
                        errors.append(key)
                if self.data.get('Операция')=='Абразио':
                    self.data['Длительность']='0.1 час'
            except tk.TclError as e:
                raise e
        return self.data, errors

    def get_errors(self):
        errors = dict()

    def _update(self):
        pass

    def add_tagged(self, data, update_data):
        if update_data == 'new_data':
            self.recordlist_rean.add_inserted_row(data)
            self.recordlist_anest.add_inserted_row(data)
            
        elif update_data == 'upd_data':
            self.recordlist_rean.add_updated_row(data)
            self.recordlist_anest.add_updated_row(data)

    def clear_tagged(self):
        self.recordlist_rean.clear_tags()
        self.recordlist_anest.clear_tags()        

    def _reset(self):
        self.event_generate('<<ClearRecord>>')

    def reset(self):
        """Resets the form entries"""
        clear_data = {**self._vars_common, **self._vars_date,
                      **self._vars_rean, **self._vars_anest}
        # clear all values
        today = w.Calendar.date.today().strftime('%d.%m.%y')
        for var in clear_data.values():
            var.set('')
        self._vars_date['Дата поступления'].set(today)
        self._vars_date['Дата выписки'].set(today)
        self._vars_date['Время поступления'].set('08:00')
        self._vars_date['Время выписки'].set('08:00')
        self._vars_common['Пол'].set('Муж')
        if self.tab_rean_anest.index("current") == 1:
            self._vars_anest['Вр_опер'].set('экстр')
        self._delta_date_common_get()                    
        self.current_record = None

    def load_record(self, rownum, data=None):
        """Загружает выбранную строку в форму записи"""
        self.current_record = rownum
        if rownum is None:
            self._reset()
            self.text_info_6.set('New Record')
        else:
            if data['Профиль']=='Реанимация':
                self._notebook_change(notebook_index=0)
                self.recordlist_rean.treeview.selection_set(rownum)
                self.recordlist_rean.treeview.see(rownum)
            else:
                self._notebook_change(notebook_index=1)
                self.recordlist_anest.treeview.selection_set(rownum)
                self.recordlist_anest.treeview.see(rownum)
            self.text_info_6.set(rownum+1)
            for key, var in data.items():
                if self._vars_common.get(key):
                    if self._vars_common['Пол'].get()=='муж':
                        self._vars_common['Пол'].set('Муж')
                    if self._vars_common['Пол'].get() == 'жен':
                        self._vars_common['Пол'].set('Жен')
                    self._vars_common[key].set(var)
                elif self._vars_date.get(key):
                    self._vars_date[key].set(var)
                elif self._vars_rean.get(key):
                    self._vars_rean[key].set(var)
                elif self._vars_anest.get(key):
                    if self._vars_anest['Вр_опер'].get()=='план':
                        self._vars_anest['Вр_опер'].set('план')
                    if self._vars_anest['Вр_опер'].get()=='экстр':
                        self._vars_anest['Вр_опер'].set('экстр')
                    self._vars_anest[key].set(var)
                else:
                    continue
        
    def populate_data(self, rows):
        self.recordlist_rean.populate(rows, profile = 'Реанимация')
        self.recordlist_anest.populate(rows, profile = 'Анестезиология')

    def open_record_tree(self):
        notebook_index = self.tab_rean_anest.index("current")
        if notebook_index ==0:
            rowkey = self.recordlist_rean.selected_id
        else:
            rowkey = self.recordlist_anest.selected_id
        return rowkey


    def _delete(self):
        pass

    def _create(self):
        pass


class RecordList(tk.Frame):
    """Display for CSV file contents"""
    column_defs = {
        '#0': {'label': 'Row', 'anchor': tk.W},
        '№': {'label': '№', 'width': 50, 'anchor': tk.W},
        'Профиль': {'label': 'Профиль', 'width': 120},
        'Номер истории': {'label': 'Номер истории', 'width': 80},
        'Ф.И.О. больного': {'label': 'Ф.И.О. больного', 'width': 100, 'stretch': True},
        'Пол': {'label': 'Пол', 'width': 40, 'stretch': False},
        'Возраст': {'label': 'Возраст', 'width': 70, 'stretch': False},
        'Дата поступления': {'label': 'Дата поступления', 'width': 120, 'stretch': False},
        'Время поступления': {'label': 'Время поступления', 'width': 80},
        'Дата выписки': {'label': 'Дата выписки', 'width': 180},
        'Время выписки': {'label': 'Время выписки', 'width': 180},
        'Длительность': {'label': 'Длительность', 'width': 80},
        'Адрес': {'label': 'Адрес', 'width': 80},
        'Место работы': {'label': 'Место работы', 'width': 180},
        'Диагноз при поступлении': {'label': 'Диагноз', 'width': 120, 'stretch': True},
        'Кем направлен': {'label': 'Кем направлен', 'width': 80},
        'Перевод': {'label': 'Перевод', 'width': 80},
        'Смерть': {'label': 'Смерть', 'width': 50},
        'ХАИ': {'label': 'ХАИ', 'width': 40},
        'Covid19': {'label': 'Covid19', 'width': 40},
        'ВИЧ': {'label': 'ВИЧ', 'width': 40},
        'Реаниматолог': {'label': 'Реаниматолог', 'width': 80, 'stretch': True},
        'Отделение': {'label': 'Отделение', 'width': 80, 'stretch': False},
        'Ангиооперационная': {'label': 'Ангиооперационная', 'width': 80},
        'Операция': {'label': 'Операция', 'width': 80, 'stretch': True},
        'Вид обезболивания': {'label': 'Вид обезболивания', 'width': 100},
        'Анестезиолог': {'label': 'Анестезиолог', 'width': 80, 'stretch': True},
        'Вр_опер': {'label': 'Вр_опер', 'width': 40}
        }
    default_width = 100
    default_minwidth = 10
    default_anchor = tk.W



    def __init__(self, master, *args, header = None,  **kwargs):
        super().__init__(master, *args, **kwargs)
        self.master = master
        self._detached_items  = list()
        self._show_items = list()
        self._inserted = list()
        self._updated = list()
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.header = {k : v for k , v in self.column_defs.items() if k in
                       header}
        self.treeview = ttk.Treeview(self,
            columns=list(self.header.keys())[1:],
            selectmode='browse', show='headings', style='Treeview')
        self.treeview.grid(row=0, column=0, sticky='NSEW')

        # Configure treeview columns
        for name, definition in self.header.items():
            label = definition.get('label', '')
            anchor = definition.get('anchor', self.default_anchor)
            minwidth = definition.get('minwidth', self.default_minwidth)
            width = definition.get('width', self.default_width)
            stretch = definition.get('stretch', False)
            self.treeview.heading(name, text=label, anchor=anchor)
            self.treeview.column(
                name, anchor=anchor, minwidth=minwidth,
                width=width, stretch=stretch)
        image = os.path.join(os.path.dirname(__file__), images.ARROW)
        self.dl_image = tk.PhotoImage(file=image)

        self.treeview.heading('№', text = '№ ', image =self.dl_image, anchor = 'w',
                              command = lambda: self.sort('№', False, key=int))
        self.treeview.heading('Ф.И.О. больного', text = 'Ф.И.О. больного ', image =self.dl_image,
                              anchor = 'w', command = lambda: self.sort('Ф.И.О. больного', False))
        self.treeview.heading('Дата поступления', text = 'Дата поступления ', image =self.dl_image,
                              anchor = 'w', command = lambda: self.sort('Дата поступления',False,
                                        key=lambda s: datetime.strptime(s, "%d.%m.%y")))
        self.treeview.heading('Возраст', text = 'Возраст ', image =self.dl_image, anchor = 'w',
                              command = lambda: self.sort('Возраст', False, key=int))


        self.treeview.bind('<Double-1>', self._on_open_record)
        self.treeview.bind('<Return>', self._on_open_record)

        # configure scrollbar for the treeview
        self.scrollbar_y = ttk.Scrollbar(self,
            orient=tk.VERTICAL,
            command=self.treeview.yview)
        self.treeview.configure(yscrollcommand=self.scrollbar_y.set)
        self.scrollbar_y.grid(row=0, column=1, sticky='NSE')

        self.scrollbar_x = ttk.Scrollbar(self,
            orient=tk.HORIZONTAL,
            command=self.treeview.xview)
        self.treeview.configure(xscrollcommand=self.scrollbar_x.set)
        self.scrollbar_x.grid(row=1, column=0, sticky='ESW')

        self.count_rows = self.treeview.get_children()

        # configure tagging
        self.treeview.tag_configure('inserted', background='lightgreen')
        self.treeview.tag_configure('updated', background='lightblue')



    def sort(self, col, reverse, key=str):
        l = [(self.treeview.set(k, col), k) for k in self.treeview.get_children("")]
        if key is int:
            l = [(x[0],x[1]) if x[0]!='' else ('0', x[1]) for x in l]
        l.sort(reverse = reverse, key=lambda t: key(t[0]))
        for index, (_, k) in enumerate(l):
            self.treeview.move(k, "", index)
        self.treeview.heading(col, command=lambda: self.sort(col, not reverse, key=key))



    def populate(self, rows, profile = None):
        """Clear the treeview and write the supplied data rows to it."""
        current_row_list = []
        for row in self.treeview.get_children():
            self.treeview.delete(row)

        cids = self.treeview.cget('columns')
        self.count=1
        for rownum, rowdata in enumerate(rows):
            if rowdata['Профиль'] == profile:
                values = [rowdata[cid] if cid != '№' else str(self.count)
                          for cid in cids]
                self.count +=1

                if rownum in self._inserted:
                    tag = 'inserted'
                elif rownum in self._updated:
                    tag = 'updated'
                else:
                    tag = ''
            
                self.treeview.insert('', 'end', iid=str(rownum),
                         text=str(rownum), values=values, tag=tag)


            elif profile is None:
                values = [rowdata[cid] if cid != '№' else str(self.count)
                          for cid in cids]
                self.count +=1


                if rownum in self._inserted:
                    tag = 'inserted'
                elif rownum in self._updated:
                    tag = 'updated'
                else:
                    tag = ''

                self.treeview.insert('', 'end', iid=str(rownum),
                         text=str(rownum), values=values, tag=tag)


        if len(rows) > 0:
            self.treeview.focus_set()

    def get_children_rows(self):
        try:
            count_show_rows = self.treeview.get_children()
            if len(count_show_rows) == (self.count-1):
                self.count_rows = count_show_rows
        except:
            pass
        else:
            return count_show_rows
        
    def show_profile(self, anest = None, rean = None):
        count_show_rows = self.get_children_rows()
        matching = (anest, rean)
        for line in self.count_rows:
            if self.treeview.item(line)["values"][1] in matching:
                self.treeview.move(line, "", "end")
            else:
                self.treeview.detach(line)

    def show_date(self, date):
        date_limit = datetime.strptime(date, "%d.%m.%y")
        count_show_rows = self.get_children_rows()
        for line in self.count_rows:
            if datetime.strptime((self.treeview.item(line)["values"][4]), "%d.%m.%y") < date_limit:
                self.treeview.detach(line)
            else:
                self.treeview.move(line, "", "end")

    def show_FIO(self, text_FIO, flag_find):
        count_show_rows = self.get_children_rows()
        list_FIO=[]
        for line in self.count_rows:
            list_FIO.append(self.treeview.item(line)["values"][2])
        matching = [
            x for x in list_FIO
            if x.lower().startswith(text_FIO.lower())
        ]
        for line in self.count_rows:
            if self.treeview.item(line)["values"][2] in matching:
                self._show_items.append(line)
                self.treeview.move(line, "", "end")
            else:
                self._detached_items.append(line)
                self.treeview.detach(line)
        self._show_items.clear()
        self._detached_items.clear()

    def _on_open_record(self, *args):
        self.event_generate('<<OpenRecord>>')

    @property
    def selected_id(self):
        selection = self.treeview.selection()
        return int(selection[0]) if selection else None

    def add_updated_row(self, row):
        if row not in self._updated:
            self._updated.append(row)

    def add_inserted_row(self, row):
        if row not in self._inserted:
            self._inserted.append(row)

    def clear_tags(self):
        self._inserted.clear()
        self._updated.clear()

