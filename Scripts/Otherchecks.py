import json
import requests
from MainModule import JsonOperations

class otherchecks():
    def __init__(self):
        #define jsons
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
    def MatchMOItestwithApp(self,mode):
        MOItests = []
        SWtests = []
        #Get tests list from MOIjson
        for header in self.JMOIData['C3_TPR']:
            if mode+'_TD_' in header:
                MOItests.append(self.JMOIData['C3_TPR'][header]['Testcase_Name'])
        #Get Tests from SW
        apptests = requests.get(f'http://localhost:{self.JtesterData[mode]["port"]}/api/TestConfiguration/GetTestCaseList/BPP')
        testdata = apptests.json()
        for phase in testdata[0]['children']:
            for test in phase['children']:
                SWtests.append(test['key'])
        if len(MOItests)>0 and len(SWtests)>0:
            print('Test Not macthing/avaialable with SW')
            for mts in MOItests:
                if mts not in SWtests:
                    print(mts)
            print('Tests not matching/avaialable with MOI')
            for sts in SWtests:
                if sts not in MOItests:
                    print(sts)
    def JSONLen(self):
        jpath = JsonOperations('json/t.json')
        jdata = jpath.read_file()
        cnt=0
        for data in jdata[0]['children']:
            cnt=cnt+len(data['children'])
        # print(cnt)
    def Gettestcases(self):
        IPJobj =  JsonOperations('json/t.json')
        IPdata = IPJobj.read_file()
        OPJobj = JsonOperations('json/t2.json')
        OPData = OPJobj.read_file()
        OPData.clear()
        OPData={}
        for chapter in IPdata:
            for subchapter in chapter["children"]:
                for testcase in subchapter["children"]:
                    key = ("_".join(testcase["key"].split("_")[0:4]))+"_"+testcase["key"].split("_")[len(testcase["key"].split("_"))-1]
                    print(key)
                    OPData['TPR_'+key]={}
                    OPData['TPR_'+key]['TC_id'] = key
                    OPData['TPR_'+key]['Testcase_Name'] = testcase["title"]
                    OPData['TPR_'+key]['TC_Chapter'] = subchapter["title"]
                    OPData['TPR_'+key]['Coils'] = testcase["additionalTags"][0]
        OPJobj.update_file(OPData)
    def TestcaseChecks(self,Mode='TPT'):
        testlist = []
        for TC in self.JMOIData[Mode]:
            if 'Status' in self.JMOIData[Mode][TC]:
                testlist.append(TC)
        print(len(testlist))
oc = otherchecks()
# oc.MatchMOItestwithApp('TPR')
# oc.Gettestcases()
        
oc.TestcaseChecks()
