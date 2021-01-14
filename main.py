import os
import pickle
import re
import sys
import time
import enchant
from enchant import tokenize
from enchant.errors import TokenizerNotFoundError
from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import *
from PyQt5.QtGui import QPalette, QColor, QSyntaxHighlighter, QTextCharFormat, QCloseEvent, QPixmap, QMovie
from PyQt5.QtWidgets import *
import traceback
from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException, TimeoutException, WebDriverException, RemoteDriverServerException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


# noinspection PyArgumentList,PyTypeChecker,PyBroadException
class Window(QWidget):
    def __init__(self, *args, **kwargs):
        super(Window, self).__init__(*args, **kwargs)
        # Window config
        self.setWindowTitle('VIPKid Feedback App')
        self.resize(525, 725)
        self.app_icon = QtGui.QIcon()
        self.app_icon.addFile('pencil.png', QtCore.QSize(16, 16))
        self.setWindowIcon(self.app_icon)
        self.threadpool = QThreadPool()
        # Create layout instance
        self.layout = QVBoxLayout()
        # Widgets
        self.student = QLineEdit(self)
        self.yes_button = QRadioButton('&Yes')
        self.no_button = QRadioButton('&No')
        self.feedback_temp = SpellTextEdit()
        self.feedback_output = QPlainTextEdit(self)
        self.generate_output = QPushButton('Generate Feedback')
        # HBox button group 1
        self.hbox_buttons1 = QWidget()
        self.hbox_buttonsLayout1 = QHBoxLayout(self.hbox_buttons1)
        self.login_button = QPushButton('Login')
        self.get_template_button = QPushButton('Get Feedback Template')
        self.get_template_button.setEnabled(False)
        self.loading = QLabel()
        self.loading.setVisible(False)
        self.login_success = QLabel('Logged In!')
        self.login_success.setVisible(False)
        self.logged_in_already = QLabel('Already logged in!')
        self.logged_in_already.setVisible(False)
        self.hbox_buttonsLayout1.addWidget(self.get_template_button, 3)
        self.hbox_buttonsLayout1.addWidget(self.login_button, 1)
        self.hbox_buttonsLayout1.addWidget(self.loading)
        self.hbox_buttonsLayout1.addWidget(self.login_success)
        self.hbox_buttonsLayout1.addWidget(self.logged_in_already)
        # HBox button group 2
        self.hbox_buttons2 = QWidget()
        self.hbox_buttonsLayout2 = QHBoxLayout(self.hbox_buttons2)
        self.copy_output_button = QPushButton('Copy Feedback')
        self.clear_form_button = QPushButton('Clear')
        self.hbox_buttonsLayout2.addWidget(self.copy_output_button)
        self.hbox_buttonsLayout2.addWidget(self.clear_form_button)
        # Add widgets to layout
        self.layout.addWidget(self.hbox_buttons1)
        self.layout.addWidget(QHline())
        self.layout.addSpacing(5)
        self.layout.addWidget(QLabel('Student Name:'))
        self.layout.addSpacing(2)
        self.layout.addWidget(self.student)
        self.layout.addSpacing(7)
        self.layout.addWidget(QLabel('New Student?'))
        self.layout.addWidget(self.yes_button)
        self.layout.addWidget(self.no_button)
        self.layout.addSpacing(7)
        self.layout.addWidget(QLabel('Feedback Template:'))
        self.layout.addSpacing(2)
        self.layout.addWidget(self.feedback_temp, 6)
        self.layout.addSpacing(5)
        self.layout.addWidget(self.generate_output)
        self.layout.addSpacing(5)
        self.layout.addWidget(QHline())
        self.layout.addSpacing(5)
        self.layout.addWidget(QLabel('Feedback:'))
        self.layout.addSpacing(2)
        self.layout.addWidget(self.feedback_output, 5)
        self.layout.addSpacing(2)
        self.layout.addWidget(self.hbox_buttons2)
        self.setLayout(self.layout)
        # Button configs
        self.no_button.setChecked(True)
        self.generate_output.setDefault(True)
        self.copy_output_button.setDefault(True)
        self.clear_form_button.setDefault(True)
        self.get_template_button.setDefault(True)
        self.feedback_temp.setTabChangesFocus(True)
        self.feedback_output.setTabChangesFocus(True)
        self.yes_button.setFocusPolicy(Qt.NoFocus)
        self.no_button.setFocusPolicy(Qt.NoFocus)
        self.feedback_output.setFocusPolicy(Qt.NoFocus)
        # Dark mode
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.WindowText, Qt.white)
        self.setPalette(palette)
        self.generate_output.setStyleSheet('QPushButton {background-color: rgb(115, 115, 115); color: rgb(235, 235, 235);'
                                           'border-radius: 12px; padding: 5px; font: bold 12px;}'
                                           'QPushButton:pressed {background-color: rgb(53, 53, 53)}'
                                           'QPushButton:hover {border: 0.5px solid white}')
        self.copy_output_button.setStyleSheet('QPushButton {background-color: rgb(115, 115, 115); color: rgb(235, 235, 235);'
                                              'border-radius: 12px; padding: 5px; font: bold 12px;}'
                                              'QPushButton:pressed {background-color: rgb(53, 53, 53)}'
                                              'QPushButton:hover {border: 0.5px solid white}')
        self.clear_form_button.setStyleSheet('QPushButton {background-color: rgb(115, 115, 115); color: rgb(235, 235, 235);'
                                             'border-radius: 12px; padding: 5px; font: bold 12px;}'
                                             'QPushButton:pressed {background-color: rgb(53, 53, 53)}'
                                             'QPushButton:hover {border: 0.5px solid white}')
        self.get_template_button.setStyleSheet('QPushButton {background-color: rgb(115, 115, 115); color: rgb(235, 235, 235);'
                                               'border-radius: 12px; padding: 5px; font: bold 12px;}'
                                               'QPushButton:pressed {background-color: rgb(53, 53, 53)}'
                                               'QPushButton:hover {border: 0.5px solid white}')
        self.login_button.setStyleSheet('QPushButton {background-color: rgb(115, 115, 115); color: rgb(235, 235, 235);'
                                        'border-radius: 12px; padding: 5px; font: bold 12px;}'
                                        'QPushButton:pressed {background-color: rgb(53, 53, 53)}'
                                        'QPushButton:hover {border: 0.5px solid white}')
        self.feedback_temp.setStyleSheet('background-color: rgb(36, 36, 36); border-radius: 4px;'
                                         'color: rgb(235, 235, 235); border: 0.5px solid rgba(115, 115, 115, 0.5)')
        self.feedback_output.setStyleSheet('background-color: rgb(36, 36, 36); border-radius: 4px; '
                                           'color: rgb(235, 235, 235); border: 0.5px solid rgba(115, 115, 115, 0.5)')
        self.student.setStyleSheet('background-color: rgb(36, 36, 36); border-radius: 2px; '
                                   'color: rgb(235, 235, 235); border: 0.5px solid rgba(115, 115, 115, 0.5)')
        # Tool Tips
        if self.get_template_button.isEnabled():
            self.get_template_button.setToolTip('Automatically get feedback template.')
        else:
            self.get_template_button.setToolTip('Login to use feature.')
        self.copy_output_button.setToolTip('Copies output to clipboard.')
        self.generate_output.setToolTip('Generate feedback from template.')
        self.clear_form_button.setToolTip('Clear student name & template.')
        self.login_button.setToolTip('Login & Connect to VIPKid.')
        # self.student.setToolTip('Get template for specific student') //needed after search function implemented
        # Start global webdriver
        if os.path.exists('cookie'):
            options = Options()
            options.headless = True
            self.browser = webdriver.Chrome(options=options)
            print('driver connected')
        # Signals and slots
        self.login_button_counter = 0
        if os.path.exists('cookie'):
            self.login_button.clicked.connect(self.login_slots)
        else:
            self.login_button.clicked.connect(self.login_nocookies)
        self.get_template_button.clicked.connect(self.feedback_automation)
        self.generate_output.clicked.connect(self.feedback_script)
        self.copy_output_button.clicked.connect(self.copy)
        self.clear_form_button.clicked.connect(self.clear_form)

    def feedback_script(self):
        global new_student
        global output
        student_name = self.student.text()
        feedback_input = self.feedback_temp.toPlainText()
        feedback_output = re.sub(' we |We', f' {student_name} and I ', feedback_input, 1)
        feedback_output = ' '.join(feedback_output.split())
        if self.yes_button.isChecked():
            new_student = 'yes'
        elif self.no_button.isChecked():
            new_student = 'no'
        if new_student == 'no':
            output = f'{feedback_output} Fantastic job today {student_name}! ' \
                     f'Keep practicing your English and working hard, you are ' \
                     f'improving every class! See you next time {student_name}. ' \
                     f'亲爱的父母，如果您喜欢今天的课程，请考虑给我一个5分的苹果评估。 这项评估对我的工作非常重要。 非常感谢! ' \
                     f'From, Teacher Carlos ZDG.'
        elif new_student == 'yes':
            output = f'{feedback_output} Fantastic job today {student_name}! ' \
                     f'It was great meeting you. Keep up the great work, and I hope ' \
                     f'to see you in my class again soon. ' \
                     f'亲爱的父母，如果您喜欢今天的课程，请考虑给我一个5分的苹果评估。 这项评估对我的工作非常重要。 非常感谢! ' \
                     f'From, Teacher Carlos ZDG.'
        if student_name == '':
            self.feedback_output.clear()
        else:
            self.feedback_output.clear()
            self.feedback_output.insertPlainText(output)

    def clear_form(self):
        self.student.clear()
        self.feedback_temp.clear()

    def copy(self):
        try:
            clipboard = QtGui.QGuiApplication.clipboard()
            clipboard.setText(output)
        except Exception:
            pass

    def closeEvent(self, event):
        try:
            self.browser.quit()
        except:
            pass

    def login(self):
        print('Logging in...')
        self.browser.get('https://www.vipkid.com/login?prevUrl=https%3A%2F%2Fwww.vipkid.com%2Ftc%2Fmissing')
        # try:
        with open('cookie', 'rb') as cookiesfile:
            cookies = pickle.load(cookiesfile)
            for cookie in cookies:
                self.browser.add_cookie(cookie)
            self.browser.refresh()
            missing_cf_button = WebDriverWait(self.browser, 3).until(EC.element_to_be_clickable((By.CLASS_NAME, 'tto-do-type')))
            self.browser.execute_script("arguments[0].click();", missing_cf_button)
            self.login_button_counter = 1
            print('Logged In!')
        os.remove('cookie')
        with open('cookie', 'wb') as file:
            pickle.dump(self.browser.get_cookies(), file)

    def login_error_msg(self):
        print("Couldn't log in")
        msgBox = QMessageBox(self)
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setWindowModality(Qt.WindowModal)
        msgBox.setWindowFlag(Qt.ToolTip)
        msgBox.setText('There was a problem logging into VIPKid.')
        msgBox.setInformativeText('Please try again by clicking the "Retry" button below.')
        msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        retry_button = msgBox.button(QMessageBox.Ok)
        retry_button.setText('Retry')
        msgBox.setDefaultButton(QMessageBox.Ok)
        msgBox.setStyleSheet('QMessageBox {background-color: rgb(53, 53, 53); border-top: 25px solid rgb(115, 115, 115);'
                             'border-left: 1px solid rgb(115, 115, 115); border-right: 1px solid rgb(115, 115, 115);'
                             'border-bottom: 1px solid rgb(115, 115, 115)}'
                             'QLabel {color: rgb(235, 235, 235); padding-top: 30px}'
                             'QPushButton {background-color: rgb(115, 115, 115); color: rgb(235, 235, 235);'
                             'border-radius: 11px; padding: 5px; min-width: 5em}'
                             'QPushButton:pressed {background-color: rgb(53, 53, 53)}'
                             'QPushButton:hover {border: 0.5px solid white}')
        result = msgBox.exec()
        if result == QMessageBox.Ok:
            try:
                print('Trying to login again..')
                os.remove('cookie')
                print('cookies removed.')
                self.browser.quit()
                time.sleep(2)
                self.login_nocookies()
            except Exception as e:
                print('got here')
                msgBox = QMessageBox(self)
                msgBox.setIcon(QMessageBox.Critical)
                msgBox.setText('Error')
                msgBox.setDetailedText(e)
                msgBox.setStyleSheet('QMessageBox {background-color: rgb(53, 53, 53); border-top: 25px solid rgb(115, 115, 115);'
                                     'border-left: 1px solid rgb(115, 115, 115); border-right: 1px solid rgb(115, 115, 115);'
                                     'border-bottom: 1px solid rgb(115, 115, 115)}'
                                     'QLabel {color: rgb(235, 235, 235); padding-top: 30px}'
                                     'QPushButton {background-color: rgb(115, 115, 115); color: rgb(235, 235, 235);'
                                     'border-radius: 11px; padding: 5px; min-width: 5em}'
                                     'QPushButton:pressed {background-color: rgb(53, 53, 53)}'
                                     'QPushButton:hover {border: 0.5px solid white}')
                msgBox.exec()

    def login_nocookies(self):
        if self.login_button_counter == 0:
            msgBox = QMessageBox(self)
            # msgBox.setWindowModality(Qt.WindowModal)
            msgBox.setWindowFlag(Qt.ToolTip)
            msgBox.setIcon(QMessageBox.Information)
            msgBox.setText('Click the "Login" button below.\nLogin to VIPKid in the window that opens.')
            # msgBox.setInformativeText('You will only need to log into VIPKid the first time you use this app.')
            msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            ok_button = msgBox.button(QMessageBox.Ok)
            ok_button.setText('Login')
            msgBox.setDefaultButton(QMessageBox.Ok)
            msgBox.setStyleSheet('QMessageBox {background-color: rgb(53, 53, 53); border-top: 25px solid rgb(115, 115, 115);'
                                 'border-left: 1px solid rgb(115, 115, 115); border-right: 1px solid rgb(115, 115, 115);'
                                 'border-bottom: 1px solid rgb(115, 115, 115)}'
                                 'QLabel {color: rgb(235, 235, 235); padding-top: 30px}'
                                 'QPushButton {background-color: rgb(115, 115, 115); color: rgb(235, 235, 235);'
                                 'border-radius: 11px; padding: 5px; min-width: 5em}'
                                 'QPushButton:pressed {background-color: rgb(53, 53, 53)}'
                                 'QPushButton:hover {border: 0.5px solid white}')
            result = msgBox.exec()
            if result == QMessageBox.Ok:
                print('Nice!')
                self.login_nocookies_slots()
        elif self.login_button_counter == 1:
            self.login_slots()

    def login_nocookies_prompt(self):
        self.browser = webdriver.Chrome()
        self.browser.get('https://www.vipkid.com/login?prevUrl=https%3A%2F%2Fwww.vipkid.com%2Ftc%2Fmissing')
        # Wait for user login.
        WebDriverWait(self.browser, 2147483647).until(EC.presence_of_element_located((By.XPATH, '//*[@id="__layout"]/div/div[2]/div/div/ul/li[2]/a')))
        time.sleep(1)
        # Save cookies file after login
        with open('cookie', 'wb') as file:
            pickle.dump(self.browser.get_cookies(), file)
        time.sleep(1)
        self.browser.quit()
        options = Options()
        options.headless = True
        self.browser = webdriver.Chrome(options=options)
        self.browser.get('https://www.vipkid.com/login?prevUrl=https%3A%2F%2Fwww.vipkid.com%2Ftc%2Fmissing')
        try:
            with open('cookie', 'rb') as cookiesfile:
                cookies = pickle.load(cookiesfile)
                for cookie in cookies:
                    self.browser.add_cookie(cookie)
                self.browser.refresh()
                missing_cf_button = WebDriverWait(self.browser, 5).until(EC.element_to_be_clickable((By.CLASS_NAME, 'to-do-type')))
                self.browser.execute_script("arguments[0].click();", missing_cf_button)
                self.login_button_counter = 1
                print('Logged In!')
                self.get_template_button.setEnabled(True)
        except Exception as e:
            msgBox = QMessageBox(self)
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.setText('Error')
            msgBox.setDetailedText(e)
            msgBox.setStyleSheet('QMessageBox {background-color: rgb(53, 53, 53); border-top: 25px solid rgb(115, 115, 115);'
                                 'border-left: 1px solid rgb(115, 115, 115); border-right: 1px solid rgb(115, 115, 115);'
                                 'border-bottom: 1px solid rgb(115, 115, 115)}'
                                 'QLabel {color: rgb(235, 235, 235); padding-top: 30px}'
                                 'QPushButton {background-color: rgb(115, 115, 115); color: rgb(235, 235, 235);'
                                 'border-radius: 11px; padding: 5px; min-width: 5em}'
                                 'QPushButton:pressed {background-color: rgb(53, 53, 53)}'
                                 'QPushButton:hover {border: 0.5px solid white}')
            msgBox.exec()

    # def login_first_msg(self):
    #     msgBox = QMessageBox(self)
    #     msgBox.setIcon(QMessageBox.Information)
    #     msgBox.setWindowFlag(Qt.ToolTip)
    #     msgBox.setText("<p align='center'>Please Login First!<br>")
    #     msgBox.setStandardButtons(QMessageBox.Ok)
    #     msgBox.setDefaultButton(QMessageBox.Ok)
    #     msgBox.setStyleSheet('QMessageBox {background-color: rgb(53, 53, 53); border-top: 25px solid rgb(115, 115, 115);'
    #                          'border-left: 1px solid rgb(115, 115, 115); border-right: 1px solid rgb(115, 115, 115);'
    #                          'border-bottom: 1px solid rgb(115, 115, 115)}'
    #                          'QLabel {color: rgb(235, 235, 235); padding-top: 30px}'
    #                          'QPushButton {background-color: rgb(115, 115, 115); color: rgb(235, 235, 235);'
    #                          'border-radius: 11px; padding: 5px; min-width: 5em}'
    #                          'QPushButton:pressed {background-color: rgb(53, 53, 53)}'
    #                          'QPushButton:hover {border: 0.5px solid white}')
    #     msgBox.exec()

    def feedback_automation(self):
        # Clear any previous text from text boxes.
        self.student.clear()
        self.feedback_temp.clear()
        ''' create own class for progress bar'''
        progress_bar = QProgressDialog('', '', 0, 100, self)
        progress_bar.setWindowModality(Qt.WindowModal)
        progress_bar.setWindowFlag(Qt.FramelessWindowHint)
        progress_bar.setAttribute(Qt.WA_TranslucentBackground)
        bar = QProgressBar()
        bar.setFixedHeight(15)
        bar.setTextVisible(False)
        progress_bar.setBar(bar)
        progress_bar.setWindowTitle('VIPKid Feedback App')
        label = QLabel('Getting feedback template...')
        label.setStyleSheet('color: rgb(235, 235, 235); font: 12px')
        progress_bar.setLabel(label)
        progress_bar.setStyleSheet('QProgressBar {border: 1px solid rgb(115, 115, 115); border-radius: 7px;'
                                   'background-color: rgb(36, 36, 36);}'
                                   'QProgressBar::chunk {background-color: rgb(115, 115, 115); border-radius: 6px;}')
        progress_bar.setCancelButton(None)
        progress_bar.forceShow()
        progress_bar.setValue(0)
        self.browser.refresh()
        progress_bar.setValue(10)
        try:
            try:
                WebDriverWait(self.browser, 2).until(EC.presence_of_element_located((By.XPATH, '//*[@id="__layout"]/div/div[2]/div/div[1]/div/div[2]/div/div[3]/div[3]/div/span/div/div/div/p')))
                progress_bar.setValue(99)
                time.sleep(1)
                progress_bar.setValue(100)
                self.feedback_output.clear()
                msgBox = QMessageBox(self)
                msgBox.setIcon(QMessageBox.Information)
                msgBox.setWindowFlag(Qt.ToolTip)
                msgBox.setText('All student feedback completed!')
                msgBox.setStandardButtons(QMessageBox.Ok)
                msgBox.setDefaultButton(QMessageBox.Ok)
                msgBox.setStyleSheet('QMessageBox {background-color: rgb(53, 53, 53); border-top: 25px solid rgb(115, 115, 115);'
                                     'border-left: 1px solid rgb(115, 115, 115); border-right: 1px solid rgb(115, 115, 115);'
                                     'border-bottom: 1px solid rgb(115, 115, 115)}'
                                     'QLabel {color: rgb(235, 235, 235); padding-top: 30px}'
                                     'QPushButton {background-color: rgb(115, 115, 115); color: rgb(235, 235, 235);'
                                     'border-radius: 11px; padding: 5px; min-width: 5em}'
                                     'QPushButton:pressed {background-color: rgb(53, 53, 53)}'
                                     'QPushButton:hover {border: 0.5px solid white}')
                msgBox.exec()
            except TimeoutException:
                progress_bar.setValue(15)
                student_name = str(WebDriverWait(self.browser, 5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="__layout"]/div/div[2]/div/div/div/div[2]/div/div[3]/div[3]/table/tbody/tr[1]/td[4]/div/div/div/span'))).get_attribute('innerHTML').splitlines()[0])
                student_name = student_name.title()
                if student_name.isupper():
                    student_name = ''.join(student_name.split()).title()
                self.student.setText(student_name)
                progress_bar.setValue(25)
                materials_button = WebDriverWait(self.browser, 5).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='__layout']/div/div[2]/div/div[1]/div/div[2]/div/div[3]/div[3]/table/tbody/tr[1]/td[7]/div/div/div[2]")))
                self.browser.execute_script("arguments[0].click();", materials_button)
                progress_bar.setValue(40)
                self.browser.switch_to.window(self.browser.window_handles[1])
                progress_bar.setValue(50)
                template_button = WebDriverWait(self.browser, 5).until(EC.element_to_be_clickable((By.ID, 'tab-5')))
                self.browser.execute_script("arguments[0].click();", template_button)
                progress_bar.setValue(75)
                # Click show 'more' button until all templates are shown.
                show_more_button = WebDriverWait(self.browser, 5).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="__layout"]/div/div/div[3]/div/div[1]/div[1]/div[2]/section/div[2]/div[4]/div/button')))
                try:
                    while show_more_button.is_displayed():
                        self.browser.execute_script("arguments[0].click()", show_more_button)
                except StaleElementReferenceException:
                    time.sleep(1)
                progress_bar.setValue(90)
                # Iterate through every <li> tag until we find a teacher name in csv file.
                ul_list = self.browser.find_element_by_class_name('shared-notes-list-container')
                li_tags = ul_list.find_elements_by_tag_name('li')
                valid_teachers = ['Katie EAV', 'Tammy PHT', 'Amber MZC', 'Andrew BAR', 'Kimberly BDP', 'Miranda CR',
                                  'Richard ZZ', 'Tomas B', 'Stefanie BD', 'Kristina EB', 'Jessica XH', 'Thomas CH']
                invalid_teacher_count = int(len(li_tags))
                for li_tag in li_tags:
                    teacher_name = li_tag.find_element_by_xpath(".//div[2]/div[1]").get_attribute('innerHTML').splitlines()[0]
                    if teacher_name in valid_teachers:
                        template = str(li_tag.find_element_by_xpath(".//div[2]/div[2]").text)
                        progress_bar.setValue(99)
                        time.sleep(1)
                        self.feedback_temp.insertPlainText(template)
                        progress_bar.setValue(100)
                        self.browser.close()
                        self.browser.switch_to.window(self.browser.window_handles[0])
                        if len(self.browser.window_handles) > 1:
                            self.browser.switch_to.window(self.browser.window_handles[-1])
                            self.browser.close()
                            self.browser.switch_to.window(self.browser.window_handles[0])
                        break
                    elif teacher_name not in valid_teachers:
                        invalid_teacher_count -= 1
                        continue
                if invalid_teacher_count == 0:
                    progress_bar.close()
                    progress_bar.setAttribute(Qt.WA_DeleteOnClose, True)
                    msgBox = QMessageBox(self)
                    msgBox.setIcon(QMessageBox.Information)
                    msgBox.setWindowFlag(Qt.ToolTip)
                    msgBox.setText('No valid teacher templates :(')
                    msgBox.setStandardButtons(QMessageBox.Ok)
                    msgBox.setDefaultButton(QMessageBox.Ok)
                    msgBox.setStyleSheet('QMessageBox {background-color: rgb(53, 53, 53); border-top: 25px solid rgb(115, 115, 115);'
                                         'border-left: 1px solid rgb(115, 115, 115); border-right: 1px solid rgb(115, 115, 115);'
                                         'border-bottom: 1px solid rgb(115, 115, 115)}'
                                         'QLabel {color: rgb(235, 235, 235); padding-top: 30px}'
                                         'QPushButton {background-color: rgb(115, 115, 115); color: rgb(235, 235, 235);'
                                         'border-radius: 11px; padding: 5px; min-width: 5em}'
                                         'QPushButton:pressed {background-color: rgb(53, 53, 53)}'
                                         'QPushButton:hover {border: 0.5px solid white}')
                    msgBox.exec()
                    self.browser.close()
                    self.browser.switch_to.window(self.browser.window_handles[0])
                    if len(self.browser.window_handles) > 1:
                        self.browser.switch_to.window(self.browser.window_handles[-1])
                        self.browser.close()
                        self.browser.switch_to.window(self.browser.window_handles[0])
        except Exception as e:
            print(e)
            progress_bar.close()
            progress_bar.setAttribute(Qt.WA_DeleteOnClose, True)
            msgBox = QMessageBox(self)
            msgBox.setIcon(QMessageBox.Information)
            msgBox.setWindowFlag(Qt.ToolTip)
            msgBox.setText('There was a problem getting student feedback.')
            msgBox.setInformativeText('Please try again by clicking the "Retry" button below.')
            msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            retry_button = msgBox.button(QMessageBox.Ok)
            retry_button.setText('Retry')
            msgBox.setDefaultButton(QMessageBox.Ok)
            msgBox.setStyleSheet('QMessageBox {background-color: rgb(53, 53, 53); border-top: 25px solid rgb(115, 115, 115);'
                                 'border-left: 1px solid rgb(115, 115, 115); border-right: 1px solid rgb(115, 115, 115);'
                                 'border-bottom: 1px solid rgb(115, 115, 115)}'
                                 'QLabel {color: rgb(235, 235, 235); padding-top: 30px}'
                                 'QPushButton {background-color: rgb(115, 115, 115); color: rgb(235, 235, 235);'
                                 'border-radius: 11px; padding: 5px; min-width: 5em}'
                                 'QPushButton:pressed {background-color: rgb(53, 53, 53)}'
                                 'QPushButton:hover {border: 0.5px solid white}')
            msgBox.exec()
            if msgBox.clickedButton() == retry_button:
                print('Running again..')
                self.browser.switch_to.window(self.browser.window_handles[0])
                self.browser.refresh()
                time.sleep(2)
                self.get_template_button.click()

    def login_started(self):
        gif = QMovie('loading.gif')
        self.loading.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.loading.setAttribute(Qt.WA_TranslucentBackground)
        self.loading.setMovie(gif)
        gif.start()
        self.loading.show()

    def login_finished(self):
        self.loading.close()

    def login_msg(self):
        self.login_success.setVisible(True)

    def login_msg_close(self):
        self.login_success.setVisible(False)

    def login_already_msg(self):
        self.logged_in_already.setVisible(True)

    def login_already_msg_close(self):
        self.logged_in_already.setVisible(False)

    def login_slots(self):
        if self.login_button_counter == 0:
            worker = WorkerThread(self.login)
            worker.signal.started.connect(self.login_started)
            worker.signal.finished.connect(self.login_finished)
            worker.signal.login_open.connect(self.login_msg)
            worker.signal.login_close.connect(self.login_msg_close)
            worker.signal.login_error.connect(self.login_error_msg)
            self.threadpool.start(worker)

        else:
            worker = WorkerThreadAlreadyLogin()
            worker.signal.login_close.connect(self.login_msg_close)
            worker.signal.started.connect(self.login_already_msg)
            worker.signal.finished.connect(self.login_already_msg_close)
            self.threadpool.start(worker)

    def login_nocookies_slots(self):
        worker = WorkerThreadNoCookies(self.login_nocookies_prompt)
        worker.signal.started.connect(self.login_started)
        worker.signal.finished.connect(self.login_finished)
        worker.signal.login_open.connect(self.login_msg)
        worker.signal.login_close.connect(self.login_msg_close)
        self.threadpool.start(worker)


