import os
import yaml
from selenium import webdriver
from selenium.webdriver.chrome.service import Service


def get_exe_yaml():
    exe_yaml_dict()
    messages_dict = exe_yaml_dict()
    return messages_dict


def exe_yaml_dict():
    '''
    Returns dict by reading yaml file
    :return:
    '''
    current_path = os.path.abspath(os.path.dirname(__file__))
    file_path = current_path + "\\Resource\\resource.yaml"
    yaml_dict = {}
    if os.path.exists(file_path):
        with open(file_path, "r") as resource_yaml_fh:
            yaml_dict = yaml.safe_load(resource_yaml_fh)
    else:
        err_msg = "Specified file {} does not exist ".format(file_path)
        raise Exception(err_msg)
    return yaml_dict


def appURL():
    url = get_exe_yaml()
    # ApplicationURL
    app_URL = url['app_url']
    return app_URL


def close_browser(self):
    driver = webdriver.Chrome()
    # Close the C2V tab
    driver.close()


def yaml_msg(value):
    config = get_exe_yaml()
    message = config[value]
    return message
