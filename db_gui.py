import sys
import sqlite3
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QTableWidgetItem
from matplotlib import pyplot as plt
from ui_db_gui import Ui_MainWindow


class Example(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.initUI()
        self.ui.Show_Button.clicked.connect(self.button_get)
        self.ui.Add_text_btn.clicked.connect(self.button_add)
        self.ui.Del_Button.clicked.connect(self.button_del)
        self.ui.plot_Button.clicked.connect(self.button_plot)

    def initUI(self):
        global cursor
        connection = sqlite3.connect(":memory:")
        cursor = connection.cursor()
        self.input_to_mydb("create_db.sql")
        self.input_to_mydb("petshop.sql")

        cursor.execute("SELECT name FROM sqlite_master WHERE type ='table'")
        tables = cursor.fetchall()

        for elements in tables:
            self.ui.list_tables.addItem(elements[0])

    def input_to_mydb(self, name_file):
        sql_lite = open(name_file)
        sql_as_string = sql_lite.read()
        cursor.executescript(sql_as_string)

    def button_get(self):
        name_tbl =self.ui.list_tables.currentText()
        cursor.execute(f"SELECT * FROM {name_tbl}")
        self.put_data_to_table()

    def put_data_to_table(self):
        self.ui.data_here.clear()
        tbl_data = cursor.fetchall()
        num = len(tbl_data[0])

        self.ui.data_here.setRowCount(len(tbl_data))
        self.ui.data_here.setColumnCount(num)

        for col in range(num):
            for row, el in enumerate(tbl_data):
                to_cell = QTableWidgetItem(str(el[col]))
                self.ui.data_here.setItem(row,col,to_cell)

        return tbl_data

    def button_add(self):
        name_tbl =self.ui.list_tables.currentText()
        text_add = self.ui.lineEdit.text()

        cursor.execute(f"PRAGMA table_info({name_tbl})")
        tbl_info = cursor.fetchall()

        print(tbl_info)
        cursor.execute(f"SELECT MAX({tbl_info[0][1]}) FROM {name_tbl}")
        id_increase = cursor.fetchone()[0] + 1
        cursor.execute(f"INSERT INTO {name_tbl} ({tbl_info[0][1]},{tbl_info[1][1]}) VALUES ({id_increase}, '{text_add}')")

        self.ui.data_here.clear()
        cursor.execute(f"SELECT * FROM {name_tbl}")
        self.put_data_to_table()

    def button_del(self):
        try:
            item = self.ui.data_here.currentItem().text()
            name_tbl = self.ui.list_tables.currentText()
            cursor.execute(f"PRAGMA table_info({name_tbl})")
            tbl_info = cursor.fetchall()

            cursor.execute(f"DELETE FROM {name_tbl} WHERE {tbl_info[0][1]} = {item}")
            self.button_get()
        except Exception as err:
            err_win = QtWidgets.QMessageBox()
            err_win.setIcon(QtWidgets.QMessageBox.Warning)
            err_win.setText(str(err))
            err_win.setWindowTitle("Error")
            err_win.setStandardButtons(QtWidgets.QMessageBox.Ok)
            err_win.exec()

    def button_plot(self):
        cursor.execute(f"SELECT g.product_id, pch.purchase_price FROM purchases as pch,goods as g WHERE g.product_id = pch.product_id ")
        table_data = self.put_data_to_table()

        plt.xlabel('x = product_id')
        plt.ylabel('y = purchase_price')
        plt.title("Scatter график: Закупочные цены")

        x = []
        y = []

        for el in table_data:
            x.append(el[0])
            y.append(el[1])

        plt.scatter(x,y,label="Values")
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.legend(loc="best", fontsize=11)
        plt.tight_layout()
        plt.show()



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    application = Example()
    application.show()
    sys.exit(app.exec())