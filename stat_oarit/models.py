import csv
from pathlib import Path
import os
import json
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog


class CSVModel:
    """CSV file storage"""


    def __init__(self, filename=None):

        self.fields = {
            'Профиль': tk.StringVar(),
            'Номер истории': tk.StringVar(),
            'Ф.И.О. больного': tk.StringVar(),
            'Пол': tk.StringVar(),
            'Возраст': tk.StringVar(),
            'Дата поступления': tk.StringVar(),
            'Время поступления': tk.StringVar(),
            'Дата выписки': tk.StringVar(),
            'Время выписки': tk.StringVar(),
            'Длительность': tk.StringVar(),
            'Адрес': tk.StringVar(),
            'Место работы': tk.StringVar(),
            'Диагноз при поступлении': tk.StringVar(),
            'Кем направлен': tk.StringVar(),
            'Перевод': tk.StringVar(),
            'Смерть': tk.StringVar(),
            'ХАИ': tk.StringVar(),
            'Covid19': tk.StringVar(),
            'ВИЧ': tk.StringVar(),
            'Реаниматолог': tk.StringVar(),
            'Отделение': tk.StringVar(),
            'Ангиооперационная': tk.StringVar(),
            'Операция': tk.StringVar(),
            'Вид обезболивания': tk.StringVar(),
            'Анестезиолог': tk.StringVar(),
            'Вр_опер': tk.StringVar()
            }

        self._model_data = {
            'Все записи': tk.StringVar(),
            'Анестезиология': tk.StringVar(),
            'Реанимация': tk.StringVar(),
            'Добавлено запись': tk.StringVar(),
            'Смерть': tk.StringVar()
            }
        {v.set('0') for v in self._model_data.values()}

        self.records_model = []
        self.records_new = []
        self.file = filename


    def save_record(self, data, rownum=None):
        """Записывает или перепысывает данные в файл CSV"""
        
        common_data, new_data = data
        if len(new_data) > 0:
            with open(self.file, 'a', encoding='cp1251', newline='') as fh:
                csvwriter = csv.DictWriter(fh, fieldnames=self.fields.keys(),
                                               extrasaction='raise')
        else:
            with open(self.file, 'w', encoding='cp1251', newline='') as fh:
                csvwriter = csv.DictWriter(fh, fieldnames=self.fields.keys(),
                                               extrasaction='raise')
                csvwriter.writeheader()
                csvwriter.writerows(common_data)


        self.records_new.clear()
        self._model_data['Добавлено запись'].set(len(self.records_new))                
 
    def get_all_records(self):
        """Получает все записи из CSV файла"""
        if not Path(self.file).exists():
            return []

        with open(self.file, 'r', encoding='cp1251') as fh:
            csvreader = csv.DictReader(fh.readlines())
            missing_fields = set(self.fields.keys()) - set(csvreader.fieldnames)
            if len(missing_fields) > 0:
                fields_string = ', '.join(missing_fields)
                raise Exception(f"File is missing fields: {fields_string}")
            records = list(csvreader)
        return records


    def get_record(self, rownum):
        """Get a single record by row number

        Callling code should catch IndexError
        in case of a bad rownum.
        """
        return self.get_all_records()[rownum]

    @property
    def current_model(self):
        return self.records_model, self.records_new
    @current_model.setter
    def current_model(self, data_tuple):
        data, rownum, update_data = data_tuple

        common_data = {**self.fields, **data}
        current_data = {key : (value if key in data else '')
                        for key, value in common_data.items()}

        if update_data == 'current':
            self.records_model.append(current_data)
            if current_data['Профиль'] == 'Реанимация':
                self._model_data['Реанимация'].set((
                int(self._model_data['Реанимация'].get())+1))
            else:
                self._model_data['Анестезиология'].set((
                int(self._model_data['Анестезиология'].get())+1))
        elif update_data == 'upd_data':
            self.records_model[rownum]=current_data
        elif update_data == 'new_data':
            self.records_new.append(current_data)
            self.records_model.append(current_data)
            self._model_data['Добавлено запись'].set(str(
                int(self._model_data['Добавлено запись'].get())+1))
            if current_data['Профиль'] == 'Реанимация':
                self._model_data['Реанимация'].set((
                int(self._model_data['Реанимация'].get())+1))
            else:
                self._model_data['Анестезиология'].set((
                int(self._model_data['Анестезиология'].get())+1))

        self._model_data['Все записи'].set(len(self.records_model))




