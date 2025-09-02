import pandas as pd
import sys
import socket
from db_connect import *
from PyQt6.QtWidgets import QProgressDialog, QApplication, QMainWindow, QMessageBox, QFileDialog, QDialog, QTableWidgetItem, QCheckBox, QWidget, QHBoxLayout
from PyQt6.QtCore import Qt

from ui_pycode.main import Ui_Main

class Main(QMainWindow, Ui_Main):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.title = 'WhatsBot'
        self.setup_window()
        self.setup_buttons()
        

    def setup_window(self):
        self.setWindowTitle(self.title)


    def setup_buttons(self):
        self.btn_import.clicked.connect(self.select_excel_file)
        self.btn_start.clicked.connect(self.start_operation)
        self.btn_stop.clicked.connect(self.stop_operation)
        self.btn_info.clicked.connect(self.info)
        self.btn_github.clicked.connect(self.github)
        self.btn_export.clicked.connect(self.export_db)
        self.btn_delete.clicked.connect(self.clear_db)


    ############## IMPORT FROM EXCEL #####################
    ######################################################


    def select_excel_file(self):
        file_filter = "Excel Files (*.xlsx *.xls)"
        file_path, _ = QFileDialog.getOpenFileName(
            None,
            "Select Excel File",
            "",
            file_filter
        )
        if file_path:
            print("Selected file:", file_path)
        else:
            print("No file selected.")
        return file_path


    ############## START #################################
    ######################################################

    def start_operation(self):
        self.test('Test')


    ############## STOP ##################################
    ######################################################

    def stop_operation(self):
        self.test('Test')


    ############## ANOTHER BUTTONS #######################
    ######################################################

    def info(self):
        self.test('Test')

    def github(self):
        self.test('Test')

    def clear_db(self):
        self.test('Test')

    def export_db(self):
        self.test('Test')


    ############## QUIT ##################################
    ######################################################

    def closeEvent(self, event):
        reply = self.confirm_exit()
        if reply == QMessageBox.StandardButton.Yes:
            if hasattr(self, 'server'):
                self.server.stop()
            event.accept()
        else:
            event.ignore()


    def confirm_exit(self):
        reply = QMessageBox.question(self, self.title,
                                     'Are you sure want to exit?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            QApplication.quit()
        else:
            pass


    def test(self, message):
        QMessageBox.information(self, self.title, message)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = Main()
    main_window.show()
    sys.exit(app.exec())