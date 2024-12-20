import os
import logging
import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from Results1 import *

setting = read_file('json/setting.json')
Element = setting['Mode']


class Result():

    def loggen(self):
        current_path = os.path.abspath(os.path.dirname(__file__))

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = f"{current_path}/Logs/{Element}_Results_automation_{timestamp}.html"

        # Create a new HTMLFileHandler
        file_handler = logging.FileHandler(log_file, mode='w')
        file_handler.setLevel(logging.INFO)

        # Define the HTML log format
        formatter = logging.Formatter(
            '<p>%(asctime)s: %(levelname)s: %(message)s</p>', datefmt='%m/%d/%Y %I:%M:%S %p')
        file_handler.setFormatter(formatter)

        # Create a new logger and add the HTMLFileHandler to it
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(file_handler)

    def ResultsTab(self):
        # driver initialization
        options = webdriver.ChromeOptions()
        options.add_argument("start-maximized")
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        s = Service(executable_path="Resources\chromedriver-win32\chromedriver.exe")
        self.driver = webdriver.Chrome(service=s)

        tc1_open_browser(self.driver, setting['Mode'])
        tc2_Result_tab(self.driver)
        tc3_uploadproject(self.driver)
        tc8_no_testcase(self.driver)
        tc9_expand_collapse(self.driver)
        tc_10_chart_header(self.driver)
        tc_11_chart_toolbar(self.driver)
        tc_12_loadtrace(self.driver)

# Create an instance of Connection_Setup
obj = Result()
obj.loggen()  # Call the loggen method to initialize the logger
obj.ResultsTab()  # Call the connectionsetup method