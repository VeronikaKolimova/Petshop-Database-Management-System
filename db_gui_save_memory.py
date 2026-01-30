# db_gui_save_memory.py

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

        self.db_file = "petshop.db"
        self.connection = None
        self.cursor = None

        self.initUI()
        self.ui.Show_Button.clicked.connect(self.button_get)
        self.ui.Add_text_btn.clicked.connect(self.button_add)
        self.ui.Del_Button.clicked.connect(self.button_del)
        self.ui.plot_Button.clicked.connect(self.button_plot)
        self.ui.max_price_btn.clicked.connect(self.show_max_price)
        self.ui.sales_chart_btn.clicked.connect(self.show_sales_chart)

    def initUI(self):
        self.connection = sqlite3.connect(self.db_file)
        self.cursor = self.connection.cursor()

        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = self.cursor.fetchall()

        if not tables:
            self.input_to_mydb("create_db.sql")
            self.input_to_mydb("petshop.sql")
            self.connection.commit()

        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = self.cursor.fetchall()

        for table in tables:
            self.ui.list_tables.addItem(table[0])

    def input_to_mydb(self, filename):
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                sql_script = file.read()
                self.cursor.executescript(sql_script)
        except Exception as e:
            print(f"Error executing {filename}: {str(e)}")

    def button_get(self):
        try:
            name_tbl = self.ui.list_tables.currentText()
            if name_tbl:
                self.cursor.execute(f"SELECT * FROM {name_tbl}")
                self.put_data_to_table()
        except Exception as e:
            self.show_error(str(e))

    def put_data_to_table(self):
        try:
            self.ui.data_here.clear()
            tbl_data = self.cursor.fetchall()

            if not tbl_data:
                return

            num_columns = len(tbl_data[0])
            self.ui.data_here.setRowCount(len(tbl_data))
            self.ui.data_here.setColumnCount(num_columns)

            for row, row_data in enumerate(tbl_data):
                for col, cell_data in enumerate(row_data):
                    item = QTableWidgetItem(str(cell_data))
                    self.ui.data_here.setItem(row, col, item)

            return tbl_data
        except Exception as e:
            self.show_error(str(e))

    def button_add(self):
        try:
            name_tbl = self.ui.list_tables.currentText()
            text_add = self.ui.lineEdit.text().strip()

            if not name_tbl or not text_add:
                return

            self.cursor.execute(f"PRAGMA table_info({name_tbl})")
            tbl_info = self.cursor.fetchall()

            if len(tbl_info) < 2:
                self.show_error("Table structure error")
                return

            id_column = tbl_info[0][1]
            self.cursor.execute(f"SELECT MAX({id_column}) FROM {name_tbl}")
            max_id = self.cursor.fetchone()[0]
            new_id = (max_id or 0) + 1

            text_column = tbl_info[1][1]

            self.cursor.execute(
                f"INSERT INTO {name_tbl} ({id_column}, {text_column}) VALUES (?, ?)",
                (new_id, text_add)
            )
            self.connection.commit()

            self.button_get()
            self.ui.lineEdit.clear()

        except Exception as e:
            self.show_error(str(e))

    def button_del(self):
        try:
            current_item = self.ui.data_here.currentItem()
            if not current_item:
                return

            item_text = current_item.text()
            name_tbl = self.ui.list_tables.currentText()

            if not name_tbl:
                return

            self.cursor.execute(f"PRAGMA table_info({name_tbl})")
            tbl_info = self.cursor.fetchall()

            if not tbl_info:
                return

            id_column = tbl_info[0][1]

            self.cursor.execute(f"DELETE FROM {name_tbl} WHERE {id_column} = ?", (item_text,))
            self.connection.commit()

            self.button_get()

        except Exception as e:
            self.show_error(str(e))

    def show_max_price(self):
        try:
            self.cursor.execute("SELECT MAX(purchase_price) FROM purchases")
            max_price = self.cursor.fetchone()[0]

            if max_price is None:
                msg = "Нет данных о закупках."
            else:
                msg = f"Максимальная цена закупки: {max_price} руб."

            QtWidgets.QMessageBox.information(
                self,
                "Максимальная цена",
                msg,
                QtWidgets.QMessageBox.StandardButton.Ok)

        except Exception as err:
            QtWidgets.QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось получить максимальную цену:\n{str(err)}"
            )

    def button_plot(self):
        try:
            self.cursor.execute("""
                SELECT g.product_id, pch.purchase_price 
                FROM purchases as pch 
                JOIN goods as g ON g.product_id = pch.product_id 
            """)
            table_data = self.cursor.fetchall()

            if not table_data:
                self.show_error("No data for plotting")
                return

            plt.figure(figsize=(10, 6))
            plt.xlabel('Product ID')
            plt.ylabel('Purchase Price')

            x = [el[0] for el in table_data]
            y = [el[1] for el in table_data]

            plt.scatter(x, y, alpha=0.5)
            plt.title('Product Prices')
            plt.grid(True)
            plt.show()

        except Exception as e:
            self.show_error(str(e))

    def show_sales_chart(self):
        try:
            self.cursor.execute(""" 
                       SELECT g.product_id, sales.sale_price 
                       FROM sales  
                       JOIN goods AS g ON g.product_id = sales.product_id 
                       WHERE sales.sale_price IS NOT NULL AND sales.product_id > 180
                       ORDER BY g.product_id """)
            data = self.cursor.fetchall()

            product_id = [row[0] for row in data]
            sale_prices = [row[1] for row in data]

            plt.figure(figsize=(12, 7))
            bars = plt.bar( product_id, sale_prices, color='#4A90E2', edgecolor='black', linewidth=1.3, alpha=0.9 )

            plt.title('Диаграмма цен продаж по товарам', fontsize=16, fontweight='bold', pad=20)
            plt.xlabel('ID товара', fontsize=13, fontweight='bold')
            plt.ylabel('Цена продажи (₽)', fontsize=13, fontweight='bold')
            # Сетка по оси Y
            plt.grid(axis='y', linestyle='--', alpha=0.7, color='#aaaaaa')
            plt.xticks(product_id, rotation=45, fontsize=11)
            for bar in bars:
                height = bar.get_height()
                plt.text( bar.get_x() + bar.get_width() / 2, height + max(sale_prices) * 0.02,
                f'{int(height)}руб', ha='center', va='bottom', fontsize=11, fontweight='bold', color='#333333' )
            plt.tight_layout()
            plt.show()

        except Exception as err:
            QtWidgets.QMessageBox.critical(
                self,
                "Ошибка построения диаграммы",
                f"Не удалось построить диаграмму продаж:\n{str(err)}",
                QtWidgets.QMessageBox.StandardButton.Ok

            )

    def show_error(self, message):
        error_dialog = QtWidgets.QMessageBox()
        error_dialog.setIcon(QtWidgets.QMessageBox.Icon.Warning)
        error_dialog.setText(message)
        error_dialog.setWindowTitle("Error")
        error_dialog.exec()

    def closeEvent(self, event):
        if self.connection:
           self.connection.close()
        event.accept()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    application = Example()
    application.show()
    sys.exit(app.exec())

