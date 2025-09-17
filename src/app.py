import os
import pandas as pd
import numpy as np
import sys
import socket
import webbrowser
from db_connect import *
from info import *
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
        self.btn_info.clicked.connect(self.about)
        self.btn_github.clicked.connect(self.github)
        self.btn_export.clicked.connect(self.export_db)
        self.btn_delete.clicked.connect(self.reset_db)


    ############## IMPORT FROM EXCEL #####################
    ######################################################

    def extract_numbers_from_excel(self, file_path):
        ext = os.path.splitext(file_path)[1].lower()
        engine = "openpyxl" if ext == ".xlsx" else "xlrd"
        df = pd.read_excel(file_path, sheet_name=0, header=None, engine=engine)
        col = df.iloc[:, 0]
        nums = pd.to_numeric(col, errors="coerce").dropna()
        nums = nums.apply(lambda x: int(x) if float(x).is_integer() else float(x))


        if len(nums) == 0:
            self.MessageBox('error', "Numbers could not be found")
            return

        self.Log.clear()
        self.label_comment_log.setText("Importing numbers...")
        QApplication.processEvents()

        try:
            with Session() as session:
                session.query(TempNumbers).delete()
                session.commit()

                for i, n in enumerate(nums, 1):
                    session.add(TempNumbers(number=n))

                    self.Log.append(f"- {n}")
                    self.label_comment_log.setText(f"Importing numbers: {i}")
                    QApplication.processEvents()

                session.commit()

        except Exception as e:
            self.MessageBox('error', f"Database error: {e}")
            return

        self.label_comment_log.setText("Real-time status updates and message delivery reports.")
        self.MessageBox('info', f'{len(nums)} numbers imported successfully')


    def select_excel_file(self):
        file_filter = "Excel Files (*.xlsx *.xls)"
        file_path, _ = QFileDialog.getOpenFileName(
            None,
            "Select Excel File",
            "",
            file_filter
        )
        if not file_path:
            return

        try:
            self.extract_numbers_from_excel(file_path)
        except Exception as e:
            self.MessageBox('error', f'Error reading file:{e}')


    ############## START #################################
    ######################################################

    def start_operation(self):
        self.MessageBox('info' ,'Test')


    ############## STOP ##################################
    ######################################################

    def stop_operation(self):
        self.MessageBox('info' ,'Test')


    ############## TOP BUTTONS #######################
    ######################################################

    ######## About ###########################
    def about (self):
        about_info = f"""\n
        Version: {app_version}
        Commit: {commit}
        Date: {last_update}
        Python: 3.13.7
        PyQt6: 6.9.1
        OS: Linux x64, Windows (10, 11) x64
        """

        self.MessageBox('info' , about_info)

    ######## Github #########################
    def github(self):
         webbrowser.open("https://github.com/alasgarovs/Octo.git")

    ####### Reset DB ############################
    def reset_db(self):
        reply = QMessageBox.question(self, 'Confirm Reset', 
                                     "Are you sure you want to reset the database?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            with Session() as session:
                session.query(Pool).delete()
                session.commit()

                session.query(TempNumbers).delete()
                session.commit()

                QMessageBox.information(self, 'Database Reset Successful', 'The database has been successfully reset to its initial state.')


    ######## Export DB from excel ####################
    def export_db(self):
        self.MessageBox('info' ,'Test')


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


    def MessageBox(self, type,message):
        if type == 'info':
            QMessageBox.information(self, self.title, message)
        elif type == 'error':
            QMessageBox.critical(self, self.title, message)




if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = Main()
    main_window.show()
    sys.exit(app.exec())