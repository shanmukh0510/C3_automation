import os
import logging
import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from Help1 import *  # Assuming these functions are defined in connection1 module

setting = read_file('json/setting.json')
Element = setting['Mode']

class Help_page():
    def loggen(self):
        current_path = os.path.abspath(os.path.dirname(__file__))

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = f"{current_path}/Logs/{Element}_Help_automation_{timestamp}.html"

        # Create a new HTMLFileHandler
        file_handler = logging.FileHandler(log_file, mode='w')
        file_handler.setLevel(logging.INFO)

        # Define the HTML log format9+
        formatter = logging.Formatter(
            '<p>%(asctime)s: %(levelname)s: %(message)s</p>', datefmt='%m/%d/%Y %I:%M:%S %p')
        file_handler.setFormatter(formatter)

        # Create a new logger and add the HTMLFileHandler to it
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(file_handler)

    def Help(self):
        # driver initialization
        options = webdriver.ChromeOptions()
        options.add_argument("start-maximized")
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        s = Service(executable_path="Resources\chromedriver-win32\chromedriver.exe")
        self.driver = webdriver.Chrome(service=s)

        tc1_open_browser(self.driver, setting['Mode'])
        tc2_verify_help_page(self.driver)
        tc3_grl_supportDesk(self.driver)
        tc4_email_support(self.driver)
        tc5_download_logs(self.driver)
        tc6_info(self.driver)
        

# Create an instance of Connection_Setup
obj = Help_page()
obj.loggen()  # Call the loggen method to initialize the logger
obj.Help()  # Call the connectionsetup method