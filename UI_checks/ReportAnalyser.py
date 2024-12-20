import os
import logging
import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from ReportAnalyser1 import *  # Assuming these functions are defined in connection1 module

setting = read_file('json/setting.json')
Element = setting['Mode']

class ReportAnalyser():
    def loggen(self):
        current_path = os.path.abspath(os.path.dirname(__file__))

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = f"{current_path}/Logs/{Element}_ReportAnalyser_automation_{timestamp}.html"

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

    def reportanalyser(self):
        # driver initialization
        options = webdriver.ChromeOptions()
        options.add_argument("start-maximized")
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        s = Service(executable_path="Resources\chromedriver-win32\chromedriver.exe")
        self.driver = webdriver.Chrome(service=s)

        tc1_open_browser(self.driver, setting['Mode'])
        tc2_Report_AnalyserTab(self.driver)
        tc3_RA_uploadjson(self.driver)
        tc4_RA_table_header(self.driver)
        tc5_Test_lab(self.driver)
        tc6_Test_Execution(self.driver)
        tc7_Test_toolinfo(self.driver)
        tc8_Test_dutinfo(self.driver)
        tc9_Test_scope(self.driver)
        tc10_expandall(self.driver)
        tc11_RA_uploadsecondjson(self.driver)
        tc12_boarder_header(self.driver)
        tc13_edit_reportRemark(self.driver)
        tc14_merge(self.driver)
        tc15_summary(self.driver)
        tc16_export_file(self.driver)
        tc17_delete(self.driver)
        tc18_digitalsignature(self.driver)

# Create an instance of Connection_Setup
obj = ReportAnalyser()
obj.loggen()  # Call the loggen method to initialize the logger
obj.reportanalyser()  # Call the connectionsetup method