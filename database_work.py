import sqlite3
import csv
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel
from PyQt5.QtWidgets import QFileDialog


class database_work:
    def create_sqlfile(self):
        con = sqlite3.connect("sensor.db")
        cur = con.cursor()
        cur.execute("""CREATE TABLE sensor_znach (
                                date  NOT NULL,
                                time  NOT NULL,
                                temp  NOT NULL,
                                humi  NOT NULL
                                );""")
        con.commit()
        con.close()

    def update_table_sql(self):
        self.view_sql.reset()
        db = QSqlDatabase.addDatabase('QSQLITE')
        db.setDatabaseName('sensor.db')
        db.open()
        model = QSqlTableModel(self, db)
        model.setTable('sensor_znach')
        model.select()
        self.view_sql.setModel(model)
        self.statusBar().showMessage(f"Таблица обновлена")

    def delete_table_sql(self):
        con = sqlite3.connect("sensor.db")
        cur = con.cursor()
        cur.execute('DELETE from sensor_znach')
        con.commit()
        con.close()
        self.statusBar().showMessage(f"База данных очищена")
        self.update_table_sql()

    def saveFileDialog(self):
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getSaveFileName(self, "QFileDialog.getSaveFileName()", "",
                                                  "All Files (*);;Csv Files (*.csv)", options=options)
        if filename:
            self.saveFile(filename)

    def saveFile(self, filename):
        con = sqlite3.connect("sensor.db")
        cur = con.cursor()
        cur.execute("select * from sensor_znach")
        with open(filename, mode="x", newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow([i[0] for i in cur.description])  # write headers
            csv_writer.writerows(cur)
            file = filename.split("/")[-1]
            self.statusBar().showMessage(f"Сохранен файл: {file}")

    def add_sql(self, date, time, temp, humi):
        con = sqlite3.connect("sensor.db")
        cur = con.cursor()
        cur.execute('INSERT INTO sensor_znach(date, time, temp, humi) VALUES (?, ?, ?, ?)', (date, time, temp, humi))
        con.commit()
        con.close()
