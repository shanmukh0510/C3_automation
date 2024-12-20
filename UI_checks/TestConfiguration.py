import os
import logging
import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from TestConfiguration1 import *


setting = read_file('json/setting.json')
Element = setting['Mode']

class TestConfiguration():

    def loggen(self):
        current_path = os.path.abspath(os.path.dirname(__file__))

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = f"{current_path}/Logs/{Element}_offlineTestConfig_automation_{timestamp}.html"

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

    def TestConfigurationTab(self):
        # driver initialization
        options = webdriver.ChromeOptions()
        options.add_argument("start-maximized")
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        s = Service(executable_path="Resources\chromedriver-win32\chromedriver.exe")
        self.driver = webdriver.Chrome(service=s)

        tc1_open_browser(self.driver, setting['Mode'])
        tc2_Test_Configuration_and_Selection(self.driver)
        tc3_projectName(self.driver)
        tc4_create_newproject(self.driver)
        tc5_uploadproject(self.driver)
        tc6_Quick_SelectTab(self.driver)
        tc7_Execute_SelectTab(self.driver)
        tc8_BSUT_Declaration(self.driver)
        tc9_Report_Generation(self.driver)
        tc10_Testcase_Availability(self.driver)
        # # # ImageCompare(self.driver, "before")
        tc11_Testresult(self.driver)
        tc12_reportgeneration(self.driver)
 


# Create an instance of Connection_Setup
obj = TestConfiguration()
obj.loggen()  # Call the loggen method to initialize the logger
obj.TestConfigurationTab()  # Call the connectionsetup method