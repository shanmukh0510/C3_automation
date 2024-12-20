import os
import logging
import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from connection1 import *  # Assuming these functions are defined in connection1 module


setting = read_file('json/setting.json')
Element = setting['Mode']

class Connection_Setup():
    def loggen(self):
        current_path = os.path.abspath(os.path.dirname(__file__))

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = f"{current_path}/Logs/{Element}_ConnectionTab_automation_{timestamp}.html"

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

    def connectionsetup(self):
        # driver initialization
        options = webdriver.ChromeOptions()
        options.add_argument("start-maximized")
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        s = Service(executable_path="Resources\chromedriver-win32\chromedriver.exe")
        self.driver = webdriver.Chrome(service=s)

        tc1_check_readme_file()
        tc2_check_release_file()
        tc3_check_eload_file()
        tc4_check_firmware_file()
        tc5_open_browser(self.driver, setting['Mode'])
        tc6_browser_tab_title(self.driver)
        tc7_scannetwork_enablestate(self.driver)
        tc8_scanNetworkstate(self.driver)
        86(self.driver)
        tc10_addressText(self.driver) 
        tc11_defaultIp(self.driver)
        tc12_dynamicIp(self.driver)
        tc13_invalidIP(self.driver)
        tc14_unreachableIP(self.driver)
        tc15_ImageCompare(self.driver)
        if Element == "TPR":
            tc16_shortFixture(self.driver)
        

# Create an instance of Connection_Setup
obj = Connection_Setup()
obj.loggen()  # Call the loggen method to initialize the logger
obj.connectionsetup()  # Call the connectionsetup method
