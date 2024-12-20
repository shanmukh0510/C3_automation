import csv
import subprocess
import sys
import tkinter as tk
from tkinter import font,messagebox,ttk
from tkinter import filedialog
from tkinter import Label, Entry, Button, Toplevel
import traceback
from Scripts.offlineValidaionC3TPR import OfflineValidationC3TPR
from Scripts.offlineValidationC3TPT import OfflineValidationC3TPT
from Scripts.MainModule import JsonOperations,APIOperations,GeneralMethods,Server
from Scripts.CSVReports import CSVreport
from Scripts.OtherReports import XLreport
from Scripts.RunTests import RunTests
from Scripts.ReportAnly import JsonReports
import tkfilebrowser
from tkinter.filedialog import askopenfilename
import datetime,time
from datetime import datetime,date
import json
import os

class MPPGUI(tk.Tk):    
    def __init__(self):
        super().__init__()
        #Get inputs from JSON
        self.Jsettings = JsonOperations('json/setting.json')
        self.JsettingsData =self.Jsettings.read_file()
        self.Jtester = JsonOperations('json/Tester.json')
        self.JtesterData =self.Jtester.read_file()
        self.Japi = JsonOperations('json/Xpath.json')
        JapiDatatemp =self.Japi.read_file()
        self.JapiData = JapiDatatemp['API']
        self.JQI = JsonOperations('json/QIconfig.json')
        self.JQIData = self.JQI.read_file()
        self.JMOI = JsonOperations('json/MOIJson.json')
        self.JMOIData = self.JMOI.read_file()
        self.JTestConf = JsonOperations('json/TestConfig.json')
        self.JTestConfData = self.JTestConf.read_file()
        self.JTCP = JsonOperations('json/Test_config_properties.json')
        self.JTCPData = self.JTCP.read_file()
        self.JLogs = JsonOperations("json/DebugLogs.json")
        self.JLogsData = self.JLogs.read_file()
        #clear Logs
        self.JLogsData.clear()
        self.JLogs.update_file(self.JLogsData)
        #Process list
        self._stop_flag = False
        self.progLogs = []
        self.TestStartTime = None
    def CreateAPP(self):
        # runUI = Run(self)
        #main setup
        self.title(f"C3 Test Automation | Version : {self.JsettingsData['SWversion']}")
        self.geometry("1050x795")  
        self.iconbitmap("Resources\\img\\GRLPFO.ico")
        self.resizable(False,False)
        #Fonts
        self.FT12BW = font.Font(family='Calibri', size=12, weight='bold')
        self.FT8BW = font.Font(family='Calibri', size=8, weight='bold')
        self.FT10BW = font.Font(family='Calibri', size=10, weight='bold')
        self.FT15BW = font.Font(family='Calibri', size=15, weight='bold')
        #Widget menu
        self.SM1_frame = Menu(self,height=795,width=100,bg='#23275C',x=0,y=0)
        self.SM2_frame = Menu(self,height=795,width=950,bg='#202325',x=100,y=0)
        #Add Combo to choose Mode
        self.Mode = self.JsettingsData['Mode']
        self.TPRTGIMG = tk.PhotoImage(file='./Resources/img/TPR.png')
        self.TPTTGIMG = tk.PhotoImage(file='./Resources/img/TPT.png')
        self.Modeswitch = Buttons(self.SM1_frame,x=6,y=20,height=32,width=80,bg='#23275C',command=self.SwitchMode)
        self.Modeswitch['image']=self.TPRTGIMG if self.Mode=='TPR' else self.TPTTGIMG
        #Version selection
        Labels(self.SM1_frame,text="Certification:",x=2,y=63,width=13,bg='#23275C',fg='#FFFFFF',font=self.FT10BW)
        self.VerCB = Combo(self.SM1_frame,width=12,state="readonly",font=self.FT10BW,val=self.JMOIData['Versions'][self.Mode],bg='#202325',fg='#FFFFFF',x=2,y=85,selectedVal=self.JMOIData['Versions'][self.Mode][0])
        print(self.VerCB.get())
        self.VerCB.bind("<<ComboboxSelected>>",self.RestoreRun)
        #PowerProfileSelection
        Labels(self.SM1_frame,text="PowerProfile:",x=2,y=108,width=13,bg='#23275C',fg='#FFFFFF',font=self.FT10BW)
        self.PPCB = Combo(self.SM1_frame,width=12,state="readonly",font=self.FT10BW,val=self.JMOIData['PowerProfile'][self.Mode],bg='#202325',fg='#FFFFFF',x=2,y=130,selectedVal="BPP")   
        # print(self.PPCB.get())
        self.PPCB.bind("<<ComboboxSelected>>",self.RestoreRun)
        #Main Menu
        img_run = tk.PhotoImage(file='./Resources/img/runbtn.png')
        Buttons(self.SM1_frame,image=img_run,bg='#23275C',x=30,y=175,command=lambda:Run(self))
        img_ip = tk.PhotoImage(file='./Resources/img/ipbtn.png')
        Buttons(self.SM1_frame,image=img_ip,bg='#23275C',x=30,y=245)
        img_rp = tk.PhotoImage(file='./Resources/img/rpbtn.png')
        Buttons(self.SM1_frame,image=img_rp,bg='#23275C',x=30,y=312,command=lambda:Reports(self))
        img_st = tk.PhotoImage(file='./Resources/img/stbtn.png')
        Buttons(self.SM1_frame,image=img_st,bg='#23275C',x=30,y=385,command=lambda:Settings(self))
        img_import = tk.PhotoImage(file='./Resources/img/import.png')
        Buttons(self.SM1_frame,image=img_import,bg='#23275C',x=30,y=461, command=self.open_file_dialog)
        img_export = tk.PhotoImage(file='./Resources/img/export.png')
        Buttons(self.SM1_frame,image=img_export,bg='#23275C',x=30,y=535, command=self.export)
        img_ui = tk.PhotoImage(file='./Resources/img/UIX1.png')
        Buttons(self.SM1_frame,image=img_ui,bg='#23275C',x=30,y=615,command=lambda:UiUx(self))
        img_ref = tk.PhotoImage(file='./Resources/img/refresh.png')
        Buttons(self.SM1_frame,image=img_ref,bg='#23275C',x=39,y=683, command=self.refresh_window)
        #Add logo
        # Labels(self.SM1_frame,text=self.JsettingsData['SWversion'],x=1,y=700,width=15,bg='#23275C',fg='#FFFFFF')
        grllogo = tk.PhotoImage(file='./Resources/img/grl.png')
        logo_frame = Menu(self.SM1_frame,height=50,width=80,bg='#23275C',x=10,y=740)
        Labels(logo_frame,x=0,y=0,img=grllogo,bg='#23275C')
        tk.Label(logo_frame,image=grllogo,background="#23275C").place(x=0,y=0)
        # off = Run(self)
        # off.OfflineValidation()
        # Run(self)
        self.mainloop()

    def open_file_dialog(self):
        # Open file dialog and get selected file path
        json_file_path  = filedialog.askopenfilename()
        if json_file_path :
            print("Selected file:", json_file_path)
            with open(json_file_path, "r") as file:
                data = json.load(file)
                if all(res in data for res in ["Header","QIconfig","TestConfig"]):
                    self.JsettingsData['Mode'] = data["Header"]['Mode']
                    self.JsettingsData['Certification']=data["Header"]['Certification']
                    self.JsettingsData['powerProfile']=data["Header"]['powerProfile']
                    self.Jsettings.update_file(self.JsettingsData)
                    self.JQIData[data["Header"]["Mode"]] = data["QIconfig"]
                    self.JQI.update_file(self.JQIData)
                    self.JTestConfData[data["Header"]["Mode"]] = data["TestConfig"]
                    self.JTestConf.update_file(self.JTestConfData)
                    self.refresh_window()
                else:messagebox.showinfo("File Upload","Invalid JSON file selected")
    def refresh_window(self):
        python = sys.executable
        os.execl(python, python, * sys.argv)

    def RestoreRun(self,ts):
        # Run.update_logs("UI",str(ts.widget.get()))
        Run(self)
    def SwitchMode(self):
        if self.Mode=='TPT':
            self.Modeswitch['image']=self.TPRTGIMG  
            self.Mode=self.JsettingsData['Mode']='TPR'
        else:
            self.Modeswitch['image']=self.TPTTGIMG
            self.Mode=self.JsettingsData['Mode']='TPT'
        self.Jsettings.update_file(self.JsettingsData)
        self.VerCB['values'] = self.JMOIData['Versions'][self.Mode]
        self.PPCB['values'] = self.JMOIData['PowerProfile'][self.Mode]
        self.VerCB.set(self.JMOIData['Versions'][self.Mode][0])
        self.PPCB.set(self.JMOIData['PowerProfile'][self.Mode][0])
        self.RestoreRun(self)
    def ClearFrame(self,frm):
        if len(frm.winfo_children()) > 0:
            for wdgt in frm.winfo_children():
                wdgt.destroy()

    def export(self):
        data = {"Header": {"Mode":self.Mode,"Certification":self.VerCB.get(),"powerProfile":self.PPCB.get()},"QIconfig":self.JQIData[self.Mode],"TestConfig":self.JTestConfData[self.Mode]}
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_json_filename = f'Export_{self.Mode}_{self.VerCB.get()}{self.PPCB.get()}_{timestamp}.json'
        # Create a new JSON file with the data
        with open(new_json_filename, 'w') as file:
            json.dump(data, file, indent=4)
        print("New JSON file created for TPT mode:", new_json_filename)
class Run(MPPGUI):
    def __init__(self,master):
        self = self
        self.master = master    
        self.master.ClearFrame(self.master.SM2_frame)
        self.CreateRUNUI()  
        self.update_logs("UI",f"Mode switched to {self.master.Mode}")
        self.TesterConnect()
    #UI Operations
    def CreateRUNUI(self):
        #create frames for runs
        self.RN_FR1 = Menu(self.master.SM2_frame,height=150,width=300,bg='#343638',x=5,y=5)
        self.RN_FR2 = Menu(self.master.SM2_frame,height=625,width=300,bg='#343638',x=5,y=160)
        self.RN_FR3 = Menu(self.master.SM2_frame,height=450,width=290,bg='#343638',x=310,y=5)
        self.RN_FR4 = Menu(self.master.SM2_frame,height=350,width=340,bg='#343638',x=605,y=5)
        self.RN_FR5 = Menu(self.master.SM2_frame,height=140,width=635,bg='#343638',x=310,y=460)
        self.RN_FR6 = Menu(self.master.SM2_frame,height=180,width=635,bg='#343638',x=310,y=605)
        self.RN_FR7 = Menu(self.master.SM2_frame,height=100,width=340,bg='#343638',x=605,y=356)
        
        #Add Connect Tester UI
        self.PutTestConnectionUI()
        #Add Test QI inputs UI
        self.PutQiInputUI()
        #Add test selection
        self.PutTestSel()
        #Add List Tests UI
        self.PutListTests()
        #Add Run Tests UI
        self.PutRunTests()
        #Add Offline Validation UI
        self.PutOfflineValUI()
        #Add Logs UI
        self.LogsUI()
    def PutTestConnectionUI(self):
        # self.master
        self.master.ClearFrame(self.RN_FR1)
        Labels(self.RN_FR1,text="Connect Tester",x=0,y=0,bg='#999999',fg="#ffffff",width=42,font=self.master.FT10BW)
        self.TesterIP = Entries(self.RN_FR1,width=20,x=5,y=30,font=self.master.FT12BW,textvar=self.master.JtesterData[self.master.Mode]['TesterIP'],bg='#23275C',fg='#FFFFFF')
        Buttons(self.RN_FR1,text='Connect',x=170,y=30,font=self.master.FT10BW,command=self.TesterConnect)
        Labels(self.RN_FR1,text=f"Status    :{self.master.JtesterData[self.master.Mode]['status']}",x=5,y=65,fg='#FFFFFF',bg='#343638',font=self.master.FT10BW)
        Labels(self.RN_FR1,text=f"BoardNo   :{self.master.JtesterData[self.master.Mode]['BoardNo']}",x=5,y=85,fg='#FFFFFF',bg='#343638',font=self.master.FT10BW)
        Labels(self.RN_FR1,text=f"SWVersion :{self.master.JtesterData[self.master.Mode]['SWVersion']}",x=5,y=105,fg='#FFFFFF',bg='#343638',font=self.master.FT10BW)
        Labels(self.RN_FR1,text=f"FWversion :{self.master.JtesterData[self.master.Mode]['FWversion']}",x=5,y=125,fg='#FFFFFF',bg='#343638',font=self.master.FT10BW)   
    def PutQiInputUI(self):
        self.master.ClearFrame(self.RN_FR2)
        Labels(self.RN_FR2,text="Qi Configurations",x=0,y=0,bg='#999999',fg='#ffffff',width=42,font=self.master.FT10BW)
        inputs = self.master.JMOIData['TestIP'][self.master.Mode]
        rw = 27
        for key,value in inputs.items():
            Labels(self.RN_FR2,text=key,font=self.master.FT10BW,x=2,y=rw,width=20,bg='#343638',fg='#FFFFFF',anchor=tk.E)
            if value['Type'] =='TextBox':
                Entries(self.RN_FR2,font=self.master.FT10BW,name=value['key'],x=150,y=rw,width=20,textvar=self.master.JQIData[self.master.Mode][value['key']],bg='#23275C',fg='#FFFFFF')
                #print(self.master.JQIData[self.master.Mode][value['key']])
            if value['Type'] =='List':
                ListBx(self.RN_FR2,width=20,height=3,font=self.master.FT10BW,name=value['key'],x=150,y=rw,bg='#23275C',fg='#FFFFFF',values=value['values'],selectedVal=self.master.JQIData[self.master.Mode][value['key']])
                rw=rw+40
            elif value['Type'] =='Combo':
                Combo(self.RN_FR2,width=18,state="readonly",font=self.master.FT10BW,val=value['values'],name=value['key'],bg='#23275C',fg='#FFFFFF',x=150,y=rw,selectedVal =self.master.JQIData[self.master.Mode][value['key']] )
            elif value['Type'] =='Check':
                CheckBtn(self.RN_FR2,font=self.master.FT10BW,name=value['key'],x=150,y=rw,bg='#343638',fg='#FFFFFF',selectedVal=self.master.JQIData[self.master.Mode][value['key']])
            rw+=21
        # Buttons(self.RN_FR2,text='Load Opti. Data',x=50,y=rw+15,font=self.master.FT10BW,command=self.LoadOptData)
        Buttons(self.RN_FR2,text='Refresh',x=150,y=rw+15,font=self.master.FT10BW,command=self.PutQiInputUI)
        Buttons(self.RN_FR2,text='Update',x=220,y=rw+15,font=self.master.FT10BW,command=self.UpdateQIJSON)
    def LoadOptData(self):
        PutcoilAPI = APIOperations(url=self.master.JapiData[self.master.Mode]['PutOptimumCoilValues'])
        APPstatusAPI = APIOperations(url=self.master.JapiData[self.master.Mode]['PutApplicationActiveStatus'])
        #Load Data
        filename = askopenfilename()
        if '.xml' in filename:
            with open(filename, mode ='r')as file:
                csvFile = csv.reader(file)
                for lines in csvFile:
                        if '<value>' in lines[0]:
                            val = GeneralMethods.GetFloatFromStr(lines[0])
                            self.UpdateProject("ts")
                            PutcoilAPI.json = {"coilValue":[{"key":"MPP_TPR1","value":str(val[0])}],"sSCheck":False}
                            print({"coilValue":[{"key":"MPP_TPR1","value":str(val[0])}],"sSCheck":False})
                            res= PutcoilAPI.PutRequest()
                            APPstatusAPI.PutRequest()
                            print(res)
                            #Enable SS check in qi confi
                            self.master.JQIData[self.master.Mode]['ssCheckForTestcases']=True
                            self.master.JQI.update_file(self.master.JQIData)
                            tk.messagebox.showinfo("Update info:","Optimum Coil Values updated: "+str(val[0]))
                            #reload form
                            self.PutQiInputUI()
        else:
            tk.messagebox.showinfo("File:","Wrong file format.")
    def PutTestSel(self):
        self.master.ClearFrame(self.RN_FR3)
        Labels(self.RN_FR3,text="Prepare Tests For Run",x=0,y=0,bg='#999999',fg='#ffffff',width=42,font=self.master.FT10BW)
        Phase = self.master.JMOIData['Chapters'][self.master.Mode][self.master.PPCB.get()]
        offset = self.master.JMOIData['Offset'][self.master.Mode][self.master.PPCB.get()]
        Labels(self.RN_FR3,text='Select Coils:',font=self.master.FT12BW,x=1,y=25,width=15,bg='#343638',fg='#FFFFFF',anchor=tk.W)
        rw=45
        for key,value in offset.items():
            CheckBtn(self.RN_FR3,font=self.master.FT10BW,name='o-'+str(value),text=value,x=1,y=rw,bg='#343638',fg='#FFFFFF')
            rw+=19
        rw=45
        Labels(self.RN_FR3,text='Select Phases:',font=self.master.FT12BW,x=130,y=25,width=15,bg='#343638',fg='#FFFFFF',anchor=tk.W)
        for key,value in Phase.items():
            CheckBtn(self.RN_FR3,font=self.master.FT10BW,name='c-'+str(value),text=value,x=130,y=rw,bg='#343638',fg='#FFFFFF')
            rw+=19
        Buttons(self.RN_FR3,text='Generate Tests',x=5,y=420,width=15,font=self.master.FT10BW,command=self.GenerateTestsForRun)
        # Buttons(self.RN_FR3,text='Config. Tester As DUT',x=130,y=len(Phase)*23,width=20,font=self.master.FT10BW,command=self.GenerateTestsForRun)
    def PutListTests(self):
        self.master.ClearFrame(self.RN_FR4)
        Labels(self.RN_FR4,text="View Test",x=0,y=0,bg='#999999',fg='#ffffff',width=49,font=self.master.FT10BW)
        pos = [i.replace(',','') for i in list(self.master.JMOIData['Offset'][self.master.Mode][self.master.PPCB.get()].values())]
        pos.append('Offline')
        Labels(self.RN_FR4,text='Select Coils :',font=self.master.FT12BW,x=1,y=25,width=15,bg='#343638',fg='#FFFFFF',anchor=tk.W)
        self.PosSelCombo = Combo(self.RN_FR4,width=28,state="readonly",font=self.master.FT10BW,val=pos,bg='#23275C',fg='#FFFFFF',x=120,y=30)
        Labels(self.RN_FR4,text='Select Project :',font=self.master.FT12BW,x=1,y=50,width=15,bg='#343638',fg='#FFFFFF',anchor=tk.W)
        self.OffValProjCB = Combo(self.RN_FR4,width=28,font=self.master.FT10BW,state="readonly",val=[],bg='#23275C',fg='#FFFFFF',x=120,y=50)
        self.TestListBox = ListBx(self.RN_FR4,width=47,height=15,font=self.master.FT10BW,x=3,y=75,bg='#23275C',fg='#FFFFFF',values=[])
        self.PosSelCombo.bind("<<ComboboxSelected>>",self.LoadPosTest)
        self.OffValProjCB.bind("<<ComboboxSelected>>",self.LoadOffTest)
        Buttons(self.RN_FR4,text='Keep Selected',width=22,x=3,y=325,font=self.master.FT10BW,command=self.KeepSelected)
        Buttons(self.RN_FR4,text='Remove Selected',width=22,x=175,y=325,font=self.master.FT10BW,command=self.RemoveSelected)      
    def LogsUI(self):
        self.master.ClearFrame(self.RN_FR7)
        UIlogs=[]
        for log in self.master.JLogsData:
            if log[1] == "UI":
                UIlogs.append(f"{str(log[0]).split(' ')[1].split('.')[0]} : {log[2]}")
        Labels(self.RN_FR7, text="Execution Status", x=0,y=0, bg='#999999',fg='#ffffff', width=55, font=self.master.FT8BW, anchor="center")
        self.statusLB = ListBx(self.RN_FR7, width=55, height=5, x=0, y=23, font=self.master.FT8BW, bg='#23275C',fg='#FFFFFF', values=UIlogs[::-1])
    #backend functions
    def TesterConnect(self):
        TesterCon = APIOperations(url=self.master.JapiData[self.master.Mode]['ConnectionSetup'],pathparam=self.TesterIP.get(),retype='json')
        testerinfo = TesterCon.GetRequest()
        #print(testerinfo)
        if testerinfo is not None:
            self.master.JtesterData[self.master.Mode]['TesterIP'] = testerinfo['testerIpAddress']
            self.master.JtesterData[self.master.Mode]['status'] = testerinfo['testerStatus']
            self.master.JtesterData[self.master.Mode]['BoardNo'] = testerinfo['serialNumber']
            self.master.JtesterData[self.master.Mode]['FWversion'] = testerinfo['firmwareVersion']
            #get Sw
            SWver = APIOperations(url=self.master.JapiData[self.master.Mode]['GetSoftwareVersion'],retype='text')
            SWverinfo = SWver.GetRequest()
            self.master.JtesterData[self.master.Mode]['SWVersion'] = SWverinfo if SWverinfo is not None else 'NA'
            self.master.Jtester.update_file(values=self.master.JtesterData)
            # print(testerinfo)
            if testerinfo['testerStatus'] == 'Connected':
                tk.messagebox.showinfo("Tester Connection:","Connected Successfully.")
                # self.update_logs(f"Connecting to the C3 {self.master.Mode} Tester with IP:{self.master.TesterIP.get()}..")
                #put certification and power profile filters
                if self.Mode=='TPR':
                    self.CallAPI(self.master.JapiData[self.master.Mode]['PutCertificationFilter']+f'/{self.master.VerCB.get()}')
                    self.CallAPI(self.master.JapiData[self.master.Mode]['PutPowerProfile']+f'/{self.master.PPCB.get()}')
                else:
                    self.CallAPI(self.master.JapiData[self.master.Mode]['PutCertificationFilterToggle']+f'/{self.master.VerCB.get()}')
                    self.CallAPI(self.master.JapiData[self.master.Mode]['PutCertificationFilterToggle']+f'/{self.master.PPCB.get()}')
                #Enable API mode
                # apiobj = APIOperations(url=self.master.JapiData[self.master.Mode]['EnableAPIMode'])
                # apiobj.PutRequest()
            else: 
                tk.messagebox.showinfo("Tester Connection:","Not Connected.")
                # self.update_logs("Connection Failed")
        else:
            #call server open
            #os.system('py ./Server.py')
            # subprocess.Popen(["python", ".\\Scripts\\Server.py"])
            server_instance = Server(self.master.Mode)
            server_instance.open_C3_server_application()
            # time.sleep(15)
            # self.TesterConnect()
        self.PutTestConnectionUI()
    def PutRunTests(self):
        self.master.ClearFrame(self.RN_FR5)
        Labels(self.RN_FR5,text="Run Test",x=0,y=0,bg='#999999',fg='#ffffff',width=90,font=self.master.FT10BW)
        offset = self.master.JMOIData['Offset'][self.master.Mode][self.master.PPCB.get()]
        Labels(self.RN_FR5,text='Select Coils:',font=self.master.FT12BW,x=1,y=25,width=15,bg='#343638',fg='#FFFFFF',anchor=tk.W)
        rw=115
        yval = 25
        cnt=0
        for key,value in offset.items():
            CheckBtn(self.RN_FR5,font=self.master.FT8BW,name='of-'+str(key),text=key,x=rw,y=yval,bg='#343638',fg='#FFFFFF')
            rw+=52
            cnt+=1
            if cnt==11:
                yval+=25
                rw=115
                cnt=0
        Labels(self.RN_FR5,text='Select/Type Project:',font=self.master.FT12BW,x=1,y=75,width=20,bg='#343638',fg='#FFFFFF',anchor=tk.W)
        self.proSelCB = Combo(self.RN_FR5,width=20,font=self.master.FT10BW,val=self.GetProjectnameFromRepDir(),bg='#23275C',fg='#FFFFFF',x=150,y=80,selectedVal=self.master.JsettingsData['Online_validation'][self.master.Mode]['ProjectName'])
        Labels(self.RN_FR5,text='Repeat Count:',font=self.master.FT12BW,x=315,y=75,width=20,bg='#343638',fg='#FFFFFF',anchor=tk.W)
        self.Repeatcount=Entries(self.RN_FR5,font=self.master.FT10BW,x=420,y=80,width=5,bg='#23275C',fg='#FFFFFF',textvar=self.master.JQIData[self.master.Mode]['repCount'])
        
        self.TADCk = CheckBtn(self.RN_FR5,font=self.master.FT12BW,name="enableTAD",text="Enable Tester As DUT",x=1,y=100,bg='#343638',fg='#FFFFFF',command=lambda:self.PopupMsg("info","Ensure both TPT and TPR hardware connected using the tool."))
        Labels(self.RN_FR5,text='Filters:',font=self.master.FT12BW,x=180,y=103,width=10,bg='#343638',fg='#FFFFFF',anchor=tk.W)
        self.TADfilter = Combo(self.RN_FR5,width=20,state="readonly",font=self.master.FT10BW,val=["Automation Tests","Excerciser Tests"],selectedVal="Automation Tests",bg='#23275C',fg='#FFFFFF',x=240,y=105)
        Buttons(self.RN_FR5,text='Run Tests - API',width=15,x=410,y=105,font=self.master.FT10BW,command= self.RunTest)
        Buttons(self.RN_FR5,text='Force Stop',width=15,x=530,y=105,font=self.master.FT10BW)
        self.proSelCB.bind("<KeyRelease>",self.UpdateProject)
        self.Repeatcount.bind("<KeyRelease>",self.UpdateRepeatCount)
        self.proSelCB.bind("<<ComboboxSelected>>",self.UpdateProject)
    def PutOfflineValUI(self):
        self.master.ClearFrame(self.RN_FR6)
        Labels(self.RN_FR6,text="Offline Validation",x=0,y=0,bg='#999999',fg='#ffffff',width=90,font=self.master.FT10BW)
        Buttons(self.RN_FR6,text='Browse & Add Projects',width=30,x=1,y=25,font=self.master.FT10BW,command=self.ProjAddOffValidation)
        Buttons(self.RN_FR6,text='Remove Selected',width=30,x=220,y=25,font=self.master.FT10BW,command=self.RemoveSelectedOffline)
        Buttons(self.RN_FR6,text='Clear All',width=30,x=440,y=25,font=self.master.FT10BW,command=self.ClearAllOffline)
        self.OfflineListBox = ListBx(self.RN_FR6,width=90,height=5,font=self.master.FT10BW,x=1,y=50,bg='#23275C',fg='#FFFFFF',values=self.master.JsettingsData['Offline_validation']['json_path'][self.master.Mode])
        Buttons(self.RN_FR6,text='Prepare Validation',width=30,x=220,y=145,font=self.master.FT10BW,command=self.PrepareOffValidation)
        Buttons(self.RN_FR6,text='Start Validation-API',width=30,x=440,y=145,font=self.master.FT10BW,command=self.OfflineValidation)
    #backend Operations
    def GenerateTestsForRun(self):
        phaselist = []
        offsetlist = []
        if len(self.RN_FR3.winfo_children()) > 0:
            for wdgt in self.RN_FR3.winfo_children():
                if wdgt.winfo_class() in ['Checkbutton']:
                    if 'c-' in wdgt.winfo_name():
                        if wdgt.getvar(wdgt.winfo_name())=='1':
                            print(wdgt.winfo_name())
                            phaselist.append(wdgt.winfo_name().split('-')[1])
                    elif 'o-' in wdgt.winfo_name():
                        if wdgt.getvar(wdgt.winfo_name())=='1':
                            offsetlist.append((wdgt.winfo_name().split('-')[1]))
        # print(phaselist)
        # print(offsetlist)
        if len(phaselist)>0 and len(offsetlist)>0:
            #clear Existing data
            for pos in self.master.JTestConfData[self.master.Mode]:
                if pos != 'Offline':
                    self.master.JTestConfData[self.master.Mode][pos].clear()
            for test in self.master.JMOIData[self.master.Mode]:
                # if str(self.master.Mode)+'_TD_' in test:
                # print(test)
                if self.master.JMOIData[self.master.Mode][test]['TC_Chapter'] in phaselist and self.master.JMOIData[self.master.Mode][test]['Coils'] in offsetlist and self.master.PPCB.get() in self.master.JMOIData[self.master.Mode][test]['PowerProfile']:
                    self.master.JTestConfData[self.master.Mode][self.master.JMOIData[self.master.Mode][test]['Coils']].append(test)
        self.master.JTestConf.update_file(self.master.JTestConfData)
    def UpdateQIJSON(self):
        remarks = []
        errors = False
        if len(self.RN_FR2.winfo_children()) > 0:
            for wdgt in self.RN_FR2.winfo_children():
                if wdgt.winfo_class() in ['Entry','Listbox','TCombobox','Checkbutton']:
                    try:
                        if wdgt.winfo_name() in ['maximumPower']:
                            val = int(wdgt.get())
                            if val > 0 and val<=15:
                                self.master.JQIData[self.master.Mode][wdgt.winfo_name()] = val
                            else:
                                remarks.append(f"{wdgt.winfo_name()} not in limit [0-15]")
                                errors=True
                        elif wdgt.winfo_name() in ['noOfCoils']:
                            val = int(wdgt.get())
                            if val >= 0 and val<=10:
                                self.master.JQIData[self.master.Mode][wdgt.winfo_name()] = str(val)
                            else:
                                remarks.append(f"{wdgt.winfo_name()} not in limit [<10]")
                                errors=True
                        elif wdgt.winfo_name() in ['kest_P1_MPTPT','kest_P2_MPTPT']:
                            val = float(wdgt.get())
                            if val >= 0.40 and val <= 0.96 or val in [0,0.0]:
                                self.master.JQIData[self.master.Mode][wdgt.winfo_name()] = val
                            else:
                                remarks.append(f"{wdgt.winfo_name()} not in limit [0.40-0.96]")
                                errors=True
                        elif wdgt.winfo_name() in ['prxCloakRetry']:
                            if self.master.JQIData[self.master.Mode]['pRx_detectPing']=='Yes':
                                val = int(wdgt.get())
                                if val >= 0 and val <= 100:
                                    self.master.JQIData[self.master.Mode][wdgt.winfo_name()] = val
                                else:
                                    remarks.append(f"{wdgt.winfo_name()} not in limit [0-100] or pRx_detectPing not set Yes")
                                    errors=True
                            else:
                                remarks.append(f"pRx_detectPing not set to yes,prxCloakRetry are ignored")
                        elif wdgt.winfo_name() in ['cloakingReason']:
                            if self.master.Mode == 'TPT':
                                if self.master.JQIData[self.master.Mode]['isCloaking']=='Yes':
                                    valindex = wdgt.curselection()
                                    if len(valindex)>0:
                                        val = [wdgt.get(i) for i in valindex]
                                        self.master.JQIData[self.master.Mode][wdgt.winfo_name()].clear()
                                        self.master.JQIData[self.master.Mode][wdgt.winfo_name()] = val
                                    else:
                                        self.master.JQIData[self.master.Mode][wdgt.winfo_name()].clear()
                                else:
                                    self.master.JQIData[self.master.Mode][wdgt.winfo_name()].clear()
                                    remarks.append(f"isCloaking not set to yes,cloakingReason are ignored")
                            else:
                                if self.master.JQIData[self.master.Mode]['supportATNCloaking']==True:
                                    valindex = wdgt.curselection()
                                    if len(valindex)>0:
                                        val = [wdgt.get(i) for i in valindex]
                                        self.master.JQIData[self.master.Mode][wdgt.winfo_name()].clear()
                                        self.master.JQIData[self.master.Mode][wdgt.winfo_name()] = val
                                    else:
                                        self.master.JQIData[self.master.Mode][wdgt.winfo_name()].clear()
                                else:
                                    self.master.JQIData[self.master.Mode][wdgt.winfo_name()].clear()
                                    remarks.append(f"supportATNCloaking not set to yes,cloakingReason are ignored")
                        elif wdgt.winfo_name() in ['isMultiTx','support25W','ssCheckForTestcases','isAuthSup','isNfcSupport','isGrqXcapSupport','isOutOfBand','isSimulIncomingAndOutgng','isNegSup']:
                            self.master.JQIData[self.master.Mode][wdgt.winfo_name()] =False if wdgt.getvar(wdgt.winfo_name())=='0' else True
                        elif wdgt.winfo_name() in ['supportedProps','supportedSRQProps','supportedADCProps','unpopulatedSlotNumbers']:
                            valindex = wdgt.curselection()
                            if len(valindex)>0:
                                val = [wdgt.get(i) for i in valindex]
                                self.master.JQIData[self.master.Mode][wdgt.winfo_name()].clear()
                                self.master.JQIData[self.master.Mode][wdgt.winfo_name()] = val
                            else:
                                self.master.JQIData[self.master.Mode][wdgt.winfo_name()].clear()
                        else:
                            self.master.JQIData[self.master.Mode][wdgt.winfo_name()] = wdgt.get()
                    except Exception as e:
                        errors=True
                        remarks.append(f"{wdgt.winfo_name()} "+str(e))
        rm = '|'.join(remarks) if len(remarks)> 0 else 'No remarks'
        if errors ==False:
            self.master.JQI.update_file(self.master.JQIData)
            self.PutQiInputUI()
            messagebox.showinfo("Updated:",rm)
        else:
            messagebox.showinfo("Not Updated:",rm)
    def LoadPosTest(self,ts):
        self.TestListBox.delete(0,tk.END)
        if self.PosSelCombo.get() not in ['Offline']:
            self.OffValProjCB['values']=[]
            self.OffValProjCB.set('')
            self.TestListBox.UpdateValues(self.master.JTestConfData[self.master.Mode][self.PosSelCombo.get()])
        else:
            if len(self.master.JTestConfData[self.master.Mode]['Offline'])>0:
                self.OffValProjCB['values']=list(self.master.JTestConfData[self.master.Mode]['Offline'].keys())
    def LoadOffTest(self,ts):
        self.TestListBox.delete(0,tk.END)
        if self.PosSelCombo.get() in ['Offline']:
            self.TestListBox.UpdateValues(self.master.JTestConfData[self.master.Mode]['Offline'][self.OffValProjCB.get()].keys())
    def KeepSelected(self):
        index = self.TestListBox.curselection()
        if len(index)>0:
            testcases = [self.TestListBox.get(i) for i in index]
            availabletc = list(self.TestListBox.get(0,tk.END))
            pos = self.PosSelCombo.get()
            ns_tests = list(set(availabletc) - set(testcases))
            if len(ns_tests)>0:
                if pos != 'Offline':
                    for tc in ns_tests:
                        self.master.JTestConfData[self.master.Mode][pos].remove(tc)
                    self.master.JTestConf.update_file(self.master.JTestConfData)
                    self.LoadPosTest(self.TestListBox) 
                else:
                    proj = self.OffValProjCB.get()
                    for tc in ns_tests:
                        del self.master.JTestConfData[self.master.Mode][pos][proj][tc]
                    self.master.JTestConf.update_file(self.master.JTestConfData)
                    self.LoadPosTest(self.TestListBox)  
                    self.LoadOffTest(self.OffValProjCB)         
    def RemoveSelected(self):
        index = self.TestListBox.curselection()
        if len(index)>0:
            testcases = [self.TestListBox.get(i) for i in index]
            pos = self.PosSelCombo.get()
            if len(testcases)>0:
                if pos != 'Offline':
                    for tc in testcases:
                        self.master.JTestConfData[self.master.Mode][pos].remove(tc)
                    self.master.JTestConf.update_file(self.master.JTestConfData)
                    self.LoadPosTest(self.TestListBox)
                else:
                    proj = self.OffValProjCB.get()
                    for tc in testcases:
                        del self.master.JTestConfData[self.master.Mode][pos][proj][tc]
                    self.master.JTestConf.update_file(self.master.JTestConfData)
                    self.LoadPosTest(self.TestListBox)
                    self.LoadOffTest(self.OffValProjCB)
    def RemoveSelectedOffline(self):
        index =self.OfflineListBox.curselection()
        proj = [self.OfflineListBox.get(i) for i in index]
        if len(proj)>0:
            for i in proj:
                self.master.JsettingsData['Offline_validation']['json_path'][self.master.Mode].remove(i)
            self.master.Jsettings.update_file(self.master.JsettingsData)
            self.OfflineListBox.UpdateValues(self.master.JsettingsData['Offline_validation']['json_path'][self.master.Mode])   
    def GetProjectnameFromRepDir(self):
        prolist=[]
        propath = self.master.JtesterData[self.master.Mode]['ReportPath']
        for file in os.listdir(propath):
            if 'V_2_0_1' in file:
                prolist.append(file.split('_')[0])
        return prolist
    def UpdateProject(self,ts):
        self.master.JsettingsData['Online_validation'][self.master.Mode]['ProjectName'] = self.proSelCB.get()
        self.master.Jsettings.update_file(self.master.JsettingsData)
        APIPutPowerProfile = APIOperations(url=self.master.JapiData[self.master.Mode]['PutPowerProfile'])
        APIPutCertificationFilter = APIOperations(url=self.master.JapiData[self.master.Mode]['PutCertificationFilter'])
        APIcreateProj = APIOperations(url=self.master.JapiData[self.master.Mode]['PutProjectFolder'],json={"projectName":self.master.JsettingsData['Online_validation'][self.master.Mode]['ProjectName'],"moiName":self.master.VerCB.get()})
        APIPutPowerProfile.PutRequest()
        APIPutCertificationFilter.PutRequest()
        res = APIcreateProj.PutRequest()
        # print("Project",res)
    def UpdateRepeatCount(self,ts):
        try:
            self.master.JQIData[self.master.Mode]['repCount'] = int(self.Repeatcount.get())
            self.master.JQI.update_file(self.master.JQIData)
        except Exception as e:
            print(e)
    def ProjAddOffValidation(self):
        jsonlist=[]
        foldernames = list(tkfilebrowser.askopendirnames(title="Select Project Folders"))
        if len(foldernames)>0:
            for path in foldernames:
                # if '_MPP_' in path:
                for root, dirs, files in os.walk(path):
                    for d in dirs:
                        if d.startswith("Run"):
                            if os.path.join(root, d) not in self.master.JsettingsData['Offline_validation']['json_path'][self.master.Mode]:
                                # print(os.path.join(root, d))
                                jsonlist.append(os.path.join(root, d))
            self.master.JsettingsData['Offline_validation']['json_path'][self.master.Mode].extend(jsonlist)
            self.master.Jsettings.update_file(self.master.JsettingsData)
            self.OfflineListBox.UpdateValues(self.master.JsettingsData['Offline_validation']['json_path'][self.master.Mode])
    def ClearAllOffline(self):
        self.master.JsettingsData['Offline_validation']['json_path'][self.master.Mode].clear()
        self.master.Jsettings.update_file(self.master.JsettingsData)
        self.OfflineListBox.delete(0,tk.END)
        self.master.JTestConfData[self.master.Mode]['Offline'].clear()
        self.master.JTestConf.update_file(self.master.JTestConfData)
        self.PutListTests()
    def PrepareOffValidation(self):
        try:
            TClist={}
            projects = self.master.JsettingsData['Offline_validation']['json_path'][self.master.Mode]
            if len(projects)>0:
                for pro in projects:
                    filepath = None
                    jsonpath = None
                    for root, dirs, files in os.walk(pro):
                        for file in files:
                            if file.endswith(".gproj") and file.__contains__("Run"):
                                filepath = os.path.join(root, file)
                            if file.endswith(".json") and file.__contains__("Run"):
                                jsonpath = os.path.join(root, file) 
                    print(filepath,jsonpath)
                    if filepath is not None and jsonpath is not None:
                        print("path",os.path.join(pro,filepath))
                        test = JsonOperations(os.path.join(pro,filepath))
                        testdata =test.read_file()
                        proname = str(filepath.split('\\')[len(filepath.split('\\'))-4])+'-'+str(filepath.split('\\')[len(filepath.split('\\'))-3])
                        if proname not in TClist:TClist[proname] ={}
                        for tcl in testdata['testBkpTestResultsandPath']:
                            if 'testinformation' in tcl:
                                if tcl['testinformation'] is not None:
                                    if tcl['testcaseDetails']['m_DisplayName'] is not None and tcl['testinformation']['TestResult'] not in [' ',None,'NotRun']:
                                        if any(self.master.JMOIData[self.master.Mode][i].get('Testcase_Name') == tcl['testcaseDetails']['m_DisplayName'] for i in self.master.JMOIData[self.master.Mode] if str(self.master.Mode)+"_TD_" in i):
                                            testpath = tcl['actualTracePath'].split('\\')
                                            TClist[proname][[i for i in self.master.JMOIData[self.master.Mode] if "TD_" in i and self.master.JMOIData[self.master.Mode][i].get('Testcase_Name') == tcl['testcaseDetails']['m_DisplayName']][0]]=[tcl['testcaseDetails']['m_DisplayName'],pro+'\\'+testpath[len(testpath)-2]+'\\'+testpath[len(testpath)-1],jsonpath]
                self.master.JTestConfData[self.master.Mode]['Offline'].clear()
                self.master.JTestConfData[self.master.Mode]['Offline']=TClist
                self.master.JTestConf.update_file(self.master.JTestConfData)
                self.PutListTests()
        except Exception as e:
            print(e)
    def OfflineValidation(self):
        self.update_logs("UI","Offline validation started.")
        TraceUPL = APIOperations(url=self.master.JapiData[self.master.Mode]['PutWaveformFile'])
        TCstatus = APIOperations(url=self.master.JapiData[self.master.Mode]['TCstatus'],retype='json')
        if len(self.master.JTestConfData[self.master.Mode]['Offline'])>0:
            for ProjRun in self.master.JTestConfData[self.master.Mode]['Offline']:
                # print(ProjRun)
                #Create Json for Results TBD--
                self.CreateResultJson(ProjRun)
                if len(self.master.JTestConfData[self.master.Mode]['Offline'][ProjRun])>0:
                   for tests in self.master.JTestConfData[self.master.Mode]['Offline'][ProjRun]:
                        self.update_logs("UI",f"Validating:{tests}")
                        TraceUPL.files = {"WaveformFile":open(self.master.JTestConfData[self.master.Mode]['Offline'][ProjRun][tests][1].replace('/','\\'),"rb")}
                        status = TraceUPL.PutRequest()
                        if status == 200:
                            t_end = time.time() + 60
                            while time.time() < t_end:
                                try:
                                    data = TCstatus.GetRequest()
                                    if data is not None:
                                        print(len(data['2']['displayDataChunk']))
                                        if len(data['2']['displayDataChunk'])>0:
                                            #call Validation
                                            if self.master.JMOIData[self.master.Mode][tests]['Status'] == True:
                                                if self.master.Mode == 'TPR':
                                                    OfflineValidationC3TPR(TestID=tests,ProjectJson=self.master.JTestConfData[self.master.Mode]['Offline'][ProjRun][tests][2],TracePath=self.master.JTestConfData[self.master.Mode]['Offline'][ProjRun][tests][1])
                                                elif self.master.Mode == 'TPT':
                                                    OfflineValidationC3TPT(TestID=tests,ProjectJson=self.master.JTestConfData[self.master.Mode]['Offline'][ProjRun][tests][2],TracePath=self.master.JTestConfData[self.master.Mode]['Offline'][ProjRun][tests][1])
                                            else: self.update_logs("UI",f'No Validation config for Test {tests}')
                                            break
                                except Exception as e:
                                    self.update_logs("sys",str(e))
                                    break
        self.update_logs("UI","Offline validation Ended.")
    def PopupMsg(self,head,msg):
        messagebox.showinfo(head, msg)
    def RunTest(self):
        print('Run tests')
        offsetlist = []
        if len(self.RN_FR5.winfo_children()) > 0:
            for wdgt in self.RN_FR5.winfo_children():
                if wdgt.winfo_class() in ['Checkbutton']:
                    if 'of-' in wdgt.winfo_name():
                        if wdgt.getvar(wdgt.winfo_name())=='1':
                            offsetlist.append((str(wdgt.winfo_name().split('-')[1])))
        if len(offsetlist)>0:
            fltr = {"Pos":offsetlist,"TAD":self.TADCk.getvar(self.TADCk.winfo_name()),"TADmode":self.TADfilter.get(),"PowerProfile":self.master.PPCB.get()}
            print(fltr)
            RunTests(fltr)
    def CreateResultJson(self,project):
        #create json file for report
        now = datetime.now()
        timestamp = now.strftime("%d%m%Y_%H%M%S")
        reponame = f'{self.master.Mode}_{project}_{timestamp}_Offline'
        path ="Results\\JsonReports\\"+reponame+'.json'
        li = []        
        resjson = JsonOperations(path)
        resjson.update_file(li)
        #update path in TCP
        print(str(os.path.abspath(path)))
        self.master.JTCPData["test_config_data"]["Report_path"] = str(os.path.abspath(path))
        self.master.JTCP.update_file(self.master.JTCPData)
    def CallAPI(self,URL):
        Obj = APIOperations(url=URL)
        if 'Put' in URL and 'PutPowerProfile' not in URL:
            status = Obj.PutRequest()
        else:
            status = Obj.GetRequest()
    def update_logs(self,logtype,log):
        dt_object = datetime.fromtimestamp(datetime.now().timestamp())
        self.master.JLogsData.append([str(dt_object),logtype,log])
        self.master.JLogs.update_file(self.master.JLogsData)
        if logtype == 'UI':self.LogsUI()
class Settings(MPPGUI):
    def __init__(self,master):
        self = self
        self.master = master
        self.master.ClearFrame(self.master.SM2_frame)
        self.CreateSettings()
    def CreateSettings(self):
        self.ST_FR1 = Menu(self.master.SM2_frame,height=650,width=300,bg='#343638',x=5,y=5)
class Reports(MPPGUI):
    def __init__(self,master):
        self=self
        self.master = master
        self.master.ClearFrame(self.master.SM2_frame)
        self.JCon = JsonOperations(self.master.JsettingsData['ConsolidatedJSON'])
        self.JConData = self.JCon.read_file()
        self.ReportMenu()
    def ReportMenu(self):
        self.RP_FR1 = Menu(self.master.SM2_frame,height=640,width=110,bg='#343638',x=5,y=5)
        self.RP_FR2 = Menu(self.master.SM2_frame,height=640,width=825,bg='#202325',x=120,y=5)
        #add menu buttons
        Labels(self.RP_FR1,text="Testing Reports",x=0,y=1,bg='#202325',fg='#FFFFFF',width=15,font=self.master.FT10BW)
        Buttons(self.RP_FR1,text='Validation Results',x=1,y=25,width=15,font=self.master.FT10BW,command=self.CreateReports)
        Labels(self.RP_FR1,text="Reports Comparison",x=0,y=50,bg='#202325',fg='#FFFFFF',width=15,font=self.master.FT10BW)
        Buttons(self.RP_FR1,text='JSON Comparison',x=1,y=75,width=15,font=self.master.FT10BW,command=self.JSONComparison)
        Buttons(self.RP_FR1,text='Golden Comparison',x=1,y=100,width=15,font=self.master.FT10BW)
        Labels(self.RP_FR1,text="Reports Merge",x=0,y=125,bg='#202325',fg='#FFFFFF',width=15,font=self.master.FT10BW)
        Buttons(self.RP_FR1,text='JSON Merge',x=1,y=150,width=15,font=self.master.FT10BW,command=self.JsonMerge)
        Labels(self.RP_FR1,text="Other Features",x=0,y=175,bg='#202325',fg='#FFFFFF',width=15,font=self.master.FT10BW)
        Buttons(self.RP_FR1,text='ASK/FSK Decode',x=1,y=200,width=15,font=self.master.FT10BW)
        Buttons(self.RP_FR1,text='Eye Plot Merge',x=1,y=225,width=15,font=self.master.FT10BW)
        Buttons(self.RP_FR1,text='BI Analysis',x=1,y=250,width=15,font=self.master.FT10BW,command=self.BIAnalysis)
             
    def CreateReports(self):
        self.RP_FR2_1 = Menu(self.RP_FR2,height=200,width=825,bg='#343638',x=0,y=0)
        self.RP_FR2_2 = Menu(self.RP_FR2,height=100,width=825,bg='#343638',x=0,y=205)
        self.RP_FR2_3 = Menu(self.RP_FR2,height=120,width=825,bg='#343638',x=0,y=310)
        #Add Reports Input form
        self.PutInput()
        self.PutReportSummary()
        self.PutReportMenu()   
    def JsonMerge(self):
        self.master.ClearFrame(self.RP_FR2)
        self.RP_FR2_1 = Menu(self.RP_FR2,height=400,width=825,bg='#343638',x=0,y=0)
        Labels(self.RP_FR2_1,text="Report Analysis with JSON",x=0,y=0,bg='#FFFFFF',width=120,font=self.master.FT10BW)
        Buttons(self.RP_FR2_1,text='Browse & Add Projects',width=30,x=1,y=25,font=self.master.FT10BW,command=lambda:self.open_Directory_path('JsonMerge'))
        Buttons(self.RP_FR2_1,text='Remove Selected',width=30,x=220,y=25,font=self.master.FT10BW,command=lambda:self.RemoveItemLB(self.JSONMrgListBox,'JsonMerge'))
        Buttons(self.RP_FR2_1,text='Clear All',width=30,x=440,y=25,font=self.master.FT10BW,command=lambda:self.ClearLB('JsonMerge'))
        self.JSONMrgListBox = ListBx(self.RP_FR2_1,width=117,height=20,font=self.master.FT10BW,x=1,y=50,bg='#23275C',fg='#FFFFFF',values=self.master.JsettingsData['JsonMerge']['JsonMergePath'])
        Buttons(self.RP_FR2_1,text='Merge & Generate JSON',width=30,x=1,y=375,font=self.master.FT10BW,command=JsonReports)
    def BIAnalysis(self):
        self.master.ClearFrame(self.RP_FR2)
        self.RP_FR2_1 = Menu(self.RP_FR2,height=400,width=825,bg='#343638',x=0,y=0)
        Labels(self.RP_FR2_1,text="Create JSON for BI Analysis",x=0,y=0,bg='#FFFFFF',width=120,font=self.master.FT10BW)
        Buttons(self.RP_FR2_1,text='Browse & Add Projects',width=30,x=1,y=25,font=self.master.FT10BW,command=lambda:self.open_Directory_path('BIAnly'))
        Buttons(self.RP_FR2_1,text='Remove Selected',width=30,x=220,y=25,font=self.master.FT10BW,command=lambda:self.RemoveItemLB(self.BIListBox,'BIAnly'))
        Buttons(self.RP_FR2_1,text='Clear All',width=30,x=440,y=25,font=self.master.FT10BW,command=lambda:self.ClearLB('BIAnly'))
        self.BIListBox = ListBx(self.RP_FR2_1,width=117,height=20,font=self.master.FT10BW,x=1,y=50,bg='#23275C',fg='#FFFFFF',values=self.master.JsettingsData['BIAnalyis'].keys())
        Buttons(self.RP_FR2_1,text='Merge & Generate JSON',width=30,x=1,y=375,font=self.master.FT10BW,command=self.GenerateBIreport2)
    def JSONComparison(self):
        self.master.ClearFrame(self.RP_FR2)
        self.RP_FR2_1 = Menu(self.RP_FR2,height=400,width=825,bg='#343638',x=0,y=0)
        Labels(self.RP_FR2_1,text="Compare JSON files with High Level Results",x=0,y=0,bg='#FFFFFF',width=120,font=self.master.FT10BW)
        Buttons(self.RP_FR2_1,text='Browse & Add JSON files',width=30,x=1,y=25,font=self.master.FT10BW,command=lambda:self.open_Directory_path('JsonComp'))
        Buttons(self.RP_FR2_1,text='Remove Selected',width=30,x=220,y=25,font=self.master.FT10BW,command=lambda:self.RemoveItemLB(self.JSONCompListBox,'JsonMerge'))
        Buttons(self.RP_FR2_1,text='Clear All',width=30,x=440,y=25,font=self.master.FT10BW,command=lambda:self.ClearLB('JsonMerge'))
        self.JSONCompListBox = ListBx(self.RP_FR2_1,width=117,height=20,font=self.master.FT10BW,x=1,y=50,bg='#23275C',fg='#FFFFFF',values=self.master.JsettingsData['JSONCompare'])
        Buttons(self.RP_FR2_1,text='Merge & Generate XLS',width=30,x=1,y=375,font=self.master.FT10BW,command=JsonReports)
    def PutInput(self):
        self.master.ClearFrame(self.RP_FR2_1)
        Labels(self.RP_FR2_1,text="Report Inputs",x=0,y=0,bg='#999999',fg='#ffffff',width=120,font=self.master.FT10BW)

        Labels(self.RP_FR2_1,text="Report Path:",x=5,y=28,fg='#FFFFFF',bg='#343638',width=10,font=self.master.FT10BW)
        self.ReportPath = Entries(self.RP_FR2_1,width=33,x=80,y=30,font=self.master.FT10BW,textvar=self.master.JTCPData['test_config_data']['ConsolidateReport'],bg='#23275C',fg='#FFFFFF')
        Buttons(self.RP_FR2_1,text='Browse',x=320,y=28,font=self.master.FT10BW)

        Labels(self.RP_FR2_1,text="SW Version :",x=5,y=60,fg='#FFFFFF',bg='#343638',width=15,font=self.master.FT10BW)
        self.SWCB = Combo(self.RP_FR2_1,width=14,state="readonly",font=self.master.FT10BW,bg='#23275C',fg='#FFFFFF',x=5,y=80,val=list(self.JConData.keys()))
        Labels(self.RP_FR2_1,text="FW Version :",x=130,y=60,fg='#FFFFFF',bg='#343638',width=15,font=self.master.FT10BW)
        self.FWCB = Combo(self.RP_FR2_1,width=14,state="readonly",font=self.master.FT10BW,bg='#23275C',fg='#FFFFFF',x=130,y=80)
        Labels(self.RP_FR2_1,text="HW Version :",x=255,y=60,fg='#FFFFFF',bg='#343638',width=15,font=self.master.FT10BW)
        self.HWCB = Combo(self.RP_FR2_1,width=14,state="readonly",font=self.master.FT10BW,bg='#23275C',fg='#FFFFFF',x=255,y=80)

        # Labels(self.RP_FR2_1,text="Test Results :",x=380,y=60,fg='#FFFFFF',bg='#343638',width=15,font=self.master.FT10BW)
        # ListBx(self.RP_FR2_1,width=15,height=3,font=self.master.FT10BW,x=380,y=80,bg='#23275C',fg='#FFFFFF')

        Labels(self.RP_FR2_1,text="Board Number :",x=5,y=100,fg='#FFFFFF',bg='#343638',width=15,font=self.master.FT10BW)
        self.BNCB=Combo(self.RP_FR2_1,width=14,state="readonly",font=self.master.FT10BW,bg='#23275C',fg='#FFFFFF',x=5,y=120)
        Labels(self.RP_FR2_1,text="DUT Name :",x=130,y=100,fg='#FFFFFF',bg='#343638',width=15,font=self.master.FT10BW)
        self.DNCB = Combo(self.RP_FR2_1,width=14,state="readonly",font=self.master.FT10BW,bg='#23275C',fg='#FFFFFF',x=130,y=120)
        Labels(self.RP_FR2_1,text="DUT ID :",x=255,y=100,fg='#FFFFFF',bg='#343638',width=15,font=self.master.FT10BW)
        self.DICB = Combo(self.RP_FR2_1,width=14,state="readonly",font=self.master.FT10BW,bg='#23275C',fg='#FFFFFF',x=255,y=120)

        self.EnTimings = CheckBtn(self.RP_FR2_1,font=self.master.FT10BW,x=5,y=140,bg='#343638',fg='#FFFFFF',name='entime',text="Timing Checks")
        self.EnMeasures = CheckBtn(self.RP_FR2_1,font=self.master.FT10BW,x=125,y=140,bg='#343638',fg='#FFFFFF',name='enmesure',text="Measure Checks")
        self.EnOthers = CheckBtn(self.RP_FR2_1,font=self.master.FT10BW,x=255,y=140,bg='#343638',fg='#FFFFFF',name='enothers',text="Other Cheks")

        Buttons(self.RP_FR2_1,text='Prepare Report',x=5,y=170,font=self.master.FT10BW,width=15)
        Buttons(self.RP_FR2_1,text='Refresh',x=120,y=170,font=self.master.FT10BW,width=15)

        Labels(self.RP_FR2_1,text="Chapters : ALL",x=385,y=28,fg='#FFFFFF',bg='#343638',width=11,font=self.master.FT10BW)
        self.ChapCKSA = CheckBtn(self.RP_FR2_1,font=self.master.FT10BW,x=470,y=27,bg='#343638',fg='#FFFFFF',name='chapCKSA',command=self.ChapLBSA)
        self.ChapLB = ListBx(self.RP_FR2_1,width=20,height=9,font=self.master.FT10BW,x=385,y=50,bg='#23275C',fg='#FFFFFF')

        Labels(self.RP_FR2_1,text="Positions:ALL",x=535,y=28,fg='#FFFFFF',bg='#343638',width=11,font=self.master.FT10BW)
        self.PosCKSA = CheckBtn(self.RP_FR2_1,font=self.master.FT10BW,x=620,y=27,bg='#343638',fg='#FFFFFF',name='posCKSA',command=self.PosLBSA)
        self.PosLB = ListBx(self.RP_FR2_1,width=20,height=9,font=self.master.FT10BW,x=535,y=50,bg='#23275C',fg='#FFFFFF')

        Labels(self.RP_FR2_1,text="Tests : ALL",x=685,y=28,fg='#FFFFFF',bg='#343638',width=11,font=self.master.FT10BW)
        self.TestCKSA = CheckBtn(self.RP_FR2_1,font=self.master.FT10BW,x=770,y=27,bg='#343638',fg='#FFFFFF',name='testCKSA',command=self.TestLBSA)
        self.TestLB = ListBx(self.RP_FR2_1,width=20,height=9,font=self.master.FT10BW,x=685,y=50,bg='#23275C',fg='#FFFFFF')

        self.SWCB.bind("<<ComboboxSelected>>",self.SWCBload)
        self.FWCB.bind("<<ComboboxSelected>>",self.FWCBload)
        self.HWCB.bind("<<ComboboxSelected>>",self.HWCBload)
        self.BNCB.bind("<<ComboboxSelected>>",self.BNCBload)
        self.DNCB.bind("<<ComboboxSelected>>",self.DNCBload)
        self.DICB.bind("<<ComboboxSelected>>",self.DICBload)
        self.ChapLB.bind("<<ListboxSelect>>",self.ChapLBload)
        self.PosLB.bind("<<ListboxSelect>>",self.PosLBload)    
    def PutReportSummary(self):
        self.master.ClearFrame(self.RP_FR2_2)
        Labels(self.RP_FR2_2,text="Report Summary",x=0,y=0,bg='#999999',fg='#ffffff',width=120,font=self.master.FT10BW)

        Labels(self.RP_FR2_2,text="Total Tests",x=20,y=22,fg='#FFFFFF',bg='#343638',width=15,font=self.master.FT15BW)
        Labels(self.RP_FR2_2,text="Pass Count",x=220,y=22,fg='#FFFFFF',bg='#343638',width=15,font=self.master.FT15BW)
        Labels(self.RP_FR2_2,text="Fail Count",x=420,y=22,fg='#FFFFFF',bg='#343638',width=15,font=self.master.FT15BW)
        Labels(self.RP_FR2_2,text="Incl. Count",x=620,y=22,fg='#FFFFFF',bg='#343638',width=15,font=self.master.FT15BW)

        Labels(self.RP_FR2_2,text="0",x=20,y=55,fg='#FFFFFF',bg='#343638',width=15,font=self.master.FT15BW)
        Labels(self.RP_FR2_2,text="0",x=220,y=55,fg='#FFFFFF',bg='#343638',width=15,font=self.master.FT15BW)
        Labels(self.RP_FR2_2,text="0",x=420,y=55,fg='#FFFFFF',bg='#343638',width=15,font=self.master.FT15BW)
        Labels(self.RP_FR2_2,text="0",x=620,y=55,fg='#FFFFFF',bg='#343638',width=15,font=self.master.FT15BW)    
    def PutReportMenu(self):
        self.master.ClearFrame(self.RP_FR2_3)
        Labels(self.RP_FR2_3,text="Generate Report",x=0,y=0,bg='#999999',fg='#ffffff',width=120,font=self.master.FT10BW)
        Buttons(self.RP_FR2_3,text='CTS Validation Report',x=5,y=30,font=self.master.FT12BW,width=19, command=self.GetReportData)
        Labels(self.RP_FR2_3,text=": Generate XLS report with all CTS checks and other checks like timings etc. based on the selection from Input section",x=170,y=30,fg='#FFFFFF',bg='#343638',font=self.master.FT10BW)
        Buttons(self.RP_FR2_3, text="Export CTS Checks", x=5, y=70, font=self.master.FT12BW, width=19,command=self.export_cts)
        Labels(self.RP_FR2_3,text=": Export CTS Checks to Excel based on the selection from Input section",x=170,y=70,fg='#FFFFFF',bg='#343638',font=self.master.FT10BW)

    def export_cts(self):
        xl_report = XLreport(mode=self.master.Mode, name="CTS Checks")  
        xl_report.ExportCTSChecks()

    def GetReportData(self):
        ch_index = self.ChapLB.curselection()
        pos_index = self.PosLB.curselection()
        ts_index = self.TestLB.curselection()
        timechk = True if self.EnTimings.getvar(self.EnTimings.winfo_name())=='1' else False
        meschk = True if self.EnMeasures.getvar(self.EnMeasures.winfo_name())=='1' else False
        othchk = True if self.EnOthers.getvar(self.EnOthers.winfo_name())=='1' else False
        fltr ={
            "SW":[self.SWCB.get()],"FW":[self.FWCB.get()],"HW":[self.HWCB.get()],"Board":[self.BNCB.get()],"DUTname":[self.DNCB.get()],"DUTID":[self.DICB.get()],
            "Chap":[self.ChapLB.get(i) for i in ch_index],"Coil":[self.PosLB.get(i) for i in pos_index],"Tests":[self.TestLB.get(i) for i in ts_index],
            "Timings":timechk,"Measures":meschk,"Others":othchk}
        print(fltr)
        self.CTSrep = CSVreport(filters=fltr,mode=self.master.Mode)
        # for Tcdata in 
        #Add summary frame --TBD
    #Backend Functions
    def SWCBload(self,ts):
        self.FWCB['values']=list(self.JConData[self.SWCB.get()].keys())
    def FWCBload(self,ts):
        self.HWCB['values']=list(self.JConData[self.SWCB.get()][self.FWCB.get()].keys())  
    def HWCBload(self,ts):
        self.BNCB['values']=list(self.JConData[self.SWCB.get()][self.FWCB.get()][self.HWCB.get()].keys())
    def BNCBload(self,ts):
        self.DNCB['values']=list(self.JConData[self.SWCB.get()][self.FWCB.get()][self.HWCB.get()][self.BNCB.get()].keys())
    def DNCBload(self,ts):
        self.DICB['values']=list(self.JConData[self.SWCB.get()][self.FWCB.get()][self.HWCB.get()][self.BNCB.get()][self.DNCB.get()].keys()) 
    def DICBload(self,ts):
        self.ChapLB.UpdateValues(list(self.JConData[self.SWCB.get()][self.FWCB.get()][self.HWCB.get()][self.BNCB.get()][self.DNCB.get()][self.DICB.get()].keys()))
    def ChapLBload(self,ts):
        index = self.ChapLB.curselection()
        chap = [self.ChapLB.get(i) for i in index]
        if len(chap)>0:
            poslist = []
            for ch in list(self.JConData[self.SWCB.get()][self.FWCB.get()][self.HWCB.get()][self.BNCB.get()][self.DNCB.get()][self.DICB.get()].keys()):
                if ch in chap:
                    for pos in list(self.JConData[self.SWCB.get()][self.FWCB.get()][self.HWCB.get()][self.BNCB.get()][self.DNCB.get()][self.DICB.get()][ch].keys()):
                        if pos not in poslist:poslist.append(pos)
            self.PosLB.UpdateValues(poslist)
        else:
            self.PosLB.delete(0,tk.END)
            self.TestLB.delete(0,tk.END)
    def PosLBload(self,ts):
        ch_index = self.ChapLB.curselection()
        chap = [self.ChapLB.get(i) for i in ch_index]
        pos_index = self.PosLB.curselection()
        pos = [self.PosLB.get(i) for i in pos_index]
        if len(chap)>0 and len(pos)>0:
            testlist = []
            for ch in list(self.JConData[self.SWCB.get()][self.FWCB.get()][self.HWCB.get()][self.BNCB.get()][self.DNCB.get()][self.DICB.get()].keys()):
                if ch in chap:
                    for ps in list(self.JConData[self.SWCB.get()][self.FWCB.get()][self.HWCB.get()][self.BNCB.get()][self.DNCB.get()][self.DICB.get()][ch].keys()):
                        if ps in pos:
                            for tc in list(self.JConData[self.SWCB.get()][self.FWCB.get()][self.HWCB.get()][self.BNCB.get()][self.DNCB.get()][self.DICB.get()][ch][ps].keys()):
                                if tc not in testlist: testlist.append(tc)
            self.TestLB.UpdateValues(testlist)
        else:self.TestLB.delete(0,tk.END)
    def ChapLBSA(self):
        status = self.ChapCKSA.getvar(self.ChapCKSA.winfo_name())
        if status =='1':
            self.ChapLB.select_set(0,tk.END)
        else: self.ChapLB.select_clear(0,tk.END)
        self.ChapLBload('ts')
    def PosLBSA(self):
        status = self.PosCKSA.getvar(self.PosCKSA.winfo_name())
        if status =='1':
            self.PosLB.select_set(0,tk.END)
        else: self.PosLB.select_clear(0,tk.END)
        self.PosLBload('ts')
    def TestLBSA(self):
        status = self.TestCKSA.getvar(self.TestCKSA.winfo_name())
        if status =='1':
            self.TestLB.select_set(0,tk.END)
        else: self.TestLB.select_clear(0,tk.END)
    def open_Directory_path(self,value):
        foldernames = list(tkfilebrowser.askopendirnames(title="Select Project Folders"))
        if len(foldernames)>0:
            if value == 'JsonMerge':
                jsonlist = []
                #fetch final reports avaialable in path
                for path in foldernames:
                    for root, dirs, files in os.walk(path):
                        for file in files:
                            if file.endswith(".json") and file.__contains__("FinalReport"):
                                jsonlist.append(os.path.join(root, file))
                if len(jsonlist)>0:
                    for jpath in jsonlist:
                        if jpath not in self.master.JsettingsData['JsonMerge']['JsonMergePath']:self.master.JsettingsData['JsonMerge']['JsonMergePath'].append(jpath)
                    self.master.Jsettings.update_file(self.master.JsettingsData)
                    self.JsonMerge()
            if value =='JsonComp':
                pass
            if value =='BIAnly':
                csvpaths = {}
                ipjson = []
                for path in foldernames:
                    for root, dirs, files in os.walk(path):
                        for file in files:
                            if 'input' in file and '.json' in file:
                                ipjson.append(os.path.join(root, file))
                if len(ipjson)>0:
                    for proj in ipjson:
                        print(proj)
                        csvpaths[proj] = []
                        projli = proj.split('\\')
                        projpath = '\\'.join(projli[0:len(projli)-1])
                        for root, dirs, files in os.walk(projpath):
                            for file in files:
                                if file.startswith('TPT_') and file.endswith('.csv'):
                                    csvpaths[proj].append(os.path.join(root, file))
                if len(csvpaths)>0:
                    for jsonpath in csvpaths:
                        if jsonpath not in self.master.JsettingsData['BIAnalyis']:
                            self.master.JsettingsData['BIAnalyis'][jsonpath] = csvpaths[jsonpath]
                    self.master.Jsettings.update_file(self.master.JsettingsData)
                    self.BIAnalysis()
    def RemoveItemLB(self,LB,value):
        index = LB.curselection()
        if len(index)>0:
            items = [LB.get(i) for i in index]
            if value =='JsonMerge':
                for item in items:
                    self.master.JsettingsData['JsonMerge']['JsonMergePath'].remove(item)
                self.master.Jsettings.update_file(self.master.JsettingsData)
                self.JsonMerge()
            if value =='BIAnly':
                for item in items:
                    self.master.JsettingsData['BIAnalyis'].pop(item)
                self.master.Jsettings.update_file(self.master.JsettingsData)
                self.BIAnalysis()
    def ClearLB(self,value):
        if value == 'JsonMerge':
            self.master.JsettingsData['JsonMerge']['JsonMergePath'].clear()
            self.master.Jsettings.update_file(self.master.JsettingsData)
            self.JsonMerge()
        if value == 'BIAnly':
            self.master.JsettingsData['BIAnalyis'].clear()  
            self.master.Jsettings.update_file(self.master.JsettingsData)
            self.BIAnalysis()
    def GenerateBIreport2(self):
        #consider old and new file structure of the SW
        results={}
        BIData = self.master.JsettingsData['BIAnalyis']
        if len(BIData)>0:
            for proj in BIData:
                jsonpath=JsonOperations(proj)
                jsondata = jsonpath.read_file()
                Board = jsondata['TestToolInfo']['SerialNumber']
                #read from CSV
                if Board not in results:results[Board]={}
                #add csv data
                for cpath in BIData[proj]:
                    # print(cpath)
                    pathli = cpath.split('\\')
                    if 'input_new.json' in proj:
                        #new frmt
                        dut = jsondata['TestToolInfo']['DUTname']
                        position = jsondata['TestToolInfo']['Position']
                        offsetData = jsondata['Calculations']['00'] if position == '0,0,0' else jsondata['Calculations']['22']
                        run = str(pathli[len(pathli)-3]).split('Run')[1] 
                        Power=0
                        if jsondata['TestToolInfo']['DUTname'] not in results[Board]: results[Board][dut]={}
                        if jsondata['TestToolInfo']['Position'] not in results[Board][dut]:results[Board][dut][position]={}
                        data = open(cpath)
                        csvFile = csv.reader(data)
                        cnt=0
                        Tempdata = {"Time":[],"Prect":[],"PFO":[],'NewPFO':[],'Inlimit':[]}
                        for lines in csvFile:
                            print(cnt)
                            if cnt !=0:
                                if cnt > 4 and float(lines[2]) < 1:
                                    #considered next power started and get max prect value and find the power
                                    if max(Tempdata['Prect']) >= 15: 
                                        Power = 15
                                    elif max(Tempdata['Prect']) > 12.5 and max(Tempdata['Prect']) < 15:
                                        Power = 12.5
                                    elif max(Tempdata['Prect']) > 10 and max(Tempdata['Prect']) < 12:
                                        Power = 10
                                    elif max(Tempdata['Prect']) > 7.5 and max(Tempdata['Prect']) < 10:
                                        Power = 7.5
                                    elif max(Tempdata['Prect']) > 5 and max(Tempdata['Prect']) < 7.5:
                                        Power = 5
                                    elif max(Tempdata['Prect']) > 3.5 and max(Tempdata['Prect']) < 5:
                                        Power = 3.5
                                    # print('Power',Power,cnt)
                                    cnt=1
                                    if Power not in results[Board][dut][position]:results[Board][dut][position][Power]={}
                                    results[Board][dut][position][Power][run]=Tempdata
                                    Tempdata = {"Time":[],"Prect":[],"PFO":[],'NewPFO':[],'Inlimit':[]}
                                Inlimit = 'No'
                                Tempdata['Time'].append(lines[0])
                                Tempdata['Prect'].append(float(lines[2]))
                                #find limits for each power
                                if Power in jsondata['PowerLimits']:
                                    tolper = [float(Power) - ((float(Power)*jsondata['PowerLimits'][Power])/100),float(Power) + ((float(Power)*jsondata['PowerLimits'][Power])/100)]
                                    # print(Power, tolper)
                                    if (float(lines[14]) <= 350 and (float(lines[14]) >= -350)) and (float(lines[2]) >= tolper[0] and float(lines[2]) <= tolper[1]):
                                        Inlimit = 'Yes'
                                Tempdata['PFO'].append(float(lines[14]))
                                NewCircutLoss = ((pow(float(lines[8]),2))*offsetData['GRAD'])+offsetData['offset']
                                NewPFM = ((pow(float(lines[8]),2))*jsondata['Calculations']['AlphaFM']*jsondata['Calculations']['GFM'])+(jsondata['Calculations']['AlphaFMDC']*jsondata['Calculations']['GFMDC'])
                                Tempdata['NewPFO'].append((((float(lines[12])*float(lines[6]))-(NewPFM+float(lines[10])+NewCircutLoss))-(float(lines[1])))*1000)
                                Tempdata['Inlimit'].append(Inlimit)
                            cnt+=1
                        #considered next power started and get max prect value and find the power
                        if max(Tempdata['Prect']) >= 15: 
                            Power = 15
                        elif max(Tempdata['Prect']) > 12.5 and max(Tempdata['Prect']) < 15:
                            Power = 12.5
                        elif max(Tempdata['Prect']) > 10 and max(Tempdata['Prect']) < 12:
                            Power = 10
                        elif max(Tempdata['Prect']) > 7.5 and max(Tempdata['Prect']) < 10:
                            Power = 7.5
                        elif max(Tempdata['Prect']) > 5 and max(Tempdata['Prect']) < 7.5:
                            Power = 5
                        elif max(Tempdata['Prect']) > 3.5 and max(Tempdata['Prect']) < 5:
                            Power = 3.5
                        if Power not in results[Board][dut][position]:results[Board][dut][position][Power]={}
                        results[Board][dut][position][Power][run]=Tempdata
                    else:
                        print(pathli)
                        finaldata = {"Time":[],"Prect":[],"PFO":[],'ACCurrent':[],'InverterVoltage':[],'DCCurrent':[],'CoilLoss':[],'ReceivedPower':[],'TxPower':[]}
                        #old format
                        dut = pathli[len(pathli)-5]
                        position = str(pathli[len(pathli)-4]).replace('(','').replace(')','').replace(',','_')
                        run = str(pathli[len(pathli)-3]).split('Run')[1]
                        Power = str(pathli[len(pathli)-2]).replace('W','')
                        # offsetData = jsondata['Calculations']['00'] if position == '0,0,0' else jsondata['Calculations']['22']
                        if dut not in results[Board]: results[Board][dut]={}
                        if position not in results[Board][dut]:results[Board][dut][position]={}
                        if Power not in results[Board][dut][position]:results[Board][dut][position][Power]={}
                        data = open(cpath)
                        csvFile = csv.reader(data)
                        cnt=0
                        # print(Board,dut,position,Power,run)
                        for lines in csvFile:
                            if cnt !=0:
                                # Inlimit = 'No'
                                finaldata['Time'].append(lines[0])
                                finaldata['Prect'].append(lines[2])
                                finaldata['PFO'].append(float(lines[14]))
                                finaldata['ACCurrent'].append(float(lines[8]))
                                finaldata['InverterVoltage'].append(float(lines[12]))
                                finaldata['DCCurrent'].append(float(lines[6]))
                                finaldata['CoilLoss'].append(float(lines[10]))
                                finaldata['ReceivedPower'].append(float(lines[1]))
                                finaldata['TxPower'].append(lines[13])
                            cnt+=1
                        # break
                        results[Board][dut][position][Power][run]=finaldata
        #export merged results to csv
        if len(results)>0:
            rows = []
            fields = ['Board', 'DUT', 'Position', 'Power','Run','PFO','Prect','Time','ACCurrent','InverterVoltage','DCCurrent','CoilLoss','ReceivedPower','TxPower']
            for Board in results:
                for DUT in results[Board]:
                    for pos in results[Board][DUT]:
                        for powr in results[Board][DUT][pos]:
                            for run in results[Board][DUT][pos][powr]:
                                for PFOval,Prectval,Timeval,ACCurrentval,InverterVoltageVal,DCCurrentval,CoilLossval,ReceivedPowerval,TxPowerval in zip(results[Board][DUT][pos][powr][run]['PFO'],
                                                                                        results[Board][DUT][pos][powr][run]['Prect'],
                                                                                        results[Board][DUT][pos][powr][run]['Time'],
                                                                                        results[Board][DUT][pos][powr][run]['ACCurrent'],
                                                                                        results[Board][DUT][pos][powr][run]['InverterVoltage'],
                                                                                        results[Board][DUT][pos][powr][run]['DCCurrent'],
                                                                                        results[Board][DUT][pos][powr][run]['CoilLoss'],
                                                                                        results[Board][DUT][pos][powr][run]['ReceivedPower'],
                                                                                        results[Board][DUT][pos][powr][run]['TxPower']):
                                    # rows.append({"Board":board,"DUT":DUT,"Position":pos,"Power":pow,"Run":run,"PFP":PFOval,"Prect":Prectval,"Time":Timeval})
                                    rows.append([Board,DUT,pos,powr,run,PFOval,Prectval,Timeval,ACCurrentval,InverterVoltageVal,DCCurrentval,CoilLossval,ReceivedPowerval,TxPowerval])
            if len(rows)>0:
                now = datetime.now()
                timestamp = now.strftime("%d%m%Y_%H%M%S")
                filename = "Results/MPP Excel Results/BIData_"+timestamp+'.csv'
                # writing to csv file
                with open(filename, 'w',newline='') as csvfile:
                    write = csv.writer(csvfile)
                    write.writerow(fields)
                    write.writerows(rows)
    def GenerateBIreport(self):
        #consider old and new file structure of the SW
        results={}
        BIData = self.master.JsettingsData['BIAnalyis']
        if len(BIData)>0:
            for proj in BIData:
                jsonpath=JsonOperations(proj)
                jsondata = jsonpath.read_file()
                Board = jsondata['TestToolInfo']['SerialNumber']
                #read from CSV
                if Board not in results:results[Board]={}
                #add csv data
                for cpath in BIData[proj]:
                    pathli = cpath.split('\\')
                    if 'input_new.json' in proj:
                        #new frmt
                        dut = jsondata['TestToolInfo']['DUTname']
                        position = jsondata['TestToolInfo']['Position']
                        offsetData = jsondata['Calculations']['00'] if position == '0,0,0' else jsondata['Calculations']['22']
                        run = str(pathli[len(pathli)-3]).split('Run')[1] 
                        Power=0
                        if jsondata['TestToolInfo']['DUTname'] not in results[Board]: results[Board][dut]={}
                        if jsondata['TestToolInfo']['Position'] not in results[Board][dut]:results[Board][dut][position]={}
                        data = open(cpath)
                        csvFile = csv.reader(data)
                        cnt=0
                        Tempdata = {"Time":[],"Prect":[],"PFO":[],'NewPFO':[],'Inlimit':[]}
                        for lines in csvFile:
                            print(cnt)
                            if cnt !=0:
                                if cnt > 4 and float(lines[2]) < 1:
                                    #considered next power started and get max prect value and find the power
                                    if max(Tempdata['Prect']) >= 15: 
                                        Power = 15
                                    elif max(Tempdata['Prect']) > 12.5 and max(Tempdata['Prect']) < 15:
                                        Power = 12.5
                                    elif max(Tempdata['Prect']) > 10 and max(Tempdata['Prect']) < 12:
                                        Power = 10
                                    elif max(Tempdata['Prect']) > 7.5 and max(Tempdata['Prect']) < 10:
                                        Power = 7.5
                                    elif max(Tempdata['Prect']) > 5 and max(Tempdata['Prect']) < 7.5:
                                        Power = 5
                                    elif max(Tempdata['Prect']) > 3.5 and max(Tempdata['Prect']) < 5:
                                        Power = 3.5
                                    # print('Power',Power,cnt)
                                    cnt=1
                                    if Power not in results[Board][dut][position]:results[Board][dut][position][Power]={}
                                    results[Board][dut][position][Power][run]=Tempdata
                                    Tempdata = {"Time":[],"Prect":[],"PFO":[],'NewPFO':[],'Inlimit':[]}
                                Inlimit = 'No'
                                Tempdata['Time'].append(lines[0])
                                Tempdata['Prect'].append(float(lines[2]))
                                #find limits for each power
                                if Power in jsondata['PowerLimits']:
                                    tolper = [float(Power) - ((float(Power)*jsondata['PowerLimits'][Power])/100),float(Power) + ((float(Power)*jsondata['PowerLimits'][Power])/100)]
                                    # print(Power, tolper)
                                    if (float(lines[14]) <= 350 and (float(lines[14]) >= -350)) and (float(lines[2]) >= tolper[0] and float(lines[2]) <= tolper[1]):
                                        Inlimit = 'Yes'
                                Tempdata['PFO'].append(float(lines[14]))
                                NewCircutLoss = ((pow(float(lines[8]),2))*offsetData['GRAD'])+offsetData['offset']
                                NewPFM = ((pow(float(lines[8]),2))*jsondata['Calculations']['AlphaFM']*jsondata['Calculations']['GFM'])+(jsondata['Calculations']['AlphaFMDC']*jsondata['Calculations']['GFMDC'])
                                Tempdata['NewPFO'].append((((float(lines[12])*float(lines[6]))-(NewPFM+float(lines[10])+NewCircutLoss))-(float(lines[1])))*1000)
                                Tempdata['Inlimit'].append(Inlimit)
                            cnt+=1
                        #considered next power started and get max prect value and find the power
                        if max(Tempdata['Prect']) >= 15: 
                            Power = 15
                        elif max(Tempdata['Prect']) > 12.5 and max(Tempdata['Prect']) < 15:
                            Power = 12.5
                        elif max(Tempdata['Prect']) > 10 and max(Tempdata['Prect']) < 12:
                            Power = 10
                        elif max(Tempdata['Prect']) > 7.5 and max(Tempdata['Prect']) < 10:
                            Power = 7.5
                        elif max(Tempdata['Prect']) > 5 and max(Tempdata['Prect']) < 7.5:
                            Power = 5
                        elif max(Tempdata['Prect']) > 3.5 and max(Tempdata['Prect']) < 5:
                            Power = 3.5
                        if Power not in results[Board][dut][position]:results[Board][dut][position][Power]={}
                        results[Board][dut][position][Power][run]=Tempdata
                    else:
                        finaldata = {"Time":[],"Prect":[],"PFO":[],'NewPFO':[],'Inlimit':[]}
                        #old format
                        dut = pathli[len(pathli)-5]
                        position = str(pathli[len(pathli)-4]).replace('(','').replace(')','').replace(',','_')
                        run = str(pathli[len(pathli)-3]).split('Run')[1]
                        Power = str(pathli[len(pathli)-2]).replace('W','')
                        offsetData = jsondata['Calculations']['00'] if position == '0,0,0' else jsondata['Calculations']['22']
                        if dut not in results[Board]: results[Board][dut]={}
                        if position not in results[Board][dut]:results[Board][dut][position]={}
                        if Power not in results[Board][dut][position]:results[Board][dut][position][Power]={}
                        data = open(cpath)
                        csvFile = csv.reader(data)
                        cnt=0
                        print(Board,dut,position,Power,run)
                        for lines in csvFile:
                            if cnt !=0:
                                Inlimit = 'No'
                                finaldata['Time'].append(lines[0])
                                finaldata['Prect'].append(lines[2])
                                #find limits for each power
                                if Power in jsondata['PowerLimits']:
                                    tolper = [float(Power) - ((float(Power)*jsondata['PowerLimits'][Power])/100),float(Power) + ((float(Power)*jsondata['PowerLimits'][Power])/100)]
                                    # print(Power, tolper)
                                    if (float(lines[14]) <= 350 and (float(lines[14]) >= -350)) and (float(lines[2]) >= tolper[0] and float(lines[2]) <= tolper[1]):
                                        Inlimit = 'Yes'
                                finaldata['PFO'].append(float(lines[14]))
                                NewCircutLoss = ((pow(float(lines[8]),2))*offsetData['GRAD'])+offsetData['offset']
                                NewPFM = ((pow(float(lines[8]),2))*jsondata['Calculations']['AlphaFM']*jsondata['Calculations']['GFM'])+(jsondata['Calculations']['AlphaFMDC']*jsondata['Calculations']['GFMDC'])
                                finaldata['NewPFO'].append((((float(lines[12])*float(lines[6]))-(NewPFM+float(lines[10])+NewCircutLoss))-(float(lines[1])))*1000)
                                finaldata['Inlimit'].append(Inlimit)
                            cnt+=1
                        # break
                        results[Board][dut][position][Power][run]=finaldata
        #export merged results to csv
        if len(results)>0:
            rows = []
            fields = ['Board', 'DUT', 'Position', 'Power','Run','PFO','Prect','Time','NewPFO','Inlimit']
            for board in results:
                for DUT in results[Board]:
                    for pos in results[Board][DUT]:
                        for powr in results[Board][DUT][pos]:
                            for run in results[Board][DUT][pos][powr]:
                                for PFOval,Prectval,Timeval,NewPFOval,Inlimitval in zip(results[Board][DUT][pos][powr][run]['PFO'],results[Board][DUT][pos][powr][run]['Prect'],results[Board][DUT][pos][powr][run]['Time'],results[Board][DUT][pos][powr][run]['NewPFO'],results[Board][DUT][pos][powr][run]['Inlimit']):
                                    # rows.append({"Board":board,"DUT":DUT,"Position":pos,"Power":pow,"Run":run,"PFP":PFOval,"Prect":Prectval,"Time":Timeval})
                                    rows.append([board,DUT,pos,powr,run,PFOval,Prectval,Timeval,NewPFOval,Inlimitval])
            if len(rows)>0:
                now = datetime.now()
                timestamp = now.strftime("%d%m%Y_%H%M%S")
                filename = "Results/MPP Excel Results/BIData_"+timestamp+'.csv'
                # writing to csv file
                with open(filename, 'w',newline='') as csvfile:
                    write = csv.writer(csvfile)
                    write.writerow(fields)
                    write.writerows(rows)


class CustomDialog(Toplevel):
    def __init__(self, parent, title, message):
        super().__init__(parent)
        self.title(title)
        
        label = Label(self, text=message)
        label.pack(padx=10, pady=10)

        button_offline = Button(self, text="Offline", command=lambda: self.choice("Offline"))
        button_offline.pack(side="left", padx=5)

        button_online = Button(self, text="Online", command=lambda: self.choice("Online"))
        button_online.pack(side="right", padx=5)

    def choice(self, value):
        self.result = value
        self.destroy()

class UiUx(MPPGUI):
    def __init__(self, master):
        self.master = master
        self.master.ClearFrame(self.master.SM2_frame)
        self.UISection()

    def UISection(self):          
        #result = messagebox.askyesno("UI Test Cases", "Do you want to run the UI Test Cases?")
        #if result:
            # Create a button in SM2_frame for connection setup
        #tester_connected = messagebox.askyesno("Tester Connection", "Is the tester connected?")
        connection_setup_button = Button(self.master.SM2_frame, text="Connection Setup",command=self.run_connectiotest)
        connection_setup_button.place(x=10, y=11, width=130, height=28)
        test_configuration_button = Button(self.master.SM2_frame, text="Test Configuration",command=self.test_configuration)
        test_configuration_button.place(x=10, y=51, width=130, height=28)
        result_button = Button(self.master.SM2_frame, text="Result")
        result_button.place(x=10, y=91, width=130, height=28)
        report_button = Button(self.master.SM2_frame, text="Report")
        report_button.place(x=10, y=131, width=130, height=28)
        report_analyser_button = Button(self.master.SM2_frame, text="Report Analyser")
        report_analyser_button.place(x=10, y=171, width=130, height=28)
        layouts_button = Button(self.master.SM2_frame, text="Layouts")
        layouts_button.place(x=10, y=211, width=130, height=28)
        if self.master.Mode =='TPR':
            Qi = Button(self.master.SM2_frame, text="QI_Authenticator")
            Qi.place(x=10, y=251, width=130, height=28)
        else:
            Qi = Button(self.master.SM2_frame, text="QI_Authenticator")
            Qi.place(x=10, y=251, width=130, height=28)
        Help = Button(self.master.SM2_frame, text="Help")
        Help.place(x=10, y=291, width=130, height=28)
        Firmwareupdate = Button(self.master.SM2_frame, text="Firmware Update")
        Firmwareupdate.place(x=10, y=331, width=130, height=28)
        if self.master.Mode =='TPT':
            Firmwareupdate = Button(self.master.SM2_frame, text="Qi-Exerciser")
            Firmwareupdate.place(x=10, y=371, width=130, height=28)
        else:
            Firmwareupdate = Button(self.master.SM2_frame, text="Qi-Exerciser")
            Firmwareupdate.place(x=10, y=371, width=130, height=28)
        self.DynamicIp()
        self.TestConfig()
        # self.QI1()

    def DynamicIp(self):
        # Clear the frame before adding new elements
        #self.master.ClearFrame(self.master.SM2_frame)

        # Add a label for Tester IP
        Tester = Labels(self.master.SM2_frame,text="Tester IP:",x=5,y=28,fg='#FFFFFF',bg='#343638',width=10,font=self.master.FT10BW)
        #Tester = Label(self.master.SM2_frame, text="Tester IP:", font=self.master.FT12BW)
        Tester.place(x=179, y=12, width=87, height=25)

        # Add an entry widget for Tester IP
        tester_ip_entry = Entries(self.master.SM2_frame,width=33,x=80,y=30,font=self.master.FT10BW,bg='#23275C',fg='#FFFFFF')
        #tester_ip_entry = Entry(self.master.SM2_frame, font=self.master.FT12BW)
        tester_ip_entry.place(x=270, y=12, width=130, height=25)

        # Add a button to save the Tester IP
        save_button = Button(self.master.SM2_frame, text="Save", command=lambda: self.save_tester_ip(tester_ip_entry.get()))
        save_button.place(x=404, y=12.5, width=71, height=25)

    def TestConfig(self):
        gproj = Labels(self.master.SM2_frame,text=".GPROJ:",x=5,y=28,fg='#FFFFFF',bg='#343638',width=10,font=self.master.FT10BW)
        #gproj = Label(self.master.SM2_frame, text=".GPROJ:", font=self.master.FT12BW)
        gproj.place(x=179, y=50, width=87, height=25)

        # Add an entry widget for Tester IP
        gproj_entry = Entries(self.master.SM2_frame,width=33,x=80,y=30,font=self.master.FT10BW,bg='#23275C',fg='#FFFFFF')
        gproj_entry.place(x=270, y=50, width=370, height=25)

        browse_button = Button(self.master.SM2_frame, text="Browse", command=lambda: self.browse_file(gproj_entry))
        browse_button.place(x=644, y=50, width=70, height=25.5)

        # Update button
        update_button = Button(self.master.SM2_frame, text="Update", command=lambda: self.update_settings(gproj_entry.get()))
        update_button.place(x=720, y=50, width=70, height=25.5)

    def save_tester_ip(self, tester_ip):
        # Load the existing settings from the JSON file
        self.Jsettings = JsonOperations('json/setting.json')
        settings_data = self.Jsettings.read_file()

        # Update the tester_ip value in the settings
        settings_data['DynamicIP'] = tester_ip

        # Save the updated settings back to the JSON file
        self.Jsettings.update_file(settings_data)

        # Optionally, show a message box indicating successful save
        messagebox.showinfo("Tester IP Saved", f"DynamicIP '{tester_ip}' has been saved.")

    def browse_file(self, entry_widget):
        # Open a file explorer window
        file_path = filedialog.askopenfilename(filetypes=[("GPROJ files", "*.gproj")])

        # Update the entry widget with the selected file path
        if file_path:
            entry_widget.delete(0, tk.END)  # Clear existing text
            entry_widget.insert(0, file_path)

    def update_settings(self, gproj_value):
        # Load the existing settings from the JSON file
        self.Jsettings = JsonOperations('json/setting.json')
        settings_data = self.Jsettings.read_file()

        # Update the gproj value in the settings
        settings_data['CustomLocation'] = gproj_value

        # Save the updated settings back to the JSON file
        self.Jsettings.update_file(settings_data)

        # Optionally, show a message box indicating successful update
        messagebox.showinfo("Settings Updated", f".GPROJ value '{gproj_value}' has been saved in settings.json.")

    def run_connectiotest(self):
        
        # Popup window for connection setup
        popup = Toplevel(self.master)
        popup.title("Connection Setup")

        label = Label(popup, text="Choose the configuration mode:")
        label.pack(padx=10, pady=10)

        # Button for Dynamic mode
        dynamic_button = Button(popup, text="Dynamic", command=lambda: self.handle_connection_setup_mode1("Dynamic", popup))
        dynamic_button.pack(padx=10, pady=5)

        # Button for Static mode
        static_button = Button(popup, text="Static", command=lambda: self.handle_connection_setup_mode1("Static", popup))
        static_button.pack(padx=10, pady=5)

    def handle_connection_setup_mode1(self, mode, popup):
        # Save the selected mode in the settings
        self.save_dynamic_static_status(mode)

        # Close the pop-up
        popup.destroy()

        # Proceed with the connection setup
        subprocess.Popen(["python", "./UI_checks/connectionsetup.py"])

    def save_dynamic_static_status(self, status):
        # Load the existing settings from the JSON file
        self.Jsettings = JsonOperations('json/setting.json')
        settings_data = self.Jsettings.read_file()

        # Update the static_dynamic value in the settings
        settings_data['static_dynamic'] = status

        # Save the updated settings back to the JSON file
        self.Jsettings.update_file(settings_data)

        # Optionally, show a message box indicating successful update
        messagebox.showinfo("Status Updated", f"static_dynamic value has been set to '{status}' in settings.json.")

    def test_configuration(self):
        # Create a custom dialog with "Offline" and "Online" options
        dialog = CustomDialog(self.master, "Test Configuration", "Choose the configuration mode:")
        self.master.wait_window(dialog)

        # Access the result from the custom dialog
        result = dialog.result

        if result == 'Offline':
            # User chose "Offline", so run the offline configuration script
            #subprocess.Popen(["python", "./UI_checks/TestConfiguration.py"])
            pass
        elif result == 'Online':
            # User chose "Online", so call the online configuration method
            self.online()

    def online(self):
        # Create a custom pop-up dialog
        popup = Toplevel(self.master)
        popup.title("Report")

        label = Label(popup, text="Select the mode for generating the report:")
        label.pack(padx=10, pady=10)

        # Button for Dynamic mode
        dynamic_button = Button(popup, text="Dynamic", command=lambda: self.handle_report_mode("Dynamic", popup))
        dynamic_button.pack(padx=10, pady=5)

        # Button for Static mode
        static_button = Button(popup, text="Static", command=lambda: self.handle_report_mode("Static", popup))
        static_button.pack(padx=10, pady=5)

    def handle_report_mode(self, mode, popup):
        # Save the selected mode in the settings
        self.save_dynamic_static_status(mode)

        # Close the pop-up
        popup.destroy()

        # Proceed with generating the report
        #subprocess.Popen(["python", "./UI_checks/online_testconfiguration.py"])

class Menu(tk.Frame):   
    def __init__(self, master, height: 650, bg: None, width: 100, x=0,y=0,grid=None):
        super().__init__(master, height=height, width=width,bg=bg)
        if grid is not None:
            self.grid(row=x,column=y)
        else:self.place(x=x,y=y)
class Buttons(tk.Button):
    def __init__(self, master,bg='#FFFFFF',bd=0,image=None,x=0,y=0,height=None,width=None,command=None,text=None,font=None,grid=None,name=None):
        super().__init__(master,image=None,bg=bg,relief='raised',bd=bd,name=name)
        if height is not None: self['height'] = height
        if width is not None: self['width'] = width
        if command is not None: self['command']=command
        if image is not None: self['image']=image
        if text is not None: self['text']=text
        if font is not None: self['font']=font 
        if grid is not None:
            self.grid(row=x,column=y)
        else:self.place(x=x,y=y)
class Combo(ttk.Combobox):
    def __init__(self, master,width=10,bg=None,fg=None,val=None,x=0,y=0,grid=None,font=None,name=None,selectedVal=None,state=None):
        style = ttk.Style()
        style.theme_use("default")
        super().__init__(master,width=width,values=val,name=name)
        if font is not None: self['font']=font
        if state is not None:self['state']=state
        if fg is not None: 
            style.map('TCombobox', foreground=[('readonly', fg)])
        if bg is not None:
            style.map('TCombobox', fieldbackground=[('readonly',bg)])
            style.map('TCombobox', selectbackground=[('readonly', bg)])
        if selectedVal is not None:
            if selectedVal==True:
                self.set("Yes")
            elif selectedVal ==False:
                self.set('No')
            else: self.set(selectedVal)
        if grid is not None:
            self.grid(row=x,column=y)
        else:self.place(x=x,y=y)
