from tkinter import *
from tkinter import ttk
import sqlite3
from datetime import datetime


class DbClass():
    def __init__(self, db="mydb.db") -> None:
        self.conn = sqlite3.connect(db)
        self.curs = self.conn.cursor()

    def __del__(self):
        self.conn.close()

    def create_tb(self, tb_name="timetable"):
        create_table_statement = \
            f'''
        CREATE TABLE IF NOT EXISTS {tb_name} (
            be_num text,
            time float,
            year text,
            month text,
            timestamp datetime default current_timestamp,
            primary key(be_num, year, month)
        )
        '''
        self.curs.execute(create_table_statement)
        self.conn.commit()

    def insert_tb(self, year, month, project_number, time=0, tb_name="timetable"):
        if project_number != "":
            month_dic = {
                1: "jan", 2: "feb", 3: "mar", 4: "apr", 5: "may", 6: "jun",
                7: "jul", 8: "aug", 9: "sep", 10: "oct", 11: "nov", 12: "dec"
            }
            month = month_dic[month]
            select_statement = \
                f'''
            SELECT time
            FROM {tb_name} WHERE year = '{year}' AND month = '{month}' AND be_num = '{project_number}'
            '''

            self.curs.execute(select_statement)
            result = self.curs.fetchone()
            pre_time = 0 if result is None else float(result[0])

            time += pre_time
            insert_statement = \
                f'''
            INSERT OR REPLACE INTO {tb_name}(
                be_num,
                time,
                year,
                month
            )
            VALUES 
                ('{project_number}', {time}, '{year}', '{month}')
            '''
            self.curs.execute(insert_statement)
            self.conn.commit()
        else:
            label.insert("end", "\n\nplease enter a BE number\n\n")

    def get_content(self, year="", month="", project_number="", tb_name="timetable"):
        # month_dic={
        #         0:"jan", 1:"feb", 2:"mar", 3:"apr", 4:"may", 5:"jun",
        #         5:"jul", 6:"aug", 7:"sep", 8:"oct", 9:"nov", 10:"dec"
        #            }
        # month = month_dic[month]
        searches = {"be_num": project_number, "month": month, "year": year}

        select_statement = \
            '''
        SELECT time'''
        select_statement_2 = \
            f'''
        FROM {tb_name} WHERE'''
        keyList = []
        for key in searches.keys():
            keyList.append(key)
            select_statement += f", {key}" if searches[key] == "" else ""
            select_statement_2 += f" {key} = '{str(searches[key])}' AND" if not searches[key] == "" else ""

        select_statement += select_statement_2[:-2] if select_statement.endswith(
            "AND") else select_statement_2[:-4]
        # """
        # example:
        # SELECT time, year, month, be_num
        # FROM timetable
        # """

        curs = self.curs.execute(select_statement)
        result = self.curs.fetchall()
        res = []
        formated_result = "SELECT "
        if year == "" and month == "" and project_number == "":
            formated_result += f"'*' FROM {tb_name}:\n"
        else:
            if year != "":
                if not formated_result.endswith("\n"):
                    formated_result += f"'year':'{year}' FROM {tb_name}:\n"
                else:
                    formated_result = formated_result[:-3-len(
                        tb_name)] + f"'year':'{year}' FROM {tb_name}:\n"
            if month != "":
                if not formated_result.endswith("\n"):
                    formated_result += f"'month':'{month}' FROM {tb_name}:\n"
                else:
                    formated_result = formated_result[:-3-len(
                        tb_name)] + f", 'month':'{month}' FROM {tb_name}:\n"
            if project_number != "":
                if not formated_result.endswith("\n"):
                    formated_result += f"'be_num':'{project_number}' FROM {tb_name}:\n"
                else:
                    formated_result = formated_result[:-3-len(
                        tb_name)] + f", 'be_num':'{project_number}' FROM {tb_name}:\n"

        print(result)
        print(curs.description)
        if result:
            # if project_number != "":
            #     res.append({"be_num":project_number})
            # if year != "": res.append({"year":year})
            # if month != "": res.append({"month":month})
            for i, result_el in enumerate(result, 0):
                for j, description in enumerate(curs.description, 0):
                    if description[j] != None:
                        res.append({})
                    res[i][description[0]] = result_el[j]
            for i, _ in enumerate(res, 0):
                formated_result += "\t" + str(res[i]) + "\n"

        return {"not formated": result, "formated": formated_result}

    def get_all_content(self, search, sort="DESC", tb_name="timetable"):
        select_statement = \
            f'''
        SELECT {search}
        FROM {tb_name} ORDER BY timestamp {sort}'''
        curs = self.curs.execute(select_statement)
        result = self.curs.fetchall()
        res = {}
        formated_result = ""
        if result:
            for i, description in enumerate(curs.description, 0):
                res[description[0]] = result[i]
        for i in res.items():
            formated_result += str(i)+"\n"
        return {"not formated": result, "formated": formated_result}