class WorkerSignals(QObject):
    started = pyqtSignal()
    finished = pyqtSignal()
    login_open = pyqtSignal()
    login_close = pyqtSignal()
    nocookies_msg = pyqtSignal()
    login_prompt = pyqtSignal()
    login_error = pyqtSignal()


class WorkerThread(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super(WorkerThread, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signal = WorkerSignals()

    @pyqtSlot()
    def run(self):
        self.signal.started.emit()
        try:
            self.fn(*self.args, **self.kwargs)
            self.signal.finished.emit()
            self.signal.login_open.emit()
            time.sleep(4)
            self.signal.login_close.emit()
        except Exception:
            self.signal.finished.emit()
            self.signal.login_error.emit()


class WorkerThreadNoCookies(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super(WorkerThreadNoCookies, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signal = WorkerSignals()

    @pyqtSlot()
    def run(self):
        self.signal.started.emit()
        try:
            self.fn(*self.args, **self.kwargs)
            self.signal.finished.emit()
            self.signal.login_open.emit()
            time.sleep(5)
            self.signal.login_close.emit()
        except Exception:
            self.signal.finished.emit()


class WorkerThreadAlreadyLogin(QRunnable):
    def __init__(self, *args, **kwargs):
        super(WorkerThreadAlreadyLogin, self).__init__()
        self.args = args
        self.kwargs = kwargs
        self.signal = WorkerSignals()

    @pyqtSlot()
    def run(self):
        self.signal.login_close.emit()
        self.signal.started.emit()
        time.sleep(3)
        self.signal.finished.emit()


class SpellTextEdit(QPlainTextEdit):
    """QPlainTextEdit subclass which does spell-checking using PyEnchant"""

    def __init__(self, *args):
        QPlainTextEdit.__init__(self, *args)

        # Start with a default dictionary based on the current locale.
        self.highlighter = SpellChecker(self.document())
        self.highlighter.setDict(enchant.Dict())


class SpellChecker(QSyntaxHighlighter):
    """QSyntaxHighlighter subclass which consults a PyEnchant dictionary"""
    tokenizer = None
    token_filters = (tokenize.EmailFilter, tokenize.URLFilter)
    err_format = QTextCharFormat()
    err_format.setUnderlineColor(Qt.red)
    err_format.setUnderlineStyle(QTextCharFormat.SpellCheckUnderline)

    def __init__(self, *args):
        QSyntaxHighlighter.__init__(self, *args)

        # Initialize private members
        self._sp_dict = None
        self._chunkers = []

    def chunkers(self):
        """Gets the chunkers in use"""
        return self._chunkers

    def dict(self):
        """Gets the spelling dictionary in use"""
        return self._sp_dict

    def setChunkers(self, chunkers):
        """Sets the list of chunkers to be used"""
        self._chunkers = chunkers
        self.setDict(self.dict())

    def setDict(self, sp_dict):
        """Sets the spelling dictionary to be used"""
        try:
            self.tokenizer = tokenize.get_tokenizer(sp_dict.tag, chunkers=self._chunkers, filters=self.token_filters)
        except TokenizerNotFoundError:
            # Fall back to English tokenizer
            self.tokenizer = tokenize.get_tokenizer(chunkers=self._chunkers, filters=self.token_filters)
        self._sp_dict = sp_dict

        self.rehighlight()

    def highlightBlock(self, text):
        """Overridden QSyntaxHighlighter method to apply the highlight"""
        if not self._sp_dict:
            return

        # Build a list of all misspelled words and highlight them
        misspellings = []
        for (word, pos) in self.tokenizer(text):
            if not self._sp_dict.check(word):
                self.setFormat(pos, len(word), self.err_format)
                misspellings.append((pos, pos + len(word)))


# noinspection PyArgumentList
class QHline(QFrame):
    """creates a dark grey horizontal line break"""
    def __init__(self):
        super(QHline, self).__init__()
        self.setFrameShape(QFrame.HLine)
        self.setStyleSheet('color: rgb(115, 115, 115)')


class Splashscreen:
    def __init__(self):
        start = time.time()
        splash_pix = QPixmap('pencil_432x432.png')
        self.splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
        self.splash.show()
        while time.time() - start < 2:
            time.sleep(0.001)
            app.processEvents()

    def stop(self, widget):
        self.splash.finish(widget)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # style = 'style.qss'
    # with open(style, 'r') as qss:
    #     app.setStyleSheet(qss.read())
    splash = Splashscreen()
    window = Window()
    window.show()
    splash.stop(window)
    app.exec()
