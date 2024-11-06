"""
Statistic OARIT
"""
import calendar
import os, sys
import tkinter as tk
from tkinter import ttk
import csv
from pathlib import Path
from datetime import datetime, timedelta, date
from datetime import time
from tkinter import messagebox
from tkinter import filedialog
from tkinter.ttk import Style
from tkinter import Menu
from pprint import pprint
from collections import namedtuple, defaultdict
import locale
from . import myWidgets as w
from . import views as v
from . import models as m
from . import employees as e
from .mainmenu import MainMenu
from . import Data
from . import images


#PROGRAM_NAME = ' Statistic OARIT '

PATH_FILE_EMPLOYEES = os.path.join(os.path.dirname(__file__), Data.EMPLOYEES)
PATH_FILE_SCHEDULE = os.path.join(os.path.dirname(__file__), Data.SCHEDULE)
PATH_FILE_PATIENTS = os.path.join(os.path.dirname(__file__), Data.PATIENTS)




            # Check for append permissions:
for file in [PATH_FILE_EMPLOYEES, PATH_FILE_SCHEDULE, 
                                PATH_FILE_PATIENTS]:
    file_exists = os.access(Path(file), os.F_OK)
    parent_writeable = os.access(Path(file).parent, os.W_OK)
    file_writeable = os.access(Path(file), os.W_OK)
    if (
        (not file_exists and not parent_writeable) or
        (file_exists and not file_writeable)):
        msg = f'Доступ к файлу запрещен: {file}'
        messagebox.showerror(
        title='Error',
        message=msg)
        raise PermissionError(msg)
        quit()

EMPLOYEES_HEADERS = ['famili', 'first_name', 'last_name',
          'phone', 'status', 'birthday', 'famili_IO']

with open(PATH_FILE_EMPLOYEES, encoding='cp1251', newline='') as f:
    EMPLOYEES = csv.DictReader(f,EMPLOYEES_HEADERS)
    EMPLOYEES = [r for r in EMPLOYEES]


class Splash(tk.Toplevel):
    def __init__(self, parent):
        tk.Toplevel.__init__(self, parent)
        self.title("Statistic OARIT")
        self.x = (self.winfo_screenwidth() - self.winfo_reqwidth()) / 4
        self.y = (self.winfo_screenheight() - self.winfo_reqheight()) / 4
        self.geometry("+%d+%d" % (self.x, self.y))
        self.resizable(False,False)
        frame = tk.Frame(self,  bg = "gray75")
        frame.grid(row=0, column=0)
        tk.Label(frame, text = "Идет загрузка приложения.....",bg = "gray75",
                 font=("Arial", 22)).grid(row=0, column=0,  padx=100, pady=100)
        self.update()


class Application(tk.Tk):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Hide window while GUI is built
        self.withdraw()
        splash = Splash(self)

        # Create model
        self.model = m.CSVModel()

        image = os.path.join(os.path.dirname(__file__), images.ICON)
        self.stat_oarit_image = tk.PhotoImage(file=image)
        self.iconphoto(True, self.stat_oarit_image)

        # Begin building GUI
        self.title("Statistic OARIT")
        self.columnconfigure(0, weight=1)


        # Create menu
        menu = MainMenu(self)
        self.config(menu=menu)

        event_callbacks = {
            '<<FileSave>>': self._on_save,
            '<<FileQuit>>': lambda _: self._quit(),
            '<<ToolButton>>' : self.show_frame,
            '<<NewRecord>>' : self._new_record,
            '<<ClearRecord>>' : self._reset,
            '<<OpenRecord>>' : self._open_record,
            '<<Status_set>>' : self._status_update,
            '<<Employees>>' : self._employees
            
        }
        for sequence, callback in event_callbacks.items():
            self.bind(sequence, callback)

        # Initialize platform-specific options
        self.initializeTk()

        # Geometry GUI
        self.x = (self.winfo_screenwidth() - self.winfo_reqwidth()) / 8
        self.y = (self.winfo_screenheight() - self.winfo_reqheight()) / 8
        self.geometry("+%d+%d" % (self.x, self.y))
        self.resizable(False,False)

        # Create ToolBar
        self.toolbar = v.ToolBar(self)

        self.container = ttk.Frame(self)
        self.container.grid(column=0, row=1, sticky=("W, E, N, S"))
        self.container.columnconfigure(0, weight = 1)
        self.container.rowconfigure(0, weight = 1)

        # Create frames
        self.frames = {}
        self.frames['DataRecordForm'] = v.DataRecordForm(master = self.container,
                                                model = self.model, filename = PATH_FILE_EMPLOYEES)
        self.frames['DataListForm'] = v.DataListForm(master = self.container,
                                                     model = self.model)

        self.frames['CalendarForm'] = v.CalendarForm(master = self.container,
                                    filename = (PATH_FILE_SCHEDULE, PATH_FILE_EMPLOYEES))
        self._on_file_select(PATH_FILE_PATIENTS)
        self._sync_doct()
        

        self.frames['GrafForm'] = v.GrafForm(master = self.container, model = self.model,
                                             filename = (PATH_FILE_SCHEDULE,
                                                         PATH_FILE_EMPLOYEES),
                                             lst_data_common=self.lst_data_common)


        self.frames['DataRecordForm'].grid(column=0, row=0, sticky=("W, E, N, S"))
        self.frames['DataRecordForm'].columnconfigure(0, weight = 1)
        self.frames['DataRecordForm'].rowconfigure(0, weight = 1)

        self.frames['DataListForm'].grid(column=0, row=0, sticky=("W, E, N, S"))
        self.frames['DataListForm'].columnconfigure(0, weight = 1)
        self.frames['DataListForm'].rowconfigure(0, weight = 1)


        self.frames['CalendarForm'].grid(column=0, row=0, sticky=("W, E, N, S"))
        self.frames['CalendarForm'].columnconfigure(0, weight = 1)
        self.frames['CalendarForm'].rowconfigure(0, weight = 1)

        self.frames['GrafForm'].grid(column=0, row=0, sticky=("W, E, N, S"))
        self.frames['GrafForm'].columnconfigure(0, weight = 1)
        self.frames['GrafForm'].rowconfigure(0, weight = 1)

        self.statusbar_frame = v.StatusBar(self)
        self.statusbar_frame.setStatusBar('Ready....')
        self.records_saved = 0
        self.show_frame()
        self._read_sch_pat()
        self._view_happy_bithday()
        self._sync_doct()
        # show the window
        splash.destroy()
        self.deiconify()

    def show_frame(self, *_):
        # Показывает выбранный фрэйм
        value = self.toolbar.value_item.get()
        frame = self.frames[value]
        frame.tkraise()

    def _status_update(self, *_):
        # Обновление статусбара
        text = self.statusbar_frame.status_text
        self.statusbar_frame.setStatusBar(text)

    def _quit(self):
        self.destroy()
        self.quit()

    def update_text_info(self):
        # Обновление надписей на фрэймах
        self.toolbar.text_info_1.set(
            self.model._model_data['Все записи'].get())
        self.toolbar.text_info_2.set(
            self.model._model_data['Добавлено запись'].get())

        if self.model.file is None:
            self.toolbar.text_info_5.set('')
        else:            
            self.toolbar.text_info_5.set(
                Path(PATH_FILE_PATIENTS).name)

        self.frames['DataRecordForm'].text_info_3.set(
                self.model._model_data['Реанимация'].get())
        self.frames['DataRecordForm'].text_info_4.set(
                self.model._model_data['Анестезиология'].get())
        self.frames['DataRecordForm'].text_info_6.set(
                '' if self.frames['DataRecordForm'].current_record==None
                else self.frames['DataRecordForm'].current_record)
        self.frames['DataListForm'].text_info_3.set(
                self.model._model_data['Реанимация'].get())
        self.frames['DataListForm'].text_info_4.set(
                self.model._model_data['Анестезиология'].get())

    def _employees(self, event):
        e.main(Data.EMPLOYEES)

    def _view_happy_bithday(self):
        lst_hb = [(datetime.strptime(r['birthday'],'%d.%m.%Y'),
                   r['famili_IO']) for r in EMPLOYEES]
        now=datetime.now()
        lst_td_hb = []
        for hb in lst_hb:
            delta1 = datetime(now.year, hb[0].month, hb[0].day)
            delta2 = datetime(now.year+1, hb[0].month, hb[0].day)
            if delta1 > now:
                time_diff = (delta1 - now).days
            else:
                time_diff = (delta2 - now).days

            lst_td_hb.append((time_diff, hb[0], hb[1]))

        if lst_td_hb:
            min_time_diff, _, _ =min(lst_td_hb)
            index_min_td = [(x[0], x[1], x[2]) for x in lst_td_hb if x[0] == min_time_diff]
            lst_fio_hb = [ x[2] for x in index_min_td]
            d_m_hb =datetime.strftime(index_min_td[0][1],'%d / %m')
            fio_hb_string = ', '.join(lst_fio_hb)
            self.toolbar.text_info_6.set(f'Осталось {min_time_diff+1} дней:  {d_m_hb}  {fio_hb_string}')


    def _sync_doct(self):
        sch = self.frames['CalendarForm'].get_schedule_all_days()
        empl = list(dct['famili_IO'] for dct in EMPLOYEES if dct['status']=='Врач')
        rows, _ = self.model.current_model
        self.lst_data_common = []
        
        for emp in empl:
            lst_sch_doct = []
            lst_rean_work_doct = []
            lst_anest_work_doct = []
            for line in sch.items():
                if [x for x in line[1] if x[0]==emp]:
                    work_day = tuple (x for x in line[1] if x[0]==emp)
                    lst_sch_doct.append((work_day, line[0]))

            for row in rows:
                date_start = datetime.strptime((row['Дата поступления']+
                                row['Время поступления']),"%d.%m.%y%H:%M")
                if row['Анестезиолог']==emp:
                    lst_anest_work_doct.append((row['Отделение'], date_start,
                                        row['Вр_опер'], row['Вид обезболивания']))
                elif row['Реаниматолог']==emp:
                    lst_rean_work_doct.append((row['Кем направлен'], date_start))
                

            Doc = w.Doctor(name = emp, schedule_doct = lst_sch_doct,
                    anest_work_doct = lst_anest_work_doct,
                    rean_work_doct = lst_rean_work_doct)

            self.lst_data_common.append(Doc)

        lst_time_death = []
        for row in rows:
            if row['Смерть']=='1':
                date_end = datetime.strptime((row['Дата выписки']+
                    row['Время выписки']),"%d.%m.%y%H:%M")
                lst_time_death.append(date_end)

        dct_doct_death=defaultdict(list)
        for t_d in lst_time_death:
            for line in sch.items():
                if ((line[0][0]<=t_d) and (line[0][1] > t_d)):
                    doct_death  = [x[0] for x in line[1] if x[1] == 'Сутки реанимация']
                    dct_doct_death[doct_death[0]].append(t_d)

        for dd in self.lst_data_common:
            dd.deaths=dct_doct_death[dd.name]

    def _read_sch_pat(self):
        self.statusbar_frame.setStatusBar('Синхронизация данных...', timeout= 2000)
        sch = self.frames['CalendarForm'].get_schedule_all_days()
        pat, _ = self.model.current_model                
        lst_doct_rean =  []
        lst_doct_anest =  []
        lst_sch_error = []
        for key, value in sch.items():
            lst_doct_rean.append(([k[0] for k in value if k[1] == 'Сутки реанимация'], key))
            lst_doct_anest.append(([k[0] for k in value if k[1] == 'Сутки анестезиология'], key))
        lst_dct_mounth = list(zip(lst_doct_rean,lst_doct_anest))
        for k,v in lst_dct_mounth:
            if (len(k[0])!=1 or len(v[0])!=1):
                lst_sch_error.append(str(k[1][0].date()))
            else:
                pass
        if len(lst_sch_error)>0:
            lst_sch_error.sort()
            string_lst_sch_error = ', '.join(lst_sch_error)
            messagebox.showerror('Warning !!!',f'Эти даты в экстренном графике заполнены неверно.\
                                                {string_lst_sch_error}')
            return False

        lst_date_pat=[]
        new_pat=[]
        flag=False
        for c,row in enumerate(pat):
            if row['Профиль']=='Реанимация':
                try:
                    date_start = datetime.strptime((row['Дата поступления']+
                                row['Время поступления']),"%d.%m.%y%H:%M")
                    date_end = datetime.strptime((row['Дата выписки']+
                                row['Время выписки']),"%d.%m.%y%H:%M")
                    date_pat=date_start, date_end
                    lst_date_pat.append(date_pat)
                    for doc, date in lst_doct_rean:
                        if (date[0]<=date_start and date[1]>date_start):
                            if row['Реаниматолог']!=doc[0]:
                                row['Реаниматолог']=doc[0]
                                flag=True
                except:
                    pass

            new_pat.append(row)
        
        if flag:
            result = messagebox.askyesno(
                title='Внимание !',
                message='Данные графика и пациентов требуют обновления. Перезаписать ?')
            if result:
                update_data = 'update'
                new_r = False
                for r in new_pat:
                    self.model.current_model = r, new_r, update_data
                self._on_save()
                flag=False
            else:
                pass
        
    def _new_record(self, *_):
        # Новая запись или редактирование существующей
        data, errors = self.frames['DataRecordForm']._get()
        if errors:
            self.statusbar_frame.setStatusBar(
            "Ошибка !!!   Пустые поля: {}"
            .format(', '.join(errors)))
            message = "Empty fields !!!"
            detail = "The following fields are empty: \n  * {}".format(
            '\n  * '.join(errors))
            messagebox.showwarning(
            title='Attention',
            message=message,
            detail=detail)
        update_data = 'new_data'
        row, _ = self.model.current_model
        
        rownum = len(row)
        if self.frames['DataRecordForm'].current_record is not None:
            rows, _ = self.model.current_model
            record = rows[self.frames['DataRecordForm'].current_record]
            result = messagebox.askyesno(
                title='Внимание !',
                message='Вы уверены, что хотите перезаписать данные ?')
            if result:
                update_data = 'upd_data'
                rownum = self.frames['DataRecordForm'].current_record
            else:
                return
        if update_data == 'upd_data' or update_data == 'new_data':
            self.frames['DataRecordForm'].add_tagged(rownum, update_data)
            self.frames['DataListForm'].add_tagged(rownum, update_data)
        self.model.current_model = data, rownum, update_data            
        self.frames['DataRecordForm'].current_record = None            
        self.update_text_info()

        self.records_saved += 1
        self.statusbar_frame.setStatusBar(
            "{} records saved this session".format(self.records_saved))
        self._populate_recordlist()

    def _reset(self, *_):
        self.frames['DataRecordForm'].reset()
        self.update_text_info()
        

    def _on_save(self, *_):
        # Сохраняет записи
        rownum = self.frames['DataRecordForm'].current_record # Выбрана ли строка
        data = self.model.current_model
        common_data, new_data = data # Общие данные, новые данные
        result = messagebox.askyesno(
            title='Подтвердить операцию',
            message='''Записать данные в существующий файл?''')
        if result:
            if self.frames['DataListForm'].get_tagged():
                new_data.clear()
                data = common_data, new_data
            self.model.save_record(data, rownum)
            self.frames['DataRecordForm'].clear_tagged()
            self.frames['DataListForm'].clear_tagged()
            self._populate_recordlist()
        else: return False

        self.update_text_info()

        self.records_saved += 1
        self.statusbar_frame.setStatusBar(
            "{} records saved this session".format(self.records_saved))

    def initializeTk(self):
        # Initialize platform-specific options
        if sys.platform == 'mac':
            self.__initializeTk_mac()
        elif sys.platform == 'win32':
            self.__initializeTk_win32()
        else:
            self.__initializeTk_unix()

    def __initializeTk_colors_common(self):

        s = ttk.Style()
        s.theme_use('clam')

        s.map('main1.Toolbutton', background=[('selected', 'gray35'),
            ('active','gray75'),('!disabled',"white")])

        s.map('main2.Toolbutton', background=[('selected', 'gray35'),
            ('active','khaki'),('!disabled',"gray75")])
        s.configure('main2.Toolbutton', font=('Arial', 12, 'bold'))
        s.configure('Treeview.Heading', background='PowderBlue', font=('Arial', 8 ))


    def __initializeTk_win32(self):
        self.__initializeTk_colors_common()
        
    def __initializeTk_mac(self):
        self.__initializeTk_colors_common()

    def __initializeTk_unix(self):
        self.__initializeTk_colors_common()

    def _on_file_select(self, filename):

            update_data = 'current'
            self.model = m.CSVModel(filename=filename)
            records = self.model.get_all_records()
            new_r = False
            for row in records:
                self.model.current_model = row, new_r, update_data
            self._populate_recordlist()
            self.toolbar.text_info_2.set('0')
            self.update_text_info()
            
 
    def _populate_recordlist(self):
        # заполнение таблицы
        try:
            rows, _ = self.model.current_model
        except Exception as e:
            messagebox.showerror(
                title='Error',
                message='Problem reading file',
                detail=str(e)
            )
        else:
            self.frames['DataRecordForm'].populate_data(rows)
            self.frames['DataRecordForm'].get_autocompect_data(rows)
            self.frames['DataListForm'].populate_data_list(rows)


    def _open_record(self, *_):
        # Загружает выбранную строку по id
        if self.toolbar.value_item.get()=='DataRecordForm':
            rowkey = self.frames['DataRecordForm'].open_record_tree()
        else:
            rowkey = self.frames['DataListForm'].open_record_tree()
            self.toolbar.value_item.set('DataRecordForm')
            self.show_frame()
            
            
        rows, new = self.model.current_model
        if rowkey is not None:
            record = rows[rowkey]
        else: return False
        self.frames['DataRecordForm'].load_record(rowkey, record)
        

