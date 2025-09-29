import os
import pandas as pd
import numpy as np
import sys
import socket
import webbrowser
import time
import urllib.parse
import re
from datetime import datetime

from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from db_connect import *
from info import *

from PyQt6.QtWidgets import QProgressDialog, QApplication, QMainWindow, QMessageBox, QFileDialog, QDialog, QTableWidgetItem, QCheckBox, QWidget, QHBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QTextCharFormat, QColor, QTextCursor

from ui_pycode.main import Ui_Main


class Main(QMainWindow, Ui_Main):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.title = 'WhatsBot'
        self.success = ['\uf058', '#055D9D']
        self.error = ['\uf057', '#BD4A53']
        self.info = ['\uf05a', '#D8D9DB']
        self.critical = ['\uf06a', '#B76D30']
        self.setup_window()
        self.setup_buttons()

        

    def setup_window(self):
        self.setWindowTitle(self.title)
        self.btn_accept.hide()
        self.btn_cancel.hide()
        self.label_active.hide()
        self.fetch_message()
        self.fetch_temp_numbers_count()
        self.fetch_all_numbers_count()
        self.log_message(f"System initialized. Waiting for commands.", self.info)
        

    def setup_buttons(self):
        self.btn_import.clicked.connect(self.select_excel_file)
        self.btn_start.clicked.connect(self.start_operation)
        self.btn_pause.clicked.connect(self.pause_operation)
        self.btn_stop.clicked.connect(self.stop_operation)
        self.btn_edit.clicked.connect(lambda: self.message_action("edit"))
        self.btn_accept.clicked.connect(lambda: self.message_action("accept"))
        self.btn_cancel.clicked.connect(lambda: self.message_action("cancel"))
        self.btn_info.clicked.connect(self.about)
        self.btn_github.clicked.connect(self.github)
        self.btn_export.clicked.connect(self.export_db)
        self.btn_delete.clicked.connect(self.reset_db)


    ############## IMPORT FROM EXCEL #####################
    ######################################################

    def import_numbers(self, file_path, file_name):
        ext = os.path.splitext(file_path)[1].lower()
        engine = "openpyxl" if ext == ".xlsx" else "xlrd"
        df = pd.read_excel(file_path, sheet_name=0, header=None, engine=engine)
        col = df.iloc[:, 0]
        nums = pd.to_numeric(col, errors="coerce").dropna()
        nums = nums.apply(lambda x: int(x) if float(x).is_integer() else float(x))

        if len(nums) == 0:
            self.log_message(f"'{file_name}' file is empty.", self.error)
            return

        try:
            with Session() as session:
                session.query(TempNumbers).delete()
                session.commit()

                self.log_message(f"Uploading numbers from '{file_name}' file...", self.info)
                for i, number in enumerate(nums, 1):
                    session.add(TempNumbers(number=number))

                    self.label_temp_numbers.setText(f"{i}")
                    QApplication.processEvents()

                session.commit()

        except Exception as e:
            self.log_message(f"Database error: {e}.", self.error)
            return

        self.fetch_temp_numbers_count()
        self.log_message(f"Excel file '{file_name}' uploaded successfully ({len(nums)} contacts).", self.success)


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

        file_name = os.path.basename(file_path)
        try:
            self.import_numbers(file_path, file_name)
        except Exception as e:
            self.log_message(f"Error reading file '{file_name}': {e}.", self.error)


    ############## OPERATIONS #################################
    ######################################################

    def start_operation(self):
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")

        # driver = webdriver.Chrome(options=chrome_options)

        logged_in = False
    
        valid_numbers = []
        invalid_numbers = []

        with Session() as session:
            temp_numbers = session.query(TempNumbers).all()

        for number in temp_numbers:
            try:
                self.log_message(f"Message to {number.number} sent successfully.", self.success)
            except Exception as e:
                self.log_message(f"Failed to send message to {number.number}: {str(e)}.", self.error)
                invalid_numbers.append(number)
                

        # driver.quit()
        
    def log_message(self, text, log_type):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.Log.append(f'<font color="{log_type[1]}">{log_type[0]} {timestamp} - {text}</font><br>')
        QApplication.processEvents()

    def pause_operation(self):
        self.MessageBox('info' ,'Test')

    def stop_operation(self):
        self.MessageBox('info' ,'Test')

    def fetch_temp_numbers_count(self):
        with Session() as session:
            temp_numbers_count = session.query(TempNumbers).count()
        
        self.label_temp_numbers.setText(str(temp_numbers_count))

    def fetch_all_numbers_count(self):
        with Session() as session:
            all_numbers_count = session.query(Pool).count()
        
        self.label_DB_numbers.setText(str(all_numbers_count))

    ############## Message Section #######################
    ######################################################

    def message_action(self, action):
        if action in ('accept', 'cancel'):
            if action == 'accept':
                reply = QMessageBox.question(
                    self,
                    "Save Message",
                    "Are you sure you want to save message?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    try:
                        message_text = self.Message.toPlainText().strip()
                        
                        # if not message_text:
                        #     QMessageBox.warning(self, "Empty Message", "Message cannot be empty.")
                        #     self.Message.setFocus()
                        #     return
   
                        with Session() as session:
                            first_msg = session.query(Message).order_by(Message.id).first()
                            
                            if first_msg:
                                first_msg.message = message_text
                            else:
                                new_msg = Message(message=message_text)
                                session.add(new_msg)
                            
                            session.commit()
                            
                    except Exception as e:
                        QMessageBox.critical(self, "Error", f"Failed to save message:\n{str(e)}")
                        return
                else:
                    self.Message.setFocus()
                    return
                    
            else: 
                reply = QMessageBox.question(
                    self,
                    "Cancel Editing",
                    "Are you sure you want to discard changes?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.No:
                    self.Message.setFocus()
                    return
            
            self.btn_accept.hide()
            self.btn_cancel.hide() 
            self.btn_edit.show() 
            self.Message.setReadOnly(True)
            self.Message.clearFocus()

            self.fetch_message()
        else:
            self.btn_accept.show()
            self.btn_cancel.show() 
            self.btn_edit.hide() 
            self.Message.setReadOnly(False)
            self.Message.setFocus()
        

    def fetch_message(self):
        with Session() as session:
            first_msg = session.query(Message).order_by(Message.id).first()
            if first_msg:
                self.Message.setPlainText(first_msg.message)
            else:
                self.Message.clear()

    ############## TOP BUTTONS #######################
    ##################################################

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
        try:
            with Session() as session:
                results = session.query(Pool.number, Pool.whatsapp_status).all()

                if not results:
                    QMessageBox.warning(self, "No Data", "The Numbers is empty. Nothing to export.")
                    return

                default_filename = f"numbers_ex_{datetime.now().strftime('%Y%m%d')}.xlsx"
                file_path, _ = QFileDialog.getSaveFileName(
                    self,
                    "Export to Excel",
                    default_filename,
                    "Excel Files (*.xlsx)"
                )

                if not file_path:
                    return

                if not file_path.endswith('.xlsx'):
                    file_path += '.xlsx'

                data = [
                    {'Number': row.number, 'WhatsApp Status': row.whatsapp_status}
                    for row in results
                ]

                df = pd.DataFrame(data)
                df.to_excel(file_path, index=False)

            QMessageBox.information(self, "Success", f"Data exported successfully to:\n{file_path}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export data:\n{str(e)}")

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
        webbrowser.open("https://github.com/alasgarovs/OctoBot.git")

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