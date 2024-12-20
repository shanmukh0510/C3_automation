import json
import requests
from datetime import datetime
import os
import time
import psutil
import subprocess

class JsonOperations:
    def __init__(self,path):
        self.path =path
    def read_file(self):
        with open(self.path, "r") as rf:
            values = json.load(rf)
        return values
    def update_file(self,values):
        with open(self.path, "w") as outfile:
            json.dump(values, outfile)
    # def CreateResultJson(self,Mode,project):
    #     #create json file for report
    #     now = datetime.now()
    #     timestamp = now.strftime("%d%m%Y_%H%M%S")
    #     reponame = f'{Mode}_{project}_{timestamp}_Offline'
    #     file ='./Results'
    #     path2 = file+'\\'+reponame+'.json'
    #     if os.path.exists(path2):
    #         file_object = open(path2, "w")
    #         file_object.truncate(0)
    #     else:
    #         file_object = open(path2, "w")
    #     #Adding a empty list in result json
    #     li = []
    #     with open(file+'\\'+reponame+'.json', "w") as outfile:
    #         json.dump(li, outfile, default=self.defaultconverter)
    #     #update path in TCP
    #     TCP["test_config_data"]["Report_path"] = str(os.path.abspath(file)).replace("\\", "\\\\")+'\\'+reponame+'.json'
    #     with open('Test_config_properties.json', "w") as outfile:
    #         json.dump(TCP, outfile, default=self.defaultconverter)

    def defaultconverter(o):
        if isinstance(o, datetime.datetime):
            return o.__str__()
        

class APIOperations:
    def __init__(self,url,pathparam=None,retype = None,files =None,param1=None,param2=None,json=None):
        self.url = url
        # self.port = port
        self.pathparam=pathparam
        self.retype = retype
        self.files = files
        self.param1 = param1
        self.param2 =param2
        self.json = json
    def GetRequest(self):
        try:
            url1=self.url
            if self.pathparam is not None: url1= str(url1)+f'/{self.pathparam}'
            if self.param1 is not None: url1=url1.replace('#param1#',str(self.param1))
            if self.param2 is not None: url1=url1.replace('#param2#',str(self.param2))
            # print(url1)
            resp = requests.get(url1)
            if resp:
                if self.retype == 'json':
                    return resp.json()
                elif self.retype == 'text':
                    return resp.text
                else: return resp.status_code
            return None
        except Exception as e:
            print(e)
    def PutRequest(self):
        try:
            # url=self.url.replace("#port#",str(self.port))
            # print(url)
            if self.pathparam is not None: url1= str(url1)+f'/{self.pathparam}'
            if self.files is not None:
                resp = requests.put(self.url,files=self.files)
            elif self.json is not None:
                resp = requests.put(self.url,json=self.json)
            else:
                resp = requests.put(self.url)
            return int(resp.status_code)
        except Exception as e:
            print(e)
    def PostRequest(self):
        try:
            if self.json is not None:
                resp = requests.post(self.url,json=self.json)
            return resp.status_code
        except Exception as e:
            print(e)

class GeneralMethods:
    def GetFloatFromStr(strg):
        appl = ['0','1','2','3','4','5','6','7','8','9','.']
        val = []
        id = 0
        while id < len(strg):
            if strg[id] in appl:
                # print('id',id)
                tid = id
                v =[]
                while tid < len(strg):
                    # print('tid',tid)
                    if strg[tid] in appl:
                        v.append(strg[tid])
                    else:
                        break
                    tid+=1
                val.append(float(''.join(v)))
                id=tid
            id+=1
        return val

class Server:
    def __init__(self, Mode):
        self.Mode = Mode
        self.app_folder = os.path.join("C:\\", "Program Files", "GRL", "GRL-WP-TPR-C3", "AppFiles") if self.Mode=="TPR" else  os.path.join("C:\\", "Program Files", "GRL", "GRL-C3-MP-TPT", "AppFiles")
    def is_process_running(self, process_name):
        for process in psutil.process_iter():
            if process.name().lower() == process_name.lower():
                return True
        return False
    def open_C3_server_application(self):
        """
        Open C3 server application if it's not already running
        """
        process_name = "C3BrowserApp.exe"
        if not self.is_process_running(process_name):
            try:
                subprocess.run(["start", "cmd", "/c", process_name], cwd= self.app_folder, shell=True, check=True)
                time.sleep(10)
            except subprocess.CalledProcessError:
                print(f"{process_name} not found. Make sure the application is installed.")
            except Exception as e:
                print(f"An error occurred while opening the application: {e}")
        else:
            print(f"{process_name} is already running.")

    def close_C3_server_application(self):
        """
        Close C3 server application if it's running
        """
        process_name = "C3BrowserApp.exe"
        if self.is_process_running(process_name):
            try:
                subprocess.run(["taskkill", "/f", "/im", process_name], check=True)
                time.sleep(5)
            except subprocess.CalledProcessError:
                print(f"An error occurred while closing {process_name}.")
            except Exception as e:
                print(f"An error occurred while closing the application: {e}")
        else:
            print(f"{process_name} is not running.")



