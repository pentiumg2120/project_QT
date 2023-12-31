import os
import sys
from datetime import datetime

from PyQt5.QtCore import Qt, QIODevice
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QLabel

# Отдельные файлы
from database_work import database_work
from program_interface import Ui_mainWindow

# Запуск COM порта
serial_sensor = QSerialPort()
serial_sensor.setBaudRate(115200)

# Класс программы
class Program(QMainWindow, Ui_mainWindow, database_work):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowIcon(QIcon('utka.ico'))         # задаем иконку основному окну

        self.pic_pixmap = QPixmap('utka.ico')               # загружаем изображение утки
        self.pic = QDialog(self)                            # создаём диалоговое окно для утки
        self.pic.setWindowTitle("ВО СЛАВУ УТКЕ!")
        self.pic.setWindowIcon(QIcon('utka.ico'))           # задаем иконку диалоговому окну
        self.pic.setGeometry(0, 0, 250, 250)                # задаем размер диалоговому окну

        self.label_pic = QLabel(self.pic)                   # создаем надпись в диалоге
        self.label_pic.setPixmap(self.pic_pixmap)           # прикрепляем изображение к надписи
        self.label_pic.setAlignment(Qt.AlignCenter)         # выравниваем картинку

        # Подготовка COM порта
        self.serial_list_update()
        serial_sensor.readyRead.connect(self.serial_read)

        # Обработка нажатий на кнопки
        self.duck_button.clicked.connect(self.duck)
        self.serial_sensor_open.clicked.connect(self.serial_open)
        self.serial_sensor_close.clicked.connect(self.serial_close)
        self.serial_sensor_update.clicked.connect(self.serial_list_update)
        self.table_update.clicked.connect(self.update_table_sql)
        self.table_delete.clicked.connect(self.delete_table_sql)
        self.export_history.clicked.connect(self.saveFileDialog)
        self.action_celsium.triggered.connect(self.temp_celsium)
        self.action_faringate.triggered.connect(self.temp_faringate)

        # Проверка наличия файла базы данных
        if not os.path.isfile("sensor.db"):
            self.create_sqlfile()

        self.update_table_sql()             # Обновление таблицы
        self.settings()             # Получение настроек из БД

    def duck(self):
        self.pic.exec()

    def serial_list_update(self):           # Обновление списка COM портов
        portlist = []
        ports = QSerialPortInfo().availablePorts()
        for port in ports:
            portlist.append(port.portName())
        print(portlist)
        self.serial_sensor.clear()
        self.serial_sensor.addItems(portlist)
        self.statusBar().showMessage("Обновлен список портов")

    def serial_open(self):                  # Открытие COM порта
        if self.serial_sensor.currentText():
            serial_sensor.setPortName(self.serial_sensor.currentText())
            serial_sensor.open(QIODevice.ReadWrite)
            self.statusBar().showMessage(f"Открыт порт {self.serial_sensor.currentText()}")
        else:
            self.statusBar().showMessage("Не выбран COM порт")

    def serial_close(self):                 # Закрытие COM порта
        serial_sensor.close()
        self.statusBar().showMessage(f"Закрыт порт {self.serial_sensor.currentText()}")

    def serial_read(self):                  # Чтение с COM порта
        if not serial_sensor.canReadLine():
            return  # выходим если нечего читать
        rx = serial_sensor.readLine()
        rxs = str(rx, 'utf-8').strip()
        if rxs:
            data = rxs.split(',')
            print(data)
            if data[0] == "0":
                self.updateLCD(data[1], data[2])

# Обновление данных и прочая обработка
    def updateLCD(self, temp, humi):        # Обновление показателей на экране
        temp_float, humi_float = float(temp), float(humi)
        self.qt_temp.display(round(temp_float * self.temp_ratio, 2))
        self.qt_humi.display(humi_float)
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        current_day = now.strftime("%d/%m/%y")
        self.add_sql(current_day, current_time, str(temp_float), str(humi_float)) # Добавление показателей в БД
        self.update_table_sql()             # Обновление таблицы показателей
        print(current_time, current_day)

    def temp_celsium(self):                 # Пересчет температуры в градусы Цельсия
        self.temp_ratio = 1
        self.qt_temp_label.setText("Температура (°C)")
        self.settings(True, 0)

    def temp_faringate(self):               # Пересчет температуры в градусы Фарингейты
        self.temp_ratio = 1.8
        self.qt_temp_label.setText("Температура (F)")
        self.settings(True, 1)

    def closeEvent(self, event):            # Закрытие БД при закрытии приложения (во избежание потери данных)
        self.con.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Program()
    ex.show()
    sys.exit(app.exec_())
