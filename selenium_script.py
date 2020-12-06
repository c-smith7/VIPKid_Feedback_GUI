from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import json
import os
from os import path
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class SeleniumAutomation:
    def config_json(self):
        # from qt widget, function will get user name and password to dump into json config file.
        # this will run when login button is clicked on gui, but if user doesn't want automation, don't press login.
        if path.exists('config.json'):
            print('Logged In!')  # Print 'Logged in' next to button with Qlabel or something.
        else:
            # open login widget window
            # pyqt_user and pyqt_password are entered by the user
            # create config file to be used in get_feedback_template()
            pyqt_user = 'carlosvsmith7@gmail.com'    # input from gui
            pyqt_password = 'brazil4444'            # input from gui
            login_dict = dict(user_name=pyqt_user, password=pyqt_password)
            with open('config.json', 'w') as outfile:
                json.dump(login_dict, outfile)
            print('Logged In!!')
        # include a reset user_name and password button that deletes the config file and let's user reenter login info.
        # def reset_button():
        # try:
        #     os.remove('config.json')
        # except OSError as e:
        #     print('File deleted')

    def login(self):
        with open('config.json', 'r') as openfile:
            config_file = json.load(openfile)
        user_name = config_file['user_name']
        password = config_file['password']
        # options = Options()
        # options.headless = True
        browser = webdriver.Chrome()
        # browser.minimize_window()
        browser.get('https://www.vipkid.com/login?prevUrl=https%3A%2F%2Fwww.vipkid.com%2Ftc%2Flist')  # using this until I have a missing lesson to test with
        # https://www.vipkid.com/login?prevUrl=https%3A%2F%2Fwww.vipkid.com%2Ftc%2Fmissing
        # Sign in
        login_email = browser.find_element_by_xpath('//*[@id="__layout"]/div/div[2]/div/div[2]/div/form/div[1]/div[1]/div/div[1]/input')
        login_email.send_keys(user_name)
        login_password = browser.find_element_by_xpath('//*[@id="__layout"]/div/div[2]/div/div[2]/div/form/div[1]/div[2]/div/div/input')
        login_password.send_keys(password)
        sign_in = browser.find_element_by_xpath('//*[@id="__layout"]/div/div[2]/div/div[2]/div/form/div[2]/button')
        sign_in.click()

        def text_present(text):
            return str(text) in browser.page_source
        if text_present('Verification'):
            print('Please Type in Verification Code & Press Enter.')  # popup widget or message in gui.
            browser.maximize_window()  # window will be minimized unless verification is required.
        else:
            print('No Verification needed!')  # don't print anything, just remove this else portion.

        # Something may need to be added here like WebDriverWait.until(...) so that user can enter code, and then
        # script can continue once an element is found on the following page.

    def get_feedback_template(self):
        # AT THIS POINT I DECIDED TO SWITCH LIBRARIES AND USE PYWINAUTO TO AUTOMATE THIS PROCESS THROUGH THE
        # VIPKID DESKTOP APP INSTEAD OF THE WEBPAGE.
        # HOWEVER, I WILL KEEP THIS FILE FOR POTENTIAL FUTURE REFERENCE.

test = SeleniumAutomation()
test.config_json()
test.login()
input('Press ENTER to end program')



# def auto_feedback():
#     student_name = input('Student name: ')
#     new_student = input('New Student?: ')
#     template = str(input('Feedback template: '))
#     feedback = template.replace('we', f'{student_name} and I', 1)
#     if new_student in ['no', 'No', 'n']:
#         print(f'{feedback} Fantastic job today {student_name}! Keep practicing your English and working hard, you are improving every class! See you next time {student_name}.' +
#             ' 亲爱的父母，如果您喜欢今天的课程，请考虑给我一个5分的苹果评估。 这项评估对我的工作非常重要。 非常感谢!' +
#             ' From, Teacher Carlos ZDG.')
#     else:
#         print(f'{feedback} Fantastic job today {student_name}! It was great meeting you. Keep up the great work, and I hope to see you in my class again soon.' +
#             ' 亲爱的父母，如果您喜欢今天的课程，请考虑给我一个5分的苹果评估。 这项评估对我的工作非常重要。 非常感谢!' +
#             ' From, Teacher Carlos ZDG.')
#
#
# auto_feedback()