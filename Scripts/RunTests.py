from Scripts.MainModule import JsonOperations,APIOperations
from Scripts.offlineValidation import OfflineValidation
from datetime import datetime,date
# from MPPGUIform_New import MPPGUI
import time
import json,os,glob
class RunTests():
    def __init__(self,fltr):
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
        self.mode = self.JsettingsData['Mode']
        self.filters = fltr
        if self.mode =='TPT':
            self.DUTport = self.JtesterData['TPR']['port'] 
            self.Testerport = self.JtesterData['TPT']['port'] 
            self.DUT = 'TPR'
        else :
            self.DUTport = self.JtesterData['TPT']['port']
            self.Testerport = self.JtesterData['TPR']['port'] 
            self.DUT = 'TPT'
        #define API's
        self.APIcreateProj_DUT = APIOperations(url=self.JapiData[self.DUT]['PutProjectFolder'],json={"projectName":self.JsettingsData['Online_validation'][self.DUT]['ProjectName'],"moiName":"MPP"})
        self.APIcreateProj_Tester = APIOperations(url=self.JapiData[self.mode]['PutProjectFolder'],json={"projectName":self.JsettingsData['Online_validation'][self.mode]['ProjectName'],"moiName":"MPP"})
        
        self.APISendQI_DUT = APIOperations(url=self.JapiData[self.DUT]['PutQIConfiguration'],json=self.JQIData[self.DUT])
        self.APISendQI_Tester = APIOperations(url=self.JapiData[self.mode]['PutQIConfiguration'],json=self.JQIData[self.mode])
        
        self.APIStartTest_DUT = APIOperations(url=self.JapiData[self.DUT]['PostTestListToExecute'])
        self.APIStartTest_Tester = APIOperations(url=self.JapiData[self.mode]['PostTestListToExecute'])
        
        self.APIstate_DUT = APIOperations(url=self.JapiData[self.DUT]['GetAppState'],retype='json')
        self.APIstate_Tester = APIOperations(url=self.JapiData[self.mode]['GetAppState'],retype='json')
        
        self.APIForceStop_Tester = APIOperations(url=self.JapiData[self.mode]['StopTestExecution'])
        self.APIForceStop_DUT = APIOperations(url=self.JapiData[self.DUT]['StopTestExecution'])
        
        self.APIStartExcer_Tester = APIOperations(url=self.JapiData[self.mode]['EXCR_PutStartExerciser'])
        self.APIStartExcer_DUT = APIOperations(url=self.JapiData[self.DUT]['EXCR_PutStartExerciser'])
        
        self.APIStopExcer_Tester = APIOperations(url=self.JapiData[self.mode]['EXCR_GetStopExerciser'])
        self.APIStopExcer_DUT = APIOperations(url=self.JapiData[self.DUT]['EXCR_GetStopExerciser'])
        
        self.APIpopup =  APIOperations(url=self.JapiData[self.DUT]['GetMessageBox'],retype='json')
        self.APIHandlePopup = APIOperations(url=self.JapiData[self.DUT]['PutMessageBoxResponse'])
        if self.filters['TAD']=='1':
            #Run auto. mode
            if self.filters['TADmode'] =='Automation Tests':
                self.RunTesterAsDUTAuto()
            else: 
                self.RunTesterAsDUTExcer()
        else:
            #Run Normal Mode of with DUT
            self.RunTestOnDUT()   
            # self.OfflineValidationAFRun()
    def RunTestOnDUT(self):
        #1. Ensure Tester COnnected
        if self.JtesterData[self.mode]['status'] =='Connected':
            #2.create project folder
            # self.APIcreateProj_Tester.PutRequest()
            #3.send qi config
            self.APISendQI_Tester.PutRequest()
            #get the list of tests to be run 
            TestList =[]
            for pos in self.filters['Pos']:
                if len(self.JTestConfData[self.mode][self.JMOIData['Offset'][self.mode][self.filters['PowerProfile']][pos]])>0:
                    for Tests in self.JTestConfData[self.mode][self.JMOIData['Offset'][self.mode][self.filters['PowerProfile']][pos]]:
                        TestList.append(self.JMOIData[self.mode][Tests]['Testcase_Name'])
            print(TestList)
            if len(TestList)>0:
                # consider repcont ,since SW api not found use repeat mode using tester
                repcount = self.JQIData[self.mode]['repCount']
                repid = 0
                while repid <= repcount:
                    #4. start the testcase on DUT side
                    self.APIStartTest_Tester.json=TestList
                    self.APIStartTest_Tester.PostRequest()
                    #Run untile tester stops
                    while True:
                        try:
                            self.handlePopup(self.mode)
                            Testrundata = self.APIstate_Tester.GetRequest()
                            if Testrundata['appState']=='READY':
                                print('Test Ended')
                                break
                        except Exception as e:
                                print(e)
                    repid+=1
                #Call the offline Validation
                # if self.mode == 'TPR': self.OfflineValidationAFRun()
        else:
            print(f'Tester {self.mode} not Connected..!')   
    def RunTesterAsDUTAuto(self):
        #1.Ensure both testers are connected
        if self.JtesterData['TPR']['status'] =='Connected':
            if self.JtesterData['TPT']['status'] =='Connected':
                #2.create project folder for both tester and DUT
                self.APIcreateProj_Tester.PutRequest()
                self.APIcreateProj_DUT.PutRequest()
                #3.send qi config for bother tester and DUT
                self.APISendQI_Tester.PutRequest()
                self.APISendQI_DUT.PutRequest()
                repcount = self.JQIData[self.mode]['repCount']
                repid = 0
                while repid <= repcount:
                    #3.Loop through onebyone tests from tester.
                    for pos in self.filters['Pos']:
                        if len(self.JTestConfData[self.mode][pos])>0:
                            for Tests in self.JTestConfData[self.mode][pos]:
                                print(Tests)
                                if 'DUTTestID' in self.JMOIData[Tests]:
                                    try:
                                        if self.JMOIData[Tests]['DUTTestID'] not in ['NA','Excerciser']:
                                            #run DUT side tests in automation
                                            #1. start the testcase on DUT side
                                            self.APIStartTest_DUT.json=[self.JMOIData[self.JMOIData[Tests]['DUTTestID']]['Testcase_Name']]
                                            self.APIStartTest_DUT.PostRequest()
                                            # self.handlePopup(self.DUT)
                                            #wait for 2sec delay
                                            time.sleep(3)
                                            self.handlePopup(self.DUT)
                                            #start from Tester side
                                            self.APIStartTest_Tester.json=[self.JMOIData[Tests]['Testcase_Name']]
                                            self.APIStartTest_Tester.PostRequest()
                                            #wait until tests to complete
                                            while True:
                                                try:
                                                    #handle popup
                                                    self.handlePopup(self.DUT)
                                                    self.handlePopup(self.mode)
                                                    Testrundata = self.APIstate_Tester.GetRequest()
                                                    Dutrundata= self.APIstate_DUT.GetRequest()
                                                    #if DUT stopped and Tester still running force stop the Tester
                                                    if Dutrundata['appState']=='READY':
                                                        print('Test force stopping from Tester side')
                                                        self.APIForceStop_Tester.GetRequest()
                                                    if Testrundata['appState']=='READY':
                                                        print('Test Ended from Tester side')
                                                        while True:
                                                                self.handlePopup(self.DUT)
                                                                Dutrundata= self.APIstate_DUT.GetRequest()
                                                                if Dutrundata['appState']!='READY':
                                                                    #force stop the Tester DUT
                                                                    print('Test force stopping from DUT side')
                                                                    self.APIForceStop_DUT.GetRequest()
                                                                    break
                                                                    #wait for Test to stop
                                                                else: 
                                                                    print('Execution Stopped at DUT side')
                                                                    break
                                                        break
                                                except Exception as e:
                                                    print(e)
                                            time.sleep(2)
                                        else:
                                            #Run excerciser mode, d
                                            pass
                                    except Exception as e: print(e)
                    repid+=1
            else:print('TPT not connnected')
        else:print('TPR not connnected')
    def RunTesterAsDUTExcer(self):
        print(f'Running as {self.DUT} as DUT, from {self.mode}')
        TestList = []
        #1.Ensure both testers are connected
        if self.JtesterData['TPR']['status'] =='Connected':
            if self.JtesterData['TPT']['status'] =='Connected':
                #2.create project folder for both tester and DUT
                self.APIcreateProj_Tester.PutRequest()
                self.APIcreateProj_DUT.PutRequest()
                #3.send qi config for bother tester and DUT
                self.APISendQI_Tester.PutRequest()
                self.APISendQI_DUT.PutRequest()
                #get the list of tests to be run ,
                for pos in self.filters['Pos']:
                    if len(self.JTestConfData[self.mode][pos])>0:
                        for Tests in self.JTestConfData[self.mode][pos]:
                            #select only tests has no confg. DUTTestid
                            if 'DUTTestID' not in self.JMOIData[Tests]:
                                TestList.append(self.JMOIData[Tests]['Testcase_Name'])
                if len(TestList)>0:
                    #Start DUT tester Excerciser mode
                    #1.Reset Excerciser
                    self.ResterExcerciser(self.DUT)
                    self.handlePopup(self.DUT)
                    #2.Start Excerciser
                    self.APIStartExcer_DUT.PutRequest()
                    #consider repcont ,since SW api not found use repeat mode using tester
                    repcount = self.JQIData[self.mode]['repCount']
                    repid = 0
                    while repid <= repcount:
                        #1. start the testcase on Tester
                        self.APIStartTest_Tester.json=TestList
                        self.APIStartTest_Tester.PostRequest()
                        #Run untile tester stops
                        while True:
                            try:
                                self.handlePopup(self.mode)
                                self.handlePopup(self.DUT)
                                Testrundata = self.APIstate_Tester.GetRequest()
                                if Testrundata['appState']=='READY':
                                    print('Test Ended')
                                    break
                            except Exception as e:
                                print(e)
                        repid+=1
                    #Stop Excerciser
                    self.APIStopExcer_DUT.GetRequest()
                    #Call the offline Validation
                    if self.mode == 'TPR': self.OfflineValidationAFRun()
            else:print('TPT not connnected')
        else:print('TPR not connnected')
    def handlePopup(self,mode):
        self.APIpopup.url=self.JapiData[mode]['GetMessageBox']
        data = self.APIpopup.GetRequest()
        if data is not None:
            if data['isValid']==True and data['message'] not in ['']:
                print('got popup',data['index'],data['message'],mode)
                #handle popup
                popupdata = {"userTextBoxInput":"","responseButton":"Ok","shouldTextBoxBeAdded":False,"isValid":True,"popID":data['index'],"displayPopUp":False,"isDisplayPopUpOpen":False,"title":"GRL-C3-MP-TPR Test Solution","message":data['message'],"button":"OK","image":None,"icon":"Asterisk","isFrontEndPopUp":False,"callBackMethod":None,"comboBoxEntries":None,"comboBoxEntriesFE":[],"selectedComboBoxValueFE":"","onlyDropdownAdded":False,"enableTimerOKButton":False,"enableCustomUserInputs":False,"customInputValues":{}}
                self.APIHandlePopup.url=self.JapiData[mode]['PutMessageBoxResponse']
                self.APIHandlePopup.json=popupdata
                self.APIHandlePopup.PutRequest()
    def OfflineValidationAFRun(self):
        path = self.JtesterData[self.mode]['ReportPath']
        repo = list(filter(os.path.isdir, glob.glob(path+ "/*"))) 
        repo.sort(key=os.path.getctime) 
        id = len(repo)-1
        while id >= 0:
            if '_MPP_' in repo[id]:
                CurrentRunPath = repo[id]
                break
            id-=1
        # print(CurrentRunPath)
        #clear existing projects
        self.JsettingsData['Offline_validation']['json_path'][self.mode].clear()
        self.Jsettings.update_file(self.JsettingsData)
        self.JTestConfData[self.mode]['Offline'].clear()
        self.JTestConf.update_file(self.JTestConfData)
        #Add current project
        jsonlist=[]
        if '_MPP_' in CurrentRunPath:
            for root, dirs, files in os.walk(CurrentRunPath):
                for d in dirs:
                    if d.startswith("Run"):
                        if os.path.join(root, d) not in self.JsettingsData['Offline_validation']['json_path'][self.mode]:
                            # print(os.path.join(root, d))
                            jsonlist.append(os.path.join(root, d))
        self.JsettingsData['Offline_validation']['json_path'][self.mode].extend(jsonlist)
        self.Jsettings.update_file(self.JsettingsData)
        #Prepare for Validation list
        TClist={}
        projects = self.JsettingsData['Offline_validation']['json_path'][self.mode]
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
                if filepath is not None and jsonpath is not None:
                    # print(os.path.join(pro,filepath))
                    test = JsonOperations(os.path.join(pro,filepath))
                    testdata =test.read_file()
                    proname = str(filepath.split('\\')[len(filepath.split('\\'))-4])+'-'+str(filepath.split('\\')[len(filepath.split('\\'))-3])
                    if proname not in TClist:TClist[proname] ={}
                    for tcl in testdata['testBkpTestResultsandPath']:
                        # print(tcl['testcaseDetails']['m_DisplayName'])
                        if tcl['testcaseDetails']['m_DisplayName'] is not None:
                            if any(self.JMOIData[i].get('Testcase_Name') == tcl['testcaseDetails']['m_DisplayName'] for i in self.JMOIData if str(self.mode)+"_TD_" in i):
                                testpath = tcl['actualTracePath'].split('\\')
                                TClist[proname][[i for i in self.JMOIData if "TD_" in i and self.JMOIData[i].get('Testcase_Name') == tcl['testcaseDetails']['m_DisplayName']][0]]=[tcl['testcaseDetails']['m_DisplayName'],pro+'\\'+testpath[len(testpath)-2]+'\\'+testpath[len(testpath)-1],jsonpath]
            self.JTestConfData[self.mode]['Offline'].clear()
            self.JTestConfData[self.mode]['Offline']=TClist
            self.JTestConf.update_file(self.JTestConfData)
        #Start tests
        TraceUPL = APIOperations(url=self.JapiData[self.mode]['PutWaveformFile'])
        TCstatus = APIOperations(url=self.JapiData[self.mode]['TCstatus'],retype='json')
        if len(self.JTestConfData[self.mode]['Offline'])>0:
            for ProjRun in self.JTestConfData[self.mode]['Offline']:
                #Create Json for Results TBD--
                self.CreateResultJson(ProjRun)
                if len(self.JTestConfData[self.mode]['Offline'][ProjRun])>0:
                   for tests in self.JTestConfData[self.mode]['Offline'][ProjRun]:
                        TraceUPL.files = {"WaveformFile":open(self.JTestConfData[self.mode]['Offline'][ProjRun][tests][1].replace('/','\\'),"rb")}
                        status = int(TraceUPL.PutRequest())
                        if status == 200:
                            t_end = time.time() + 60
                            while time.time() < t_end:
                                data = TCstatus.GetRequest()
                                if len(data['2']['displayDataChunk'])>0:
                                    #call Validation
                                    #----class call
                                    # print(tests) 
                                    if self.JMOIData[tests]['Status'] == True:
                                        Offval = OfflineValidation(TestID=tests,ProjectJson=self.JTestConfData[self.mode]['Offline'][ProjRun][tests][2],TracePath=self.JTestConfData[self.mode]['Offline'][ProjRun][tests][1])
                                    else: print(f'No Validation config for Test {tests}')
                                    # Offval.UpdateHeaderInfo()
                                    #call old scripts
                                    # os.system(f"py Scripts\TCvalidation.py {tests} {str(self.JTestConfData[self.mode]['Offline'][ProjRun][tests][1]).replace(' ','#')} {str(self.JTestConfData[self.mode]['Offline'][ProjRun][tests][2]).replace(' ','#')}")
                                    break
    def CreateResultJson(self,project):
        #create json file for report
        now = datetime.now()
        timestamp = now.strftime("%d%m%Y_%H%M%S")
        reponame = f'{self.mode}_{project}_{timestamp}_Offline'
        path ="Results\\JsonReports\\"+reponame+'.json'
        li = []        
        resjson = JsonOperations(path)
        resjson.update_file(li)
        #update path in TCP
        print(str(os.path.abspath(path)))
        self.JTCPData["test_config_data"]["Report_path"] = str(os.path.abspath(path))
        self.JTCP.update_file(self.JTCPData)
    def ResterExcerciser(self,mode):
        for apis in self.JapiData[mode]:
            print(apis)
            if 'EXCR_RS' in apis:
                rsobj = APIOperations(url=self.JapiData[mode][apis])
                if 'Get' in apis: rsobj.GetRequest()
                if 'Put' in apis:rsobj.PutRequest()
            #setpackets
            if 'EXCR_SPK_' in apis:
                if '_PutModulatorValues360' in apis:
                    inobj = APIOperations(url=self.JapiData['TPR']['EXCR_GetModulatorValues'],retype='json')
                    inres = indata = inobj.GetRequest()
                    rsobj = APIOperations(url=self.JapiData['TPR'][apis],json=indata)
                    outres = rsobj.PutRequest()
                elif '_PutRxCoil' in apis:
                    inobj = APIOperations(url=self.JapiData['TPR']['EXCR_GetRxCoilValues'],retype='json')
                    inres =indata = inobj.GetRequest()
                    rsobj = APIOperations(url=self.JapiData['TPR'][apis],json=indata)
                    outres =rsobj.PutRequest()
                elif '_PutTxCoil' in apis:
                    inobj = APIOperations(url=self.JapiData['TPR']['EXCR_GetTxCoil'],retype='json')
                    inres =indata = inobj.GetRequest()
                    rsobj = APIOperations(url=self.JapiData['TPR'][apis],json=indata)
                    outres =rsobj.PutRequest()
                elif '_PutPhaseSetting' in apis:
                    inobj = APIOperations(url=self.JapiData['TPR']['EXCR_GetDefaultPhaseSettings'],retype='json')
                    inres =indata = inobj.GetRequest()
                    rsobj = APIOperations(url=self.JapiData['TPR'][apis],json=indata)
                    outres =rsobj.PutRequest()
                elif '_PutQiPacketInformation' in apis:
                    Packetdata = JsonOperations('json/TPTSetPackets.json')
                    Packetdataval =Packetdata.read_file()
                    rsobj = APIOperations(url=self.JapiData['TPR'][apis],json=Packetdataval)
                    outres = rsobj.PutRequest()
                    inres=0
                elif '_PutSelectedQiSpecMode' in apis:
                    rsobj = APIOperations(url=self.JapiData['TPR'][apis])
                    outres =rsobj.PutRequest()
                    inres=0
                elif '_GetRxCoilRectifiedReadings' in apis:
                    rsobj = APIOperations(url=self.JapiData['TPR'][apis])
                    outres =rsobj.GetRequest()
                    inres=0
        #Enable clock if DUT is TPT
        if mode=='TPT':
            enclkobj = APIOperations(url=self.JapiData[mode]['EXCR_EnableClk'],json={"enableCloak":True})
            enclkobj.PutRequest()
# fltr = {"Pos":["00"],"TAD":True,"TADmode":"Automation Tests"}
# RunTests(fltr)