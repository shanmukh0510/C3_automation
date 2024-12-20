import os
import logging
import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from Qi128_Exercise1 import * # Assuming these functions are defined in connection1 module

setting = read_file('json/setting.json')
Element = setting['Mode']

class Qi_exercise1():
    def loggen(self):
        current_path = os.path.abspath(os.path.dirname(__file__))

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = f"{current_path}/Logs/{Element}_Qi_Exerciser_Automation128khz{timestamp}.html"

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

    def qi_exercise(self):
        # driver initialization
        options = webdriver.ChromeOptions()
        options.add_argument("start-maximized")
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        s = Service(executable_path="Resources\chromedriver-win32\chromedriver.exe")
        self.driver = webdriver.Chrome(service=s)

        tc1_open_browser(self.driver, setting['Mode'])     
        tc2_verify_QiExercise(self.driver) 
        tc3_128khz_remove_packet_seq(self.driver)
        tc4_128khz_reset_packet_seq(self.driver)
        tc5_128khz_reset_exerciser(self.driver)
        tc6_128khz_add_packets_info(self.driver)
        tc7_128khz_add_packets_sequence(self.driver)
        tc8_128khz_add_packets_sequence_checks1_ID_Config(self.driver)
        tc9_128khz_add_packets_sequence_checks2_PT_Phase(self.driver)
        tc10_128khz_add_packets_sequence_checks3_Negotiation_Phase(self.driver)
        tc11_128khz_add_packets_sequence_checks4_Ping_Phase(self.driver)
        tc12_128khz_edit_packet_sequence_1(self.driver)
        tc13_128khz_edit_packet_sequence_2(self.driver)
        tc14_128khz_edit_packet_sequence_3(self.driver)
        tc15_128Khz_set_packet_sequence(self.driver)
        tc16_128Khz_save_and_recall_sequence(self.driver)
        tc17_128khz_start_clear(self.driver)
        tc18_128khz_instant_packets(self.driver)
        tc19_128khz_sip_tableheader(self.driver)
        tc20_128khz_prx_initiator(self.driver)
        tc21_128khz_ptx_initiator(self.driver)
        tc22_128khz_add_history(self.driver)

# Create an instance of Connection_Setup
obj = Qi_exercise1()
obj.loggen()  # Call the loggen method to initialize the logger
obj.qi_exercise()  # Call the connectionsetup method
