import os
import logging
import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from QI_Authenticator1 import *

setting = read_file('json/setting.json')
Element = setting['Mode']

class Authenticator():
    def loggen(self):
        current_path = os.path.abspath(os.path.dirname(__file__))

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = f"{current_path}/Logs/{Element}_QI_Auth__automation_{timestamp}.html"

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

    def qi_Authenticator(self):
        # driver initialization
        options = webdriver.ChromeOptions()
        options.add_argument("start-maximized")
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        s = Service(executable_path="Resources\chromedriver-win32\chromedriver.exe")
        self.driver = webdriver.Chrome(service=s)
        
        tc1_open_browser(self.driver, setting['Mode'])
        tc2_check_QI_Authenticator(self.driver)
        tc3_upload_and_validate_Authfile(self.driver)
        tc4_verify_signature_notValid(self.driver)
        tc5_upload_PTX_Auth(self.driver)
        tc6_nonce(self.driver)
        tc7_challenge_Auth(self.driver)
        tc8_decode_certificate(self.driver)
        tc9_certificate_chain(self.driver)
        tc10_tbsAuth(self.driver)
        tc11_validateauth_button(self.driver)
        tc12_download_RawCertificate(self.driver)
        tc13_download_Manufacturer_certificate(self.driver)
        tc14_download_product_certificate(self.driver)

# Create an instance of Connection_Setup
obj = Authenticator()
obj.loggen()  # Call the loggen method to initialize the logger
obj.qi_Authenticator()  # Call the connectionsetup method
