import csv
import sqlite3

from PyQt5.QtSql import QSqlDatabase, QSqlTableModel
from PyQt5.QtWidgets import QFileDialog


class database_work:
    def create_sqlfile(self):                       # создаем БД
        con = sqlite3.connect("sensor.db")
        cur = con.cursor()
        cur.execute("""CREATE TABLE sensor_znach (
                                date  NOT NULL,
                                time  NOT NULL,
                                temp  NOT NULL,
                                humi  NOT NULL
                                );""")
        cur.execute("""CREATE TABLE settings (
                                id    INTEGER UNIQUE
                                      PRIMARY KEY,
                                znach INTEGER
                                );""")
        cur.execute("INSERT INTO settings(id,znach) VALUES(?,?)", (1, 0))
        con.commit()
        con.close()

    def update_table_sql(self):                       # обновляем таблицу с БД в приложении
        self.view_sql.reset()
        db = QSqlDatabase.addDatabase('QSQLITE')
        db.setDatabaseName('sensor.db')
        db.open()
        model = QSqlTableModel(self, db)
        model.setTable('sensor_znach')
        model.select()
        self.view_sql.setModel(model)
        self.statusBar().showMessage(f"Таблица обновлена")

    def settings(self, write=False, znach=0):         # берем или записываем настройки в БД
        if write:
            con = sqlite3.connect("sensor.db")
            cur = con.cursor()
            cur.execute("UPDATE settings SET znach = ? WHERE id = 1", (znach, ))
            con.commit()
            con.close()

        else:
            con = sqlite3.connect("sensor.db")
            cur = con.cursor()
            data = cur.execute("""SELECT znach FROM settings
                            WHERE id = 1""").fetchone()
            print(data)
            znach = int(data[0])
            if znach:
                self.temp_faringate()
            else:
                self.temp_celsium()
            con.close()
    def delete_table_sql(self):                        # очищаем БД
        con = sqlite3.connect("sensor.db")
        cur = con.cursor()
        cur.execute('DELETE from sensor_znach')
        con.commit()
        con.close()
        self.statusBar().showMessage(f"База данных очищена")
        self.update_table_sql()

    def saveFileDialog(self):                           # вызов окна сохранение файла
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getSaveFileName(self, "QFileDialog.getSaveFileName()", "",
                                                  "All Files (*);;Csv Files (*.csv)", options=options)
        if filename:
            self.saveFile(filename)

    def saveFile(self, filename):                       # экспортируем значения из БД в csv файл
        con = sqlite3.connect("sensor.db")
        cur = con.cursor()
        cur.execute("select * from sensor_znach")
        with open(filename, mode="x", newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow([i[0] for i in cur.description])
            csv_writer.writerows(cur)
            file = filename.split("/")[-1]
            self.statusBar().showMessage(f"Сохранен файл: {file}")

    def add_sql(self, date, time, temp, humi):          # добавляем запись в БД
        con = sqlite3.connect("sensor.db")
        cur = con.cursor()
        cur.execute('INSERT INTO sensor_znach(date, time, temp, humi) VALUES (?, ?, ?, ?)', (date, time, temp, humi))
        con.commit()
        con.close()