class Labels(tk.Label):
    def __init__(self,master,x:0,y:0,text='',name=None,img=None,bg=None,fg=None,font=None,grid=None,width=None,anchor=None):
        super().__init__(master,text=text,name=name)
        if anchor is not None: self['anchor']=anchor
        if font is not None: self['font']=font
        if img is not None: self['image']=img
        if fg is not None: self['fg']=fg
        if bg is not None: self['bg']=bg
        if width is not None: self['width']=width
        if grid is not None:
            self.grid(row=x,column=y)
        else:self.place(x=x,y=y)
class Entries(tk.Entry):
    def __init__(self, master,width=10,x=0,y=0,font=None,textvar=None,grid=None,bg=None,fg=None,name=None):
        super().__init__(master,width=width,name=name)
        if font is not None: self['font']=font
        if bg is not None: self['bg']=bg
        if fg is not None: self['fg']=fg
        if textvar is not None: self.insert(0,textvar)
        if grid is not None:
            self.grid(row=x,column=y)
        else:
            self.place(x=x,y=y)
class ListBx(tk.Listbox):
    def __init__(self, master,width=10,height=10,font=None,name=None,grid=None,x=0,y=0,bg=None,fg=None,values=None,selectedVal=None):
        super().__init__(master,width=width,height=height,selectmode=tk.MULTIPLE,name=name,exportselection=False)
        if font is not None: self['font']=font
        if bg is not None: self['bg']=bg
        if fg is not None: self['fg']=fg
        if values is not None:
            pos=1
            for v in values:
                self.insert(pos,v)
                pos+=1
        if selectedVal is not None:
            for vs in selectedVal:
                id=0
                while id < self.size():
                    if self.get(id) == vs:
                        self.selection_set(id)
                    id+=1
        if grid is not None:
            self.grid(row=x,column=y)
        else:
            self.place(x=x,y=y)
    def UpdateValues(self,values):
        self.delete(0,tk.END)
        pos=1
        for v in values:
            self.insert(pos,v)
            pos+=1
class CheckBtn(tk.Checkbutton):
    def __init__(self,master,font=None,name='',x=0,y=0,grid=None,bg=None,fg=None,selectedVal=None,text=None,command=None):
        super().__init__(master,name=name,justify=tk.LEFT)
        if font is not None: self['font']=font
        if text is not None: self['text']=text
        if command is not None: self['command']=command
        if fg is not None:
            self['fg']=fg
            self['selectcolor'] = '#23275C'
        if bg is not None:
            self['bg'] = self['activebackground'] =bg
        if selectedVal is not None:
            if selectedVal ==True : 
                    self.select()
            else: self.deselect()
        if grid is not None:
            self.grid(row=x,column=y)
        else:
            self.place(x=x,y=y)
APP=MPPGUI()
APP.CreateAPP()