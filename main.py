import sqlite3
import sys
import requests
import webbrowser
from MainWindow import *

from PyQt5.QtWidgets import QWidget, QColorDialog, QTableWidgetItem, QSizeGrip
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QPushButton
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QPropertyAnimation
import pyqtgraph

import datetime

import pandas_datareader.data

pyqtgraph.setConfigOption('background', '#f0f0f0')
pyqtgraph.setConfigOption('foreground', '#000')

WINDOW_SIZE = 0

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.available_currencies = list()
        self.the_date = datetime.date.today()
        self.graphicsView.setAxisItems({'bottom': pyqtgraph.DateAxisItem()})
        self.initUI()

    def initUI(self):
        self.setWindowTitle('RateX')
        self.setWindowIcon(QtGui.QIcon(":/images/assets/icon.png"))

        self.setWindowFlags(Qt.FramelessWindowHint)

        self.minimizeButton.clicked.connect(lambda: self.showMinimized())
        self.restoreButton.clicked.connect(lambda: self.restore_or_maximize_window())
        self.closeButton.clicked.connect(lambda: self.close())

        self.X.clicked.connect(lambda: self.close())

        self.menuButton.clicked.connect(lambda: self.slide_left_menu())
        self.rightButtonMenu.clicked.connect(lambda: self.slide_right_menu())

        self.stackedWidget.setCurrentWidget(self.CurrencyRateCharts_page)

        self.Rate.clicked.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.CurrencyRateCharts_page))
        self.Rate.clicked.connect(self.apply_button_style_rate)

        self.CurrencyRateCharts_button.clicked.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.CurrencyRateCharts_page))
        self.CurrencyConverter_button.clicked.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.CurrencyConverter_page))
        self.Suggestions_button.clicked.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.Suggestions_page))

        for button in self.left_side_menu.findChildren(QPushButton):
            button.clicked.connect(self.apply_button_style)

        self.menuButton.clicked.connect(self.apply_menu_button_style)
        self.rightButtonMenu.clicked.connect(self.apply_right_button_menu_style)

        QSizeGrip(self.size_grip)

        self.overheader.mouseMoveEvent = self.move_window

        self.input.setPlaceholderText('I HAVE')
        self.output.setPlaceholderText('I WANT TO BUY')

        self.convert.clicked.connect(self.converting)

        con = sqlite3.connect("db/currencies.db")
        cur = con.cursor()
        result = cur.execute("""SELECT currency FROM currencies""").fetchall()

        for elem in result:
            self.available_currencies.append(str(elem)[2:-3])
            self.currency_input.addItem(str(elem)[2:-3])
            self.currency_output.addItem(str(elem)[2:-3])
        con.close()

        self.swap.clicked.connect(self.swap_currencies)

        self.vk.clicked.connect(self.switch_to_vk)
        self.telegram.clicked.connect(self.switch_to_telegram)
        self.instagram.clicked.connect(self.switch_to_instagram)

        self.BuildAGraph.clicked.connect(self.plotting)

    def restore_or_maximize_window(self):
        global WINDOW_SIZE
        window_status = WINDOW_SIZE

        if window_status == 0:
            WINDOW_SIZE = 1
            self.showMaximized()
            self.restoreButton.setIcon(QtGui.QIcon("assets/restoreButtonMaximize.png"))
        else:
            WINDOW_SIZE = 0
            self.showNormal()
            self.restoreButton.setIcon(QtGui.QIcon("assets/restoreButton.png"))

    def mousePressEvent(self, event):
        self.clickPosition = event.globalPos()

    def move_window(self, e):
        if not self.isMaximized():
            if e.buttons() == Qt.LeftButton:
                self.move(self.pos() + e.globalPos() - self.clickPosition)
                self.clickPosition = e.globalPos()
                e.accept()

    def slide_left_menu(self):
        width = self.left_side_menu.width()
        if width == 50:
            new_width = 220
        else:
            new_width = 50

        self.animation = QPropertyAnimation(self.left_side_menu, b"minimumWidth")

        self.animation.setDuration(250)
        self.animation.setStartValue(width)
        self.animation.setEndValue(new_width)
        self.animation.setEasingCurve(QtCore.QEasingCurve.InOutQuart)

        self.animation.start()

    def slide_right_menu(self):
        width = self.right_side_menu.width()
        width_label = self.i_have_label.width()
        width_swap = self.swap.width()
        if width == 100:
            new_width = 240
            new_width_label = 140
            new_width_swap = 190
        else:
            new_width = 100
            new_width_label = 0
            new_width_swap = 50

        self.animation1 = QPropertyAnimation(self.right_side_menu, b"minimumWidth")

        self.animation1.setDuration(250)
        self.animation1.setStartValue(width)
        self.animation1.setEndValue(new_width)
        self.animation1.setEasingCurve(QtCore.QEasingCurve.InOutQuart)


        self.animation2 = QPropertyAnimation(self.i_have_label, b"minimumWidth")

        self.animation2.setDuration(250)
        self.animation2.setStartValue(width_label)
        self.animation2.setEndValue(new_width_label)
        self.animation2.setEasingCurve(QtCore.QEasingCurve.InOutQuart)


        self.animation3 = QPropertyAnimation(self.i_want_to_buy_label, b"minimumWidth")

        self.animation3.setDuration(250)
        self.animation3.setStartValue(width_label)
        self.animation3.setEndValue(new_width_label)
        self.animation3.setEasingCurve(QtCore.QEasingCurve.InOutQuart)

        self.animation4 = QPropertyAnimation(self.swap, b"minimumWidth")

        self.animation4.setDuration(250)
        self.animation4.setStartValue(width_swap)
        self.animation4.setEndValue(new_width_swap)
        self.animation4.setEasingCurve(QtCore.QEasingCurve.InOutQuart)

        self.animation1.start()
        self.animation2.start()
        self.animation3.start()
        self.animation4.start()

    def apply_button_style(self):
        for button in self.left_side_menu.findChildren(QPushButton):
            if button.objectName() != self.sender().objectName():
                default_style = button.styleSheet().replace("border-bottom: 2px solid rgb(0, 234, 153);", "")
                button.setStyleSheet(default_style)

        new_style = self.sender().styleSheet()[:14] + (
            "border-bottom: 2px solid rgb(0, 234, 153);") + self.sender().styleSheet()[14:]
        self.sender().setStyleSheet(new_style)

    def apply_button_style_rate(self):
        for button in self.left_side_menu.findChildren(QPushButton):
            if button.objectName() != self.CurrencyRateCharts_button.objectName():
                default_style = button.styleSheet().replace("border-bottom: 2px solid rgb(0, 234, 153);", "")
                button.setStyleSheet(default_style)

        new_style = self.CurrencyRateCharts_button.styleSheet()[:14] + (
            "border-bottom: 2px solid rgb(0, 234, 153);") + self.CurrencyRateCharts_button.styleSheet()[14:]
        self.CurrencyRateCharts_button.setStyleSheet(new_style)

    def apply_menu_button_style(self):
        if self.left_side_menu.width() == 220:
            new_style = ""
            self.menuButton.setStyleSheet(new_style)
        else:
            new_style = "border-top: 2px solid rgb(0, 234, 153);"
            self.menuButton.setStyleSheet(new_style)

    def apply_right_button_menu_style(self):
        if self.right_side_menu.width() == 240:
            new_style = self.rightButtonMenu.styleSheet().replace("border-top: 2px solid rgb(32, 225, 175);",
                                                                  "").replace(
                "border-bottom: 2px solid rgb(8, 176, 231);", "")
            self.rightButtonMenu.setStyleSheet(new_style)
        else:
            new_style = self.rightButtonMenu.styleSheet() + "border-top: 2px solid rgb(32, 225, 175);" + \
                        "border-bottom: 2px solid rgb(8, 176, 231);"
            self.rightButtonMenu.setStyleSheet(new_style)

    def converting(self):
        try:
            con = sqlite3.connect("db/currencies.db")
            cur = con.cursor()
            result = cur.execute("""SELECT * FROM currencies
                                                    WHERE currency = ? OR currency = ?""",
                                 (self.currency_output.currentText(), self.currency_input.currentText())).fetchall()
            first_elem_db = ()
            second_elem_db = ()
            for elem in result:
                if str(elem[3]) != str(self.the_date):
                    url = f"https://api.apilayer.com/fixer/convert?to=usd&from={elem[1]}&amount=1&"
                    payload = {}
                    headers = {"apikey": "TIYYefw0nJ2fbIWmhJVkMCaSgf22GiPv"}
                    response = requests.request("GET", url, headers=headers, data=payload)
                    status_code = response.status_code
                    if status_code == 200:
                        self.error_label.setText("")
                        result_text = response.text
                        con = sqlite3.connect("db/currencies.db")
                        cur = con.cursor()
                        cur.execute("""UPDATE currencies SET usd = ? WHERE currency = ?""",
                                    (float(result_text[result_text.find("result") + 9:result_text.find("result") + 9 + (
                                        result_text[result_text.find("result") + 9:].find("\n"))]),
                                     elem[1]))
                        cur.execute("""UPDATE currencies SET date = ? WHERE currency = ?""",
                                    (self.the_date, elem[1]))
                        con.commit()
                        second_result = cur.execute("""SELECT * FROM currencies WHERE currency = ?""",
                                                    (elem[1],)).fetchall()
                        for new_elem in second_result:
                            if new_elem[1] == self.currency_input.currentText():
                                first_elem_db = new_elem
                            else:
                                second_elem_db = new_elem
                        con.close()
                    elif status_code == 400:
                        self.error_label.setText("Bad Request")
                    elif status_code == 401:
                        self.error_label.setText("Unauthorized")
                    elif status_code == 404:
                        self.error_label.setText("Not Found")
                    elif status_code == 429:
                        self.error_label.setText("Too many requests")
                    elif status_code // 100 == 5:
                        self.error_label.setText("Server Error")
                else:
                    self.error_label.setText("")
                    if elem[1] == self.currency_input.currentText():
                        first_elem_db = elem
                    else:
                        second_elem_db = elem
            con.close()
            self.output.setText(
                str(round(float('.'.join(self.input.text().split(','))) * (first_elem_db[2] / second_elem_db[2]), 2)))
        except ValueError:
            if self.input.text():
                self.error_label.setText("Incorrect value!")
            else:
                self.error_label.setText("Enter value!")

    def swap_currencies(self):
        new_currency = self.currency_input.currentText()
        self.currency_input.setCurrentIndex(self.available_currencies.index(self.currency_output.currentText()))
        self.currency_output.setCurrentIndex(self.available_currencies.index(new_currency))

        new_text = self.input.text()
        self.input.setText(self.output.text())
        self.output.setText(new_text)

    @staticmethod
    def switch_to_vk(self):
        webbrowser.open('https://vk.com/spideydamn', new=2)

    @staticmethod
    def switch_to_telegram(self):
        webbrowser.open('https://t.me/spideydamn', new=2)

    @staticmethod
    def switch_to_instagram(self):
        webbrowser.open('https://www.instagram.com/spideydamnn/', new=2)

    def plotting(self):
        try:
            date_begin = self.dateEdit.dateTime().toString('yyyy-MM-dd')
            self.graphicsView.clear()
            df = pandas_datareader.data.DataReader(
                self.currency_input.currentText() + self.currency_output.currentText() + '=X', 'yahoo',
                start=date_begin,
                end=self.the_date)
            dates = [
                (datetime.datetime.strptime(str(i), '%Y-%m-%d %H:%M:%S') - datetime.datetime(1970, 1, 1,
                                                                                             5)).total_seconds()
                for i in df.index]
            self.graphicsView.plot(dates, df['Close'], pen='g')
        except pandas_datareader._utils.RemoteDataError:
            self.error_label_2.setText("error")


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec_())