import os, sys
from pathlib import Path
from tkinter import messagebox
from tkinter import filedialog
from tkinter.ttk import Style
from tkinter import Menu
import csv

import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as mb
import re
from . import myWidgets as w


def required(value, message):
    if not value:
        raise ValueError(message)
    return value

path_employees = ''


FIELDS = ['famili', 'first_name', 'last_name',
          'phone', 'status', 'birthday', 'famili_IO']

class Contact(object):

    def __init__(self, famili, first_name, last_name,
                 phone, status, birthday, famili_IO=None):
        self.famili = famili
        self.first_name = first_name
        self.last_name = last_name
        self.phone = phone
        self.status = status
        self.birthday = birthday
        self.famili_IO = (str(famili.title())+' '+str(first_name[0].upper())+'.'
                            +str(last_name[0].upper())+'.')
        
    @property
    def famili(self):
        return self._famili

    @famili.setter
    def famili(self, value):
        self._famili = required(value, "Фамилия не заполнена")

    @property
    def first_name(self):
        return self._first_name

    @first_name.setter
    def first_name(self, value):
        self._first_name = required(value, "Имя не заполнено")

    @property
    def last_name(self):
        return self._last_name

    @last_name.setter
    def last_name(self, value):
        self._last_name = required(value, "Отчество не заполнено")

    @property
    def phone(self):
        return self._phone

    @phone.setter
    def phone(self, value):
        self._phone = required(value, "Телефон не заполнен")

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        self._status = required(value, "Должность не заполнена")


class ContactList(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master)
        self.lb = tk.Listbox(self, **kwargs)
        scroll = tk.Scrollbar(self, command=self.lb.yview)

        self.lb.config(yscrollcommand=scroll.set)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.lb.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        

    def insert(self, contact, index=tk.END):
        text = "{}, {}".format(contact.famili, contact.first_name)
        self.lb.insert(index, text)

    def delete(self, index):
        self.lb.delete(index, index)

    def update(self, contact, index):
        self.delete(index)
        self.insert(contact, index)

    def bind_doble_click(self, callback):
        handler = lambda _: callback(self.lb.curselection()[0])
        self.lb.bind("<Double-Button-1>", handler)

class ContactForm(tk.LabelFrame):

    def __init__(self, master, **kwargs):
        super().__init__(master, text="Contact", padx=10, pady=10, **kwargs)
        self._vars_contacts = {
            "Фамилия": tk.StringVar(),
            "Имя": tk.StringVar(),
            "Отчество": tk.StringVar(),
            "Телефон": tk.StringVar(),
            "Должность": tk.StringVar(),
            "Дата рождения": tk.StringVar()
            }

        self.frame = tk.Frame(self)
        self.entries = list(map(self.create_field, enumerate(self._vars_contacts.keys())))
        self.frame.pack()
        

    def create_field(self, field):
        position, text = field
        label = ttk.Label(self.frame, text=text)
        if text in ("Фамилия", "Имя", "Отчество"):
            entry = w.MyEntryFIO(self.frame, width=25,
                        textvariable=self._vars_contacts[text])
        elif text in ("Дата рождения"):
            entry = w.MyDateEntry(self.frame, width=25,
                                       textvariable=self._vars_contacts[text],
                                     style = 'my.DateEntry', date_pattern = 'dd.mm.yyyy',
                      locale = 'ru_RU',state = "readonly",
                      mindate=None, maxdate = w.Calendar.date.today())
        elif text in ("Должность"):
            entry = ttk.Combobox(self.frame, values = ['Врач', 'Медсестра'], width=25)
        else:
            entry = ttk.Entry(self.frame, width=25)
        label.grid(row=position, column=0, pady=5)
        entry.grid(row=position, column=1, pady=5)
        return entry

    def load_details(self, contact):
        values = (contact.famili, contact.first_name, contact.last_name,
                  contact.phone, contact.status, contact.birthday)
        for entry, value in zip(self.entries, values):
            if isinstance (entry, w.MyDateEntry):
                entry.set_date(value)
            else:
                entry.delete(0, tk.END)
                entry.insert(0, value)

    def get_details(self):
        values = [e.get() for e in self.entries]
        try:
            return Contact(*values)
        except ValueError as e:
            mb.showerror("Validation error", str(e), parent=self)

    def clear(self):
        for entry in self.entries:
            entry.delete(0, tk.END)

class NewContact(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.contact = None
        self.form = ContactForm(self)
        self.btn_add = tk.Button(self, text="Confirm", command=self.confirm)
        self.form.pack(padx=10, pady=10)
        self.btn_add.pack(pady=10)
        self.resizable(False,False)

    def confirm(self):
        self.contact = self.form.get_details()
        if self.contact:
            self.destroy()

    def show(self):
        self.grab_set()
        self.wait_window()
        return self.contact

class UpdateContactForm(ContactForm):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.btn_save = tk.Button(self, text="Save")
        self.btn_delete = tk.Button(self, text="Delete")
        
        self.btn_save.pack(side=tk.RIGHT, ipadx=5, padx=5, pady=5)
        self.btn_delete.pack(side=tk.RIGHT, ipadx=5, padx=5, pady=5)

    def bind_save(self, callback):
        self.btn_save.config(command=callback)

    def bind_delete(self, callback):
        self.btn_delete.config(command=callback)



class ContactsView(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Сотрудники")
        self.list = ContactList(self, height=15)
        self.form = UpdateContactForm(self)
        self.btn_new = tk.Button(self, text="Add new contact")

        self.list.pack(side=tk.LEFT, padx=10, pady=10)
        self.form.pack(padx=10, pady=10)
        self.btn_new.pack(side=tk.BOTTOM, pady=5)
        self.resizable(False,False)

    def set_ctrl(self, ctrl):
        self.btn_new.config(command=ctrl.create_contact)
        self.list.bind_doble_click(ctrl.select_contact)
        self.form.bind_save(ctrl.update_contact)
        self.form.bind_delete(ctrl.delete_contact)

    def add_contact(self, contact):
        self.list.insert(contact)

    def update_contact(self, contact, index):
        self.list.update(contact, index)

    def remove_contact(self, index):
        self.form.clear()
        self.list.delete(index)
        index = None

    def get_details(self):
        return self.form.get_details()

    def load_details(self, contact):
        self.form.load_details(contact)



class ContactsRepository(object):
    
    def __init__(self):
        UPDATE_CONTACTS = True
        self.contacts = self.load_contacts()
        print(f' === {self.contacts}')
        UPDATE_CONTACTS = False
        self.lastrowid = 0

    def upd_contacts(self, UPDATE_CONTACTS):
        if UPDATE_CONTACTS:
            self.contacts = self.load_contacts()
            UPDATE_CONTACTS = False
            

    def load_contacts(self):
        try:
            with open(path_employees, 'r', encoding='cp1251', newline='') as f:
                return [Contact(*r) for r in csv.reader(f) if r]
        except:
            pass

    def get_contacts(self):
        try:
            for row, contact in enumerate(self.contacts):
                contact.rowid = row
                yield contact
        except:
            pass

    def add_contact(self, contact):
        row_csv = (contact.famili, contact.first_name,
                   contact.last_name, contact.phone,
                   contact.status, contact.birthday, contact.famili_IO)
        contact.rowid = self.lastrowid + 1
        self.contacts.append(contact)
        with open(path_employees, 'a', encoding='cp1251', newline='') as f:
            csvwriter = csv.writer(f)
            csvwriter.writerow(row_csv)
        return contact
    def update_contact(self, contact):
        row_csv = (contact.famili, contact.first_name,
                   contact.last_name, contact.phone,
                   contact.status, contact.birthday, contact.famili_IO)

        update_cont_list = []
        for new_contact in self.contacts:
            new_row_csv = (new_contact.famili, new_contact.first_name,
                       new_contact.last_name, new_contact.phone,
                       new_contact.status, new_contact.birthday,
                       new_contact.famili_IO)
            if new_contact.rowid == contact.rowid:
                update_cont_list.append(row_csv)
            else:
                update_cont_list.append(new_row_csv)
        with open(path_employees, 'w', encoding='cp1251', newline='') as f:
            csvwriter = csv.writer(f)
            csvwriter.writerows(update_cont_list)
        return contact
    def delete_contact(self, contact):
        row_csv = (contact.famili, contact.first_name,
                   contact.last_name, contact.phone,
                   contact.status, contact.birthday, contact.famili_IO)

        update_cont_list = []
        for new_contact in self.contacts:
            new_row_csv = (new_contact.famili, new_contact.first_name,
                       new_contact.last_name, new_contact.phone,
                       new_contact.status, new_contact.birthday,
                       new_contact.famili_IO)
            if new_contact.rowid == contact.rowid:
                continue
            else:
                update_cont_list.append(new_row_csv)
        with open(path_employees, 'w', encoding='cp1251', newline='') as f:
            csvwriter = csv.writer(f)
            csvwriter.writerows(update_cont_list)
        return contact

    

class ContactsController(object):
    def __init__(self, repo, view):
        self.repo = repo
        self.view = view
        self.selection = None
        self.contacts = list(repo.get_contacts())

    def create_contact(self):
        new_contact = NewContact(self.view).show()
        if new_contact:
            contact = self.repo.add_contact(new_contact)
            self.contacts.append(contact)
            self.view.add_contact(contact)
            self.repo.upd_contacts(UPDATE_CONTACTS = True)
            self.contacts = list(self.repo.get_contacts())


    def select_contact(self, index):
        self.selection = index
        contact = self.contacts[index]
        self.view.load_details(contact)

    def update_contact(self):
        if not self.selection:
            return
        rowid = self.contacts[self.selection].rowid
        update_contact = self.view.get_details()
        update_contact.rowid = rowid
        contact = self.repo.update_contact(update_contact)
        self.contacts[self.selection] = contact
        self.view.update_contact(contact, self.selection)
        self.repo.upd_contacts(UPDATE_CONTACTS = True)
        self.contacts = list(self.repo.get_contacts())
    
    def delete_contact(self):
        if not self.selection:
            return
        contact = self.contacts[self.selection]
        self.repo.delete_contact(contact)
        self.view.remove_contact(self.selection)
        self.repo.upd_contacts(UPDATE_CONTACTS = True)
        self.contacts = list(self.repo.get_contacts())

    def start(self):
        for c in self.contacts:
            self.view.add_contact(c)
        self.view.mainloop()



def main(PATH_FILE_EMPLOYEES):
        global path_employees
        path_employees = PATH_FILE_EMPLOYEES
        view = ContactsView()
        repo = ContactsRepository()
        ctrl = ContactsController(repo, view)

        view.set_ctrl(ctrl)
        ctrl.start()



if __name__ == "__main__":
    main()



        