# Create an instance of Tkinter frame

win = Tk()

# Set the geometry of Tkinter frame
# win.geometry("583x591+468+158")
win.configure(borderwidth="1")

db = DbClass()
db.create_tb()


# db.get_all_content()

def insert_time():
    global time_entry
    global be_entry
    time_str = time_entry.get()
    time = int(time_str) if time_str != "" else 0
    project_number = be_entry.get()

    currentMonth = datetime.now().month
    currentYear = datetime.now().year
    db.insert_tb(currentYear, currentMonth, project_number, time)


def gettime():
    global be_entry
    # time_str = time_entry.get()
    # time = int(time_str) if time_str != "" else 0
    project_number = be_entry.get()
    year = year_entry.get()
    month = month_entry.get()
    project_number = be_entry.get()

    label.insert("end", db.get_content(
        year=year, month=month, project_number=project_number)["formated"])


def refresh(event):
    global be_entry
    project_number = be_entry.get()

    if project_number != "":
        for i, be_el in enumerate(be_list, 0):
            if project_number in be_el:
                del be_list[i]
        be_list.insert(0, project_number)
        be_entry['values'] = be_list


def refresh_searcher(event):
    global month_entry
    month = month_entry.get()

    if month != "":
        for i, month_el in enumerate(month_list, 0):
            if month in month_el:
                del month_list[i]
        month_list.insert(0, month)
        month_entry['values'] = month_list
# Initialize a Label to display the User Input


be_lable = Label(win, width=40, text="BE:", font=("Courier 10 bold"))
be_lable.grid(row=0, column=0, sticky=W)

be_list = db.get_all_content("be_num")["not formated"]
be_entry = ttk.Combobox(win, values=(be_list), width=50)
be_entry.grid(row=0, column=1, sticky=W)

# be_entry= Entry(win, width=50)
# be_entry.grid(row=0, column=1, sticky=W)

time_lable = Label(win, width=40, text="time:", font=("Courier 10 bold"))
time_lable.grid(row=1, column=0, sticky=W)

time_entry = Entry(win, width=50)
time_entry.grid(row=1, column=1, sticky=W)


month_lable = Label(win, width=20, text="month:", font=("Courier 10 bold"))
month_lable.grid(row=0, column=3, sticky=W)

month_list = ["jan", "feb", "mar", "apr", "may",
              "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
month_entry = ttk.Combobox(win, width=20, values=(month_list))
month_entry.grid(row=0, column=4, sticky=W)
month_entry.bind('<FocusIn>', refresh_searcher)

year_lable = Label(win, width=20, text="year:", font=("Courier 10 bold"))
year_lable.grid(row=0, column=5, sticky=W)

year_list = db.get_all_content("year")["not formated"]
year_entry = ttk.Combobox(win, width=20, values=(year_list))
year_entry.grid(row=0, column=6, sticky=W)
year_entry.bind('<FocusIn>', refresh_searcher)

set_time_button = ttk.Button(
    win, text="Set time", width=20, command=insert_time)
set_time_button.grid(row=2, column=0, sticky=EW)
set_time_button.bind('<Button-1>', refresh)
ttk.Button(win, text="Get time", width=20, command=gettime).grid(
    row=2, column=1, sticky=EW)

label = Text(win, font=("Courier 15 bold"))
label.insert("end", "Info:\n")
label.grid(row=3, columnspan=300, sticky=EW)

win.mainloop()
