from ast import literal_eval
import traceback
import uuid
import os
import zipfile
import csv
from Scripts.MainModule import JsonOperations,APIOperations,GeneralMethods
from datetime import datetime,date
import time
class OfflineValidationC3TPR():
    def __init__(self,TestID='',ProjectJson='',TracePath='',mode='TPR'):
        self.TestID =TestID
        self.ProjectJson = ProjectJson
        self.TracePath = TracePath
        self.mode = mode
        self.Header = {}
        self.timing_map = {}
        self.stability=None
        self.initialVoltage=None
        self.Plotstarttime=0
        self.TClogs = []
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
        self.Json_TC = self.JMOIData[self.mode][self.TestID]
        self.TimeTolr = self.JMOIData['TT_4']
        self.Json_Def = self.JMOIData['default_Values']
        self.JTestConf = JsonOperations('json/TestConfig.json')
        self.JTestConfData = self.JTestConf.read_file()  
        self.JPhaPkt = JsonOperations('json/PhasePackets.json')
        self.JPhaPktData = self.JPhaPkt.read_file()  
        self.JTCP = JsonOperations('json/Test_config_properties.json')
        self.JTCPData = self.JTCP.read_file()
        self.FinalRep = JsonOperations(self.JTCPData['test_config_data']['Report_path'])
        self.FinalRepData = self.FinalRep.read_file()
        self.conRep = JsonOperations(self.JsettingsData['ConsolidatedJSON'])
        self.conRepData = self.conRep.read_file()
        #Get Packets###########################
        self.PktAPI = APIOperations(url=self.JapiData[self.mode]['GetCCLinePackets'],retype='json')
        self.file_list = self.PktAPI.GetRequest()
        #Get Signales##########################
        self.AllChannelData = self.GetAllChannelData(index='2')
        self.AllChannelData3 =self.GetAllChannelData(index='3')
        #call func
        self.UpdateHeaderInfo()
        # print(self.Header)
        self.flows = self.SegricatePackets()
        self.ValidationForFlow()
    #1
    def UpdateHeaderInfo(self):
        now = datetime.now()
        timestamp = now.strftime("%d%m%Y_%H%M%S")
        jsondata = JsonOperations(self.ProjectJson)
        jsonValues = jsondata.read_file()
        self.Header['DBStatus']= 'NotUpdated'
        self.Header['UID'] = str(uuid.uuid1())
        self.Header['TestcaseID'] = self.Json_TC['TC_id']
        self.Header['TestcaseName']= self.Json_TC['Testcase_Name']
        # self.Header['ChapterID']=self.Json_TC['TC_ChapterID']
        self.Header['ChapterName']=self.Json_TC['TC_Chapter']
        self.Header['Transmitter']= self.JQIData[self.mode]['transmitterType']
        self.Header['potentialPower']=self.JQIData[self.mode]['potentialPower']
        self.Header['Coil'] = self.Json_TC['Coils']
        self.Header['SWVersion'] = jsonValues['TestToolInfo']['SoftwareVersion']
        self.Header['FWVersion'] = jsonValues['TestToolInfo']['FirmwareVersion']
        self.Header['HWVersion'] = jsonValues['TestToolInfo']['HardwareVersion']
        self.Header['BoardNo'] = jsonValues['TestToolInfo']['SerialNumber']
        self.Header['BoardModel'] = jsonValues['TestToolInfo']['ModelName']
        self.Header['CapturePath'] = self.TracePath
        pathlist = self.TracePath.split("\\")
        self.Header['ProjectName'] = pathlist[len(pathlist)-4]
        # self.Header['Run'] = int(pathlist[len(pathlist)-3].split('Run')[1])
        self.Header['Run'] = pathlist[len(pathlist)-3]
        #TBD 
        self.Header['TestedTime'] ='NA'
        self.Header['ValidatedTime']=timestamp
        self.Header['DUTName']= jsonValues['DutInfo']['BrandName']
        self.Header['DUTID']= jsonValues['DutInfo']['ProductName']
        self.Header['DUTSL']= jsonValues['DutInfo']['SerialNumber']
        self.Header['QiID'] = jsonValues['DutInfo']['QiID']
        self.Header['TestLab']=self.JQIData[self.mode]['testLab'] = jsonValues['TestLab']['LabName'] 
        self.Header['Engineer']=self.JQIData[self.mode]['testEngineer'] = jsonValues['TestLab']['TestEngineer']
        # self.Header['DUTName']= self.JQIData[self.mode]['manufacturer'] if jsonValues['DutInfo']['ProductName'] =='' else jsonValues['DutInfo']['ProductName']
        # self.Header['DUTID']=self.JQIData[self.mode]['modelNumber'] if jsonValues['DutInfo']['SerialNumber'] =='' else jsonValues['DutInfo']['SerialNumber']
        # self.Header['TestLab']=self.JQIData[self.mode]['testLab'] if jsonValues['TestLab']['LabName'] =='' else jsonValues['TestLab']['LabName']
        # self.Header['Engineer']=self.JQIData[self.mode]['testEngineer'] if jsonValues['TestLab']['TestEngineer'] =='' else jsonValues['TestLab']['TestEngineer']
    #2
    def SegricatePackets(self):
        packets = []
        limit=[0,len(self.file_list)-1]
        if len(limit)>1:
            id = limit[0]
            while id < limit[1]:
                start = 0
                end = 0
                if 'Ping Detected' in self.file_list[id].get('pktType'):
                    # print('pd',id)
                    #find Shutdown
                    sd= self.GetPacketDetails(packet='Shutdown',limit=[id,limit[1]])
                    if len(sd)>2:
                        # print('sd',sd)
                        #ensure no PD recevied btw PD-SD
                        ilPD = self.GetPacketDetails(packet='Ping Detected',limit=[id+1,sd[2]])
                        if len(ilPD)>1: id = ilPD[2]
                        # #check TestStop recevied before SD
                        # ilTS = self.GetPacketDetails(packet='Shutdown',limit=[id,sd[2]])
                        # if len(ilTS)>1: sd = ilTS
                        start = id
                        end = sd[2]
                        id = end
                    else:
                        #consider for the End of packet
                        start = id
                        end = limit[1]
                        id = end
                    #consider seq. has length > 3 and ss in flow
                    SS = self.GetPacketDetails(packet='Fop:',limit=[start,end])
                    if (end -start) >= 2 and len(SS)>1: 
                        packets = [start,end]
                else: id+=1
            # print(packets)
            #consider last seq.
            return packets
    #3
    def ValidationForFlow(self):     
        if len(self.flows)>0:
            self.CheckPktSequnce(self.flows)
            #Calculat finalresult
            self.Header['TCresult']=self.CheckFinalResult()
            self.UpdateToJsonReport()
            # print(self.timing_map)
    #4
    def CheckPktSequnce(self,limit):
        # print('initial',limit)
        PkseqData = self.JPhaPkt.read_file()
        packets = PkseqData[self.mode]['Packets']
        Pkseq = PkseqData[self.mode]['PacketSeq']
        PTPkts = []
        # print(Pkseq['Standard'])
        seq = Pkseq['Standard']
        # print('ini',seq)
        # if index==1 : seq.extend(self.JPhaPktData[self.mode]['PacketSeq']['127_nego'])
        # if index not in self.timing_map:self.timing_map[index]={}
        self.timing_map['Illegal']=[]
        seqpos = 1
        id = limit[0]+1
        while id < limit[1] and seqpos < len(seq):
            try:
                print(id,self.file_list[id].get('pktType'),self.file_list[id].get('value'),seq[seqpos],seq,limit)
                # if self.file_list[id].get('isFWTestermessage') == True and self.file_list[id].get('isTesterPkt') == True:
                pktstatus = False
                if len(packets[seq[seqpos]]['values'])>0:
                    if any(rs in self.file_list[id].get('value') for rs in packets[seq[seqpos]]['values']) and packets[seq[seqpos]]['Descr'] in self.file_list[id].get('pktType'):pktstatus=True
                else:
                    if packets[seq[seqpos]]['Descr'] in self.file_list[id].get('pktType'):pktstatus=True
                if pktstatus == True:
                        print('packet found',seq[seqpos])
                        if packets[seq[seqpos]]['PhaseID'] not in self.timing_map:self.timing_map[packets[seq[seqpos]]['PhaseID']]={}
                        if seq[seqpos] not in self.timing_map[packets[seq[seqpos]]['PhaseID']] : self.timing_map[packets[seq[seqpos]]['PhaseID']][seq[seqpos]] = []
                        # check response if required, id,self.file_list[id].get('startTime'),self.file_list[id].get('stopTime')
                        # if len(packets[seq[seqpos]]['Response'])>0:
                        rid = id+1
                        while rid <= limit[1]:
                            if self.file_list[rid].get('isFWTestermessage') == False and self.file_list[rid].get('isTesterPkt') == False:
                                if all(rs not in self.file_list[rid].get('pktType') for rs in packets[seq[seqpos]]['Response']):
                                    self.timing_map[packets[seq[seqpos]]['PhaseID']][seq[seqpos]].append([[id,self.file_list[id].get('startTime'),self.file_list[id].get('stopTime')]])
                                else:
                                    self.timing_map[packets[seq[seqpos]]['PhaseID']][seq[seqpos]].append([[id,self.file_list[id].get('startTime'),self.file_list[id].get('stopTime')],[rid,self.file_list[rid].get('pktType'),self.file_list[rid].get('startTime'),self.file_list[rid].get('stopTime')]])
                                break
                            elif self.file_list[rid].get('isFWTestermessage') == False and self.file_list[rid].get('isTesterPkt') == True:
                                self.timing_map[packets[seq[seqpos]]['PhaseID']][seq[seqpos]].append([[id,self.file_list[id].get('startTime'),self.file_list[id].get('stopTime')]])
                                # print('Received Pkt instead of response')
                                break
                            elif rid == limit[1]:
                                self.timing_map[packets[seq[seqpos]]['PhaseID']][seq[seqpos]].append([[id,self.file_list[id].get('startTime'),self.file_list[id].get('stopTime')]])
                                break
                            rid+=1
                        # if len(self.timing_map[index][packets[seq[seqpos]]['PhaseID']][seq[seqpos]]) == 0: self.timing_map[index][packets[seq[seqpos]]['PhaseID']][seq[seqpos]].append([[id,self.file_list[id].get('startTime'),self.file_list[id].get('stopTime')]])
                        # # Check for PT pkts
                        # if packets[seq[seqpos]]['PhaseID'] == 'PT' and 'PT' in self.file_list[id].get('description'):
                        #     id+=1
                        #     while id < limit[1]:
                        #         # print(id)
                        #         PTpktstatus = False
                        #         if self.file_list[id].get('isFWTestermessage') == False and self.file_list[id].get('isTesterPkt') == False:
                        #             if 'PT' in self.file_list[id].get('description'):
                        #                 print(PTPkts)
                        #                 for PTpkt in PTPkts:
                        #                     if packets[PTpkt]['Descr'] in self.file_list[id].get('pktType'):
                        #                         PTpktstatus=True
                        #                 # for PTpkt in PTPkts:
                        #                     # print(packets[PTpkt]['Descr'] ,self.file_list[id].get('pktType'))
                        #                     # if packets[PTpkt]['Descr'] in self.file_list[id].get('pktType') :
                        #                         # print(id,self.file_list[id].get('pktType'),self.file_list[id].get('value'),PTpkt)
                        #                         if packets[PTpkt]['PhaseID'] not in self.timing_map[index]:self.timing_map[index][packets[PTpkt]['PhaseID']]={}
                        #                         if PTpkt not in self.timing_map[index][packets[PTpkt]['PhaseID']] : self.timing_map[index][packets[PTpkt]['PhaseID']][PTpkt] = []
                        #                         # if len(packets[PTpkt]['Response'])>0:
                        #                         rid = id+1
                        #                         while rid < limit[1]:
                        #                             if self.file_list[rid].get('isFWTestermessage') == False and self.file_list[rid].get('isTesterPkt') == False:
                        #                                 if all(rs not in self.file_list[rid].get('pktType') for rs in packets[PTpkt]['Response']):
                        #                                     self.timing_map[index][packets[PTpkt]['PhaseID']][PTpkt].append([[id,self.file_list[id].get('startTime'),self.file_list[id].get('stopTime')]])
                        #                                 else:
                        #                                     self.timing_map[index][packets[PTpkt]['PhaseID']][PTpkt].append([[id,self.file_list[id].get('startTime'),self.file_list[id].get('stopTime')],[rid,self.file_list[rid].get('pktType'),self.file_list[rid].get('startTime'),self.file_list[rid].get('stopTime')]])
                        #                                 break
                        #                             elif self.file_list[rid].get('isFWTestermessage') == False and self.file_list[rid].get('isTesterPkt') == True:
                        #                                 self.timing_map[index][packets[PTpkt]['PhaseID']][PTpkt].append([[id,self.file_list[id].get('startTime'),self.file_list[id].get('stopTime')]])
                        #                                 # print('Received Pkt instead of response')
                        #                                 break
                        #                             rid+=1
                        #                         id=rid
                        #                     # else: id+=1
                        #                 if PTpktstatus == False : id+=1
                        #             else:
                        #                 print('Not expected1')
                        #                 #check for Cloak
                        #                 if 'Cloak' in self.file_list[id].get('pktType'):
                        #                     self.GetCloakPkts(index,id,packets)
                        #                     id+=1
                        #                 else:
                        #                     #add to illegal
                        #                     pkt = [id,self.file_list[id].get('pktType'),self.file_list[id].get('value'),self.file_list[id].get('startTime'),self.file_list[id].get('stopTime')]
                        #                     resp =None
                        #                     tmpid = id+1
                        #                     #check for response
                        #                     while tmpid < limit[1]:
                        #                         if self.file_list[tmpid].get('isFWTestermessage') == False and self.file_list[tmpid].get('isTesterPkt') == True:
                        #                             break
                        #                         elif self.file_list[tmpid].get('isFWTestermessage') == False and self.file_list[tmpid].get('isTesterPkt') == False:
                        #                             resp = [tmpid,self.file_list[tmpid].get('pktType'),self.file_list[tmpid].get('startTime'),self.file_list[tmpid].get('stopTime')]
                        #                         tmpid+=1
                        #                     self.timing_map[index]['Illegal'].append([pkt,resp])
                        #                     id=tmpid
                        #         else:id+=1
                        #Check for ID packet
                        # print(seq[seqpos])
                        if seq[seqpos] =='ID':
                            res = self.GetPayloadValue('Ext',id)
                            if all(rs in '0x01' for rs in res):
                                seq.extend(Pkseq['ExID'])
                            seq.extend(Pkseq['CNF'])
                        # # ExtID
                        # if seq[seqpos] =='ExID':
                        #     res = self.GetPayloadValue('Restricted',id)
                        #     # print(res,'ExID')
                        #     if all(rs in '0x00' for rs in res):
                        #         if index == 1:
                        #             seq.extend(Pkseq['127_nego'])
                        #         if index == 2:
                        #             seq.extend(Pkseq['360_nego'])
                        #             seq.extend(self.JPhaPktData[self.mode]['PacketSeq']['MPP_PT'])
                        #             PTPkts = self.JPhaPktData[self.mode]['PacketSeq']['MPP_PT']
                        #     else:
                        #         if index == 2:
                        #             # print('BPP mode')
                        #             seq.extend(self.JPhaPktData[self.mode]['PacketSeq']['BPP_PT'])
                        #             PTPkts = self.JPhaPktData[self.mode]['PacketSeq']['BPP_PT']
                        id=rid
                        seqpos+=1
                    # else:
                    #     print('Not expected2')
                    #     opt_pktstatus = False
                    #     opt_pkt = None
                    #     #if phase = Nego , check the packet is a optional packet
                    #     if packets[seq[seqpos]]['PhaseID'] == "Nego":
                    #         optseq = '360_nego_opt' if index == 2 else '128_nego_opt'
                    #         if optseq in  Pkseq:
                    #             print('Op pkt check nego')
                    #             for optnegopkt in Pkseq['360_nego_opt']:
                    #                 if len(packets[optnegopkt]['values']):
                    #                     if any(rs in self.file_list[id].get('value') for rs in packets[optnegopkt]['values']) and packets[optnegopkt]['Descr'] in self.file_list[id].get('pktType'):
                    #                         opt_pktstatus=True
                    #                         opt_pkt = optnegopkt
                    #                         break
                    #                 else:
                    #                     if packets[optnegopkt]['Descr'] in self.file_list[id].get('pktType'):
                    #                         opt_pktstatus=True
                    #                         opt_pkt = optnegopkt
                    #                         break
                    #     if opt_pktstatus == True:
                    #         if packets[opt_pkt]['PhaseID'] not in self.timing_map[index]:self.timing_map[index][packets[opt_pkt]['PhaseID']]={}
                    #         if opt_pkt not in self.timing_map[index][packets[opt_pkt]['PhaseID']] : self.timing_map[index][packets[opt_pkt]['PhaseID']][opt_pkt] = []
                    #         rid = id+1
                    #         while rid <= limit[1]:
                    #             if self.file_list[rid].get('isFWTestermessage') == False and self.file_list[rid].get('isTesterPkt') == True:
                    #                 if all(rs not in self.file_list[rid].get('pktType') for rs in packets[seq[seqpos]]['Response']):
                    #                     self.timing_map[index][packets[opt_pkt]['PhaseID']][opt_pkt].append([[id,self.file_list[id].get('startTime'),self.file_list[id].get('stopTime')]])
                    #                 else:
                    #                     self.timing_map[index][packets[opt_pkt]['PhaseID']][opt_pkt].append([[id,self.file_list[id].get('startTime'),self.file_list[id].get('stopTime')],[rid,self.file_list[rid].get('pktType'),self.file_list[rid].get('startTime'),self.file_list[rid].get('stopTime')]])
                    #                 break
                    #             elif self.file_list[rid].get('isFWTestermessage') == False and self.file_list[rid].get('isTesterPkt') == False:
                    #                 self.timing_map[index][packets[opt_pkt]['PhaseID']][opt_pkt].append([[id,self.file_list[id].get('startTime'),self.file_list[id].get('stopTime')]])
                    #                 # print('Received Pkt instead of response')
                    #                 break
                    #             rid+=1
                    #         id=rid
                    #         # seqpos+=1
                    #     else:
                    #         # id+=1
                    #         # pass
                    #         #check for ill / add pkts
                    #         # if self.file_list[id].get('description') !=  packets[seq[seqpos]]['PhaseID'] or (self.file_list[id].get('description') =='Nego' and any(rs in self.file_list[id].get('pktType') for rs in ['ADC','DSR','SADC','SADT'])):
                    #         pkt = [id,self.file_list[id].get('pktType'),self.file_list[id].get('value'),self.file_list[id].get('startTime'),self.file_list[id].get('stopTime')]
                    #         resp =None
                    #         tmpid = id+1
                    #         #check for response
                    #         while tmpid < limit[1]:
                    #             print(tmpid)
                    #             if self.file_list[tmpid].get('isFWTestermessage') == False and self.file_list[tmpid].get('isTesterPkt') == True:
                    #                 break
                    #             elif self.file_list[tmpid].get('isFWTestermessage') == False and self.file_list[tmpid].get('isTesterPkt') == False:
                    #                 resp = [tmpid,self.file_list[tmpid].get('pktType'),self.file_list[tmpid].get('startTime'),self.file_list[tmpid].get('stopTime')]
                    #             tmpid+=1
                    #         self.timing_map[index]['Illegal'].append([pkt,resp])
                    #         # print(tmpid,id)
                    #         id=tmpid
                else:id+=1
            except Exception as e:
                er = traceback.print_exc()
        print("val done")
        #add PD&SD
        self.timing_map['General'] ={
            "PD":[limit[0],self.file_list[limit[0]].get('startTime'),self.file_list[limit[0]].get('stopTime')],
            "SD":[limit[1],self.file_list[limit[1]].get('startTime'),self.file_list[limit[1]].get('stopTime')]
        }
        #Get Freq data
        FQPkt = self.GetPacketDetails(packet='Fop:',limit=limit)
        if len(FQPkt)>2:
            fq = GeneralMethods.GetFloatFromStr(self.file_list[FQPkt[2]].get("value"))
            self.timing_map['General']['FOP']=[FQPkt[2],FQPkt[1],FQPkt[1],fq[0]]
        # #GetLoads
        # self.timing_map[index]['Loads']={}
        # id = limit[0]
        # while id < limit[1]:
        #     # print(id,self.file_list[id].get('pktType'))
        #     if 'Set_Load' in self.file_list[id].get('pktType'):
        #         self.timing_map[index]['Loads'][self.file_list[id].get('pktType').split(':')[0].split(' ')[1]] = id
        #     id+=1
        # # apply validations
        self.timing_map['Timings']=self.timing_checks()
        self.timing_map['Measures'] = self.Measures()
        self.timing_map['OtherChecks'] = self.OtherChecks()
        #add Logs
        self.timing_map['TClogs'] = self.TClogs
        print(self.timing_map)
    ##support func______________________________
    def GetRunTime(self):
        TcStartAPI = APIOperations(url=self.JapiData[self.mode]['GetWaveformStartTime'],retype='json')
        TCstartTime = TcStartAPI.GetRequest()
        TcStopAPI = APIOperations(url=self.JapiData[self.mode]['GetWaveformStopTime'],retype='json')
        TCstopTime = TcStopAPI.GetRequest()
        return[TCstartTime,TCstopTime/100000000]
    def GetAllChannelData(self,index='2'):
        ACD={}
        TestTime = self.GetRunTime()
        if TestTime[1]/60 >15:
            print(TestTime[1]/60)
            plottime = int(((TestTime[1]*1000)/2.5)-80)
        else:
            plottime = int(((TestTime[1]*1000)/1.0510)-80)
        SignalAPI = APIOperations(url=self.JapiData[self.mode]['GetAllChannelData'],retype='json',param1=TestTime[1],param2=plottime)
        data = SignalAPI.GetRequest()
        if index in data:
            ACD['RV']=data[index]
            ACD['starttime'] = data[index]['absoluteStartTime']
            ACD['endtime'] = data[index]['absoluteEndTime']
            ACD['records'] = len(data[index]['displayDataChunk'])
            ACD['Diff'] =  ((ACD['endtime']-ACD['starttime'])/100000)
            ACD['Interval'] = (ACD['Diff']/ACD['records'])
        return ACD
    def GetPacketDetails(self,packet='',value=None,limit=[],timelimit=None):
        id = limit[0]
        if type(packet) != list:
            while id != limit[1]:
                if packet in self.file_list[id].get('pktType') and value in self.file_list[id].get('value') if value is not None else packet in self.file_list[id].get('pktType'):
                    if timelimit is None:
                        return[self.file_list[id].get('startTime'),self.file_list[id].get('stopTime'),id]
                    else:
                        if self.file_list[id].get('startTime') >= timelimit:
                            return[self.file_list[id].get('startTime'),self.file_list[id].get('stopTime'),id]
                if limit[0]<limit[1]:
                    id+=1
                else: id-=1
        else:
            while id != limit[1]:
                if all(rs in self.file_list[id].get('pktType') for rs in packet) and value in self.file_list[id].get('value') if value is not None else packet in self.file_list[id].get('pktType'):
                    return[self.file_list[id].get('startTime'),self.file_list[id].get('stopTime'),id]
                if limit[0]<limit[1]:
                    id+=1
                else: id-=1

        return[0]
    def Findflow(self,limit):
        id = limit[0]
        index = 0
        while id<limit[1]:
            if 'Identification' in self.file_list[id].get('pktType'):
                index=1
            if 'Specific Request' in self.file_list[id].get('pktType') and 'Frequency Selection: 360 Khz' in self.file_list[id].get('value'):
                index = 1
                break
            if 'Extended_Power_Receiver_Capabilities' in self.file_list[id].get('pktType'):
                index = 2
                break
            elif 'Modulation_Type' in self.file_list[id].get('pktType') and '33nF' in self.file_list[id].get('value'):
                index = 1
                break
            elif 'Modulation_Type' in self.file_list[id].get('pktType') and '33nF' not in self.file_list[id].get('value'):
                index = 2
                break
            elif 'FOP:' in  self.file_list[id].get('value'):
                if float(self.file_list[id].get('value').split(':')[1].split(' ')[0]) >300:
                    index =2
                    break
                else:
                    index=1
                    break
            id+=1
        # print(limit,index)
        return index
    def GetPayloadValue(self,payloadname,index):
        # print('Payload check',self.file_list[index].get('pktType'))
        results=[]
        for d1 in self.file_list[index]['header_Payload']['childelement']:
            for d2 in d1['childelement']:
                # print(d2['sDecodedValue'])
                if payloadname in d2['sDecodedValue']:
                    results.append(d2['sRawData'])
        return results 
    def timing_checks(self):
        AllTimings={"twake":[],"tstart":[]}
        #Twake check--------------------------------------------------------------------------
        remarks = []
        tol= self.Json_Def['twake']
        AllTimings['twake_exp'] = str(tol[0]-tol[1])+'-'+str(tol[0]+tol[1])
        AllTimings['twake']='NA'
        AllTimings['twake_res']='NA'
        try:
            if 'Ping' in self.timing_map and 'General' in self.timing_map:
                AllTimings['twake']=[]
                res = round((self.timing_map['Ping']['SS'][0][0][1] - self.timing_map['General']['PD'][1])*1000,2)+5.5
                if res < tol[0]-tol[1] or res >tol[0]+tol[1]:
                    AllTimings['twake'].append(res)
                    remarks.append(f"Measured twake {res} Not in Limit({(tol[0]-tol[1])}-{(tol[0]+tol[1])}) @index:{self.timing_map['General']['PD'][0]}")
                if len(remarks)>0:
                    AllTimings['twake_res'] ='Fail'
                    AllTimings['twake']=','.join(map(str,AllTimings['twake']))
                else:
                    AllTimings['twake_res'] ='Pass'
                    AllTimings['twake']='No Mismatch'
                AllTimings['twake_remark'] = '.'.join(remarks)
                self.update_TClogs("Timings",f"Twake Measured @index {self.timing_map['Ping']['SS'][0][0][0]} to @index {self.timing_map['General']['PD'][0]} is {res}")
        except Exception as e:
            er = traceback.print_exc()
            AllTimings['twake_remark'] = '' if er is None else er
            AllTimings['twake_res'] ='Fail'
        #Tstart check-------------------------------------------------------------------------
        remarks = []
        tol= self.Json_Def['tstart'] if 'tstart' not in self.Json_TC else self.Json_TC['tstart']
        AllTimings['tstart_exp'] = str(tol[0]-tol[1])+'-'+str(tol[0]+tol[1])
        AllTimings['tstart_res']='NA'
        AllTimings['tstart']='NA'
        Pktslist =[]
        for phase in self.timing_map:
            if phase in ['Ping','ID&CFG']:
                for pkts in self.timing_map[phase]:
                    pk = self.timing_map[phase][pkts]
                    if type(pk)==list:
                        Pktslist.append(pk[0][0])
        if len(Pktslist)>0:
            id=0
            AllTimings['tstart']=[]
            AllTimings['tstart_res']='Fail'
            while id < len(Pktslist)-1:
                res = round((Pktslist[id+1][1]-Pktslist[id][2])*1000,2)+5.5
                if res < tol[0]-tol[1] or res >tol[0]+tol[1]:
                    AllTimings['tstart'].append(res)
                    self.update_TClogs("Timings",f"Measured tstart {res} Not in Limit({(tol[0]-tol[1])}-{(tol[0]+tol[1])}) @index:{Pktslist[id][0]}")
                else:self.update_TClogs("Timings",f"Measured tstart {res} in Limit({(tol[0]-tol[1])}-{(tol[0]+tol[1])}) @index:{Pktslist[id][0]}")
                id+=1
            if len(remarks)>0:
                AllTimings['tstart_res'] ='Fail'
                AllTimings['tstart']=','.join(map(str,AllTimings['tstart']))
            else:
                AllTimings['tstart_res'] ='Pass'
                AllTimings['tstart']='No Mismatch'
            AllTimings['tstart_exp'] = str(tol[0]-tol[1])+'-'+str(tol[0]+tol[1])
            AllTimings['tstart_remark'] = '.'.join(remarks)
        # ##tsilent check-------------------------------------------------------------------------
        # remarks = []
        # tol= self.Json_Def['tsilent']
        # AllTimings['tsilent_exp'] = str(tol[0]-tol[1])+'-'+str(tol[0]+tol[1])
        # AllTimings['tsilent_res']='NA'
        # AllTimings['tsilent']='NA'
        # Pktslist =[]
        # for phase in self.timing_map:
        #     if phase in ['Ping','ID&CFG']:
        #         for pkts in self.timing_map[phase]:
        #             pk = self.timing_map[phase][pkts]
        #             if type(pk)==list:
        #                 Pktslist.append(pk[0][0])
        # if len(Pktslist)>0:
        #     id=0
        #     AllTimings['tsilent']=[]
        #     AllTimings['tsilent_res']='Fail'
        #     while id < len(Pktslist)-1:
        #         res = round((Pktslist[id+1][1]-Pktslist[id][2])*1000,2)
        #         if res < tol[0]-tol[1] or res >tol[0]+tol[1]:
        #             AllTimings['tsilent'].append(res)
        #             remarks.append(f"Measured tsilent {res} Not in Limit({(tol[0]-tol[1])}-{(tol[0]+tol[1])}) @index:{Pktslist[id][0]}")
        #         id+=1
        #     if len(remarks)>0:
        #         AllTimings['tsilent_res'] ='Fail'
        #         AllTimings['tsilent']=','.join(map(str,AllTimings['tsilent']))
        #     else:
        #         AllTimings['tsilent_res'] ='Pass'
        #         AllTimings['tsilent']='No Mismatch'
        #     AllTimings['tsilent_exp'] = str(tol[0]-tol[1])+'-'+str(tol[0]+tol[1])
        #     AllTimings['tsilent_remark'] = '.'.join(remarks)
        # #tresponse, pass all flows and get the tresponse for the pkts has response
        # remarks = []
        # tol= self.Json_Def['tresponse']
        # for phase in self.timing_map:
        #     if phase not in ['Illegal','Cloak']:
        #         for pkts in self.timing_map[phase]:
        #             pk = self.timing_map[phase][pkts]
        #             if type(pk) == list:
        #                 for pks in pk:
        #                     if type(pks) == list:
        #                         if len(pks)>1:
        #                             print(pks)
        #                             res = round((pks[1][2] - pks[0][2])*1000,2)
        #                             if res < tol[0]-tol[1] or res >tol[0]+tol[1]:
        #                                 AllTimings['tresponse'].append(res)
        #                                 remarks.append(f"Measured tresponse {res} Not in Limit({(tol[0]-tol[1])}-{(tol[0]+tol[1])}) @index:{pks[1][0]} ")
        # if len(remarks)>0:
        #     AllTimings['tresponse_res'] ='Fail'
        #     AllTimings['tresponse']=','.join(map(str,AllTimings['tresponse']))
        # else:
        #     AllTimings['tresponse_res'] ='Pass'
        #     AllTimings['tresponse']='No Mismatch'
        # AllTimings['tresponse_exp'] = str(tol[0]-tol[1])+'-'+str(tol[0]+tol[1])
        # AllTimings['tresponse_remark'] = '.'.join(remarks)
        # #Tintervel XCE-----------------------------------------------------------
        # remarks = []
        # tol= self.Json_Def['tintervalXCE-XCE']
        # AllTimings['tintervalXCE-XCE_exp'] = str(tol[0]-tol[1])+'-'+str(tol[0]+tol[1])
        # AllTimings['tintervalXCE-XCE_res']='NA'
        # AllTimings['tintervalXCE-XCE']='NA'
        # try:
        #     if 'PT' in self.timing_map[index]:
        #         if 'XCE' in self.timing_map[index]['PT']:
        #             XCEpkt = self.timing_map[index]['PT']['XCE']
        #             AllTimings['tintervalXCE-XCE']=[]
        #             if len(XCEpkt)>0:
        #                 id = 0
        #                 while id < len(XCEpkt)-1:
        #                     if (XCEpkt[id+1][0][0] - XCEpkt[id][0][0]) <=4:
        #                         res= round((XCEpkt[id+1][0][1] - XCEpkt[id][0][2])*1000,2)
        #                         if res < tol[0]-tol[1] or res >tol[0]+tol[1]:
        #                                 AllTimings['tintervalXCE-XCE'].append(res)
        #                                 remarks.append(f"Measured tintervalXCE-XCE {res} Not in Limit({(tol[0]-tol[1])}-{(tol[0]+tol[1])}) @index:{XCEpkt[id][0][0]}")
        #                     id+=1
        #                 if len(remarks)>0:
        #                     AllTimings['tintervalXCE-XCE_res'] ='Fail'
        #                     AllTimings['tintervalXCE-XCE']=','.join(map(str,AllTimings['tintervalXCE-XCE']))
        #                 else:
        #                     AllTimings['tintervalXCE-XCE_res'] ='Pass'
        #                     AllTimings['tintervalXCE-XCE']='No Mismatch'
        #                 AllTimings['tintervalXCE-XCE_remark'] = '.'.join(remarks)  
        # except Exception as e:
        #     er = traceback.print_exc()
        #     AllTimings['tintervalXCE-XCE_remark'] = '' if er is None else er
        #     AllTimings['tintervalXCE-XCE_res'] ='Fail'
        # #Treceived PLA--------------------------------------------------------------
        # remarks = []
        # tol= self.Json_Def['treceviedPLA-PLA']
        # AllTimings['treceviedPLA-PLA_exp'] = str(tol[0]-tol[1])+'-'+str(tol[0]+tol[1])
        # AllTimings['treceviedPLA-PLA_res']='NA'
        # AllTimings['treceviedPLA-PLA']='NA'
        # try:
        #     if 'PT' in self.timing_map[index]:
        #         if 'PLA' in self.timing_map[index]['PT']:
        #             PLApkt = self.timing_map[index]['PT']['PLA']
        #             AllTimings['treceviedPLA-PLA']=[]
        #             if len(PLApkt)>0:
        #                 id = 0
        #                 while id < len(PLApkt)-1:
        #                     res= round((PLApkt[id+1][0][1] - PLApkt[id][0][2])*1000,2)
        #                     if res < tol[0]-tol[1] or res >tol[0]+tol[1]:
        #                             AllTimings['treceviedPLA-PLA'].append(res)
        #                             remarks.append(f"Measured treceviedPLA-PLA {res} Not in Limit({(tol[0]-tol[1])}-{(tol[0]+tol[1])}) @index:{PLApkt[id][0][0]}")
        #                     id+=1
        #                 if len(remarks)>0:
        #                     AllTimings['treceviedPLA-PLA_res'] ='Fail'
        #                     AllTimings['treceviedPLA-PLA']=','.join(map(str,AllTimings['treceviedPLA-PLA']))
        #                 else:
        #                     AllTimings['treceviedPLA-PLA_res'] ='Pass'
        #                     AllTimings['treceviedPLA-PLA']='No Mismatch'
        #                 AllTimings['treceviedPLA-PLA_remark'] = '.'.join(remarks)  
        # except Exception as e:
        #     er = traceback.print_exc()
        #     AllTimings['treceviedPLA-PLA_remark'] = '' if er is None else er
        #     AllTimings['treceviedPLA-PLA_res'] ='Fail'
        # # print(AllTimings)
        return(AllTimings)
    def Measures(self):
        # self.GetInitailVoltage(idx)
        self.Plotstarttime = (self.AllChannelData['starttime']/100000)
        AllMeasures={}
            # self.XCEref=None
        if len(self.Json_TC['App_Measures'])>0:
            for apmes in self.Json_TC['App_Measures']:
                print(apmes)
                try:
                    if apmes in ['Vr']:
                        AllMeasures[apmes]=None
                        if self.Json_TC['App_Measures'][apmes]['packet'] =="SS":
                            if 'SS' in self.timing_map['Ping']:
                                res = self.CalculateVoltTwindow(self.timing_map['Ping']['SS'][0][0][0],self.AllChannelData,winsize=self.Json_TC['App_Measures'][apmes]['TwinSize'])
                                AllMeasures[apmes] =  res[0]
                        elif self.Json_TC['App_Measures'][apmes]['packet'] =="PD":
                            if 'PD' in self.timing_map['General']:
                                    res = self.CalculateVoltTwindow(self.timing_map['General']['PD'][0],self.AllChannelData,winsize=self.Json_TC['App_Measures'][apmes]['TwinSize'])
                                    AllMeasures[apmes] =  res[0]
                except Exception as e:
                    print(e)
                print(AllMeasures)
                #apply Validations
                exp = self.Json_TC['App_Measures'][apmes]['expected']
                if type(exp) != str:
                    if type(AllMeasures[apmes]) !=list:
                        # AllMeasures[str(apmes)+'_exp'] = self.Json_TC['App_Measures'][str(idx)][apmes]['expected']
                        AllMeasures[str(apmes)+'_res'] = 'Fail'
                        if AllMeasures[apmes] is not None:
                            reslt = self.check_measure(exp, AllMeasures[apmes],self.Json_TC['App_Measures'][apmes]['comp'])
                            AllMeasures[str(apmes)+'_exp']=reslt[2]+str(reslt[0][0]) if reslt[2] != 0 else str(reslt[0][0])+'-'+str(reslt[0][1])
                            AllMeasures[str(apmes)+'_res'] = reslt[1]
                        else:
                            AllMeasures[str(apmes)+'_exp'] = str(exp[0])+'-'+str(exp[1]) if len(exp)>1 else exp[0]
                    else:
                        resultli = []
                        for res in AllMeasures[apmes]:
                            reslt = self.check_measure(exp, res,self.Json_TC['App_Measures'][apmes]['comp'])
                            resultli.append(reslt[1])
                        AllMeasures[str(apmes)+'_exp']=reslt[2]+str(reslt[0][0]) if reslt[2] != 0 else str(reslt[0][0])+'-'+str(reslt[0][1])
                        AllMeasures[apmes] = ','.join(map(str,AllMeasures[apmes]))
                        AllMeasures[str(apmes)+'_res'] = 'Fail' if 'Fail' in resultli else 'Pass'
        print(AllMeasures)
        return AllMeasures
    def CPLmeasure(self,index,AllMeasures):
        #Get DPL
        DPL=None
        if 'SS' in self.timing_map[2]['Ping']:
            res = self.CalculateVoltTwindow(self.timing_map[2]['Ping']['SS'][0][0][0],self.AllChannelData,winsize=[9,11])
            DPL = res[0]
        #Get CPLs
        limit = [self.timing_map[2]['General']['PD'][0],len(self.file_list)-1]
        #find all Cloak 360 flows
        prevclk = 0
        cnt=0
        CLKtterminate = []
        Tcloak =[]
        CPL=[]
        id = limit[0]
        while id < limit[1]:
            if self.file_list[id].get('isFWTestermessage') ==False and self.file_list[id].get('isTesterPkt') ==True:
                if 'Cloak' in self.file_list[id].get('pktType'):
                    # print('clk',id,cnt)
                    cnt+=1
                    #Get SD
                    SDid = id+1
                    while SDid < limit[1]:
                        if any(rs in self.file_list[SDid].get('pktType') for rs in ['Shutdown','Test_Stop']):
                            break
                        SDid+=1
                    # print('SD',SDid)
                    if 'CLK_tterminate' in self.Json_TC['App_Measures'][index]:
                        if id != SDid:
                            CLKtterminate.append(round((self.file_list[SDid]['stopTime']*1000)-(self.file_list[id+1]['stopTime']*1000),2))
                        else:CLKtterminate.append(0)
                    if 'Tcloak' in self.Json_TC['App_Measures'][index]:
                        if cnt >1 and prevclk != 0:
                            #find PD 
                            PDid = id
                            while PDid > limit[0]:
                                if  'Ping Initiated' in self.file_list[PDid].get('pktType'):
                                    break
                                PDid-=1
                            Tcloak.append(round((self.file_list[PDid]['startTime']*1000)-(self.file_list[prevclk+1]['stopTime']*1000),2))
                    if cnt >1:
                        #cal CPLs
                        res = self.CalculateVoltTwindow(id,self.AllChannelData,winsize=[9,11])
                        CPL.append(res[0])
                    prevclk = id
                    id=SDid
                else:id+=1
            else:id+=1
        AllMeasures['DPL'] = DPL
        AllMeasures['CPLCheck'] = CPL
        AllMeasures['CLK_tterminate'] = CLKtterminate
        AllMeasures['Tcloak'] = Tcloak
        AllMeasures['CloakSeqCount'] = cnt-1
    def OtherChecks(self):
        AllOtherChecks = {}
        if len(self.Json_TC['other_checks_details'])>0:
            try:
                for apchk in self.Json_TC['other_checks_details']:
                    if apchk in ['Fq']:
                        AllOtherChecks[apchk]=None
                        exp =  self.Json_TC['other_checks_details'][apchk]['expected']
                        if exp == "Transmitter":
                            expval = self.JMOIData['Fpo'][self.JQIData[self.mode]['transmitterType']]
                            AllOtherChecks[apchk+'_exp'] =  str(expval[0])+'-'+str(expval[1])+' kHz'
                        else:
                            expval = exp
                            AllOtherChecks[apchk+'_exp'] = str(expval[0])+'-'+str(expval[1])+' kHz'
                        AllOtherChecks[apchk+'_res'] ='Fail'
                        print(AllOtherChecks)
                        if 'FOP' in self.timing_map['General']:
                            AllOtherChecks[apchk] = self.timing_map['General']['FOP'][3]
                            AllOtherChecks[apchk+'_res'] ='Pass' if AllOtherChecks[apchk] >= expval[0] and AllOtherChecks[apchk] <= expval[1] else 'Fail'
            except Exception as e:
                print(e)
        return AllOtherChecks
    def GetInitailVoltage(self,index):
        if str(index) in self.Json_TC['other_checks_details']:
            if 'CEStability' in self.Json_TC['other_checks_details'][str(index)]:
                try:
                    limit=[self.timing_map[2]['General']['PD'][0],self.timing_map[2]['General']['SD'][0]]
                    id = limit[0]
                    while id < limit[1]:
                        if 'MPP_XCE_Stabilized' in self.file_list[id].get('pktType'):
                            revid = id
                            while revid > limit[0]:
                                if self.file_list[revid].get('pktType') in ['Control Error','Extended Control Error']:
                                    self.stability=revid
                                    # print('stability',self.stability)
                                    #GetIntital Voltage
                                    # print(self.Json_TC['other_checks_details'])
                                    if 'InitialVoltage' in self.Json_TC['other_checks_details'][str(index)]:
                                        res = self.CalculateVoltTwindow(revid,self.AllChannelData)
                                        self.initialVoltage =  res[0]
                                    break
                                revid-=1
                            break
                        id+=1
                except Exception as e:
                    traceback.print_exc()
    def GetStableBtwLimits(self,limit):
        id = limit[0]
        XCEcount = 0
        while id < limit[1]:
            if any(rs in self.file_list[id].get('pktType') for rs in ['Extended Control Error','Control Error']): XCEcount +=1
            if 'MPP_XCE_Stabilized' in self.file_list[id].get('pktType'):
                revid = id
                while revid > limit[0]:
                    
                    if self.file_list[revid].get('pktType') in ['Control Error','Extended Control Error']:
                        # res = self.CalculateVoltTwindow(revid,self.AllChannelData)
                        return [revid,XCEcount]
                    revid-=1
            id+=1
        return None
    def CalculateVoltBtwStEd(self,indx,AllChannelData):
        starttime = (AllChannelData['starttime']/100000)
        vlot =0
        index = 0
        # print('chks',self.file_list[indx].get('startTime')*1000,((self.file_list[indx].get('startTime')*1000)-starttime-8))
        sindex = int(((((self.file_list[indx].get('startTime'))*1000)-starttime)-8)/AllChannelData['Interval'])
        eindex = int((((self.file_list[indx].get('stopTime'))*1000)-starttime)/AllChannelData['Interval'])
        id = sindex
        while id < eindex:
            if round(abs(AllChannelData['RV']['displayDataChunk'][id]),4) > vlot : 
                index=id
                vlot = round(abs(AllChannelData['RV']['displayDataChunk'][id]),4)
            id+=1
        # print('vlt',vlot)
        return [round(vlot,2), index]  
    def CalculateVoltTwindow(self,indx,AllChannelData,winsize=[8,11]):
        #calculate vrect min /max for all XCE twin time
        xceEtime = self.file_list[indx].get('stopTime')*1000
        xceSindex = int((xceEtime+winsize[0])/AllChannelData['Interval'])
        xceEindex = int((xceEtime+winsize[1])/AllChannelData['Interval'])
        id = xceSindex
        VRlist=[]
        print(xceSindex,xceEindex)
        # Vrectmax = 0
        while id <= xceEindex:
            VRlist.append(round(abs(AllChannelData['RV']['displayDataChunk'][id]),4))
            # if round(abs(AllChannelData['RV']['displayDataChunk'][id]),4) > Vrectmax or Vrectmax==0: 
            #     Vrectmax = round(abs(AllChannelData['RV']['displayDataChunk'][id]),4)
            id+=1
        print(VRlist)
        return [round((sum(VRlist)/len(VRlist)),3), id-1]
    def CalculateVoltTimePeriod(self,AllChannelData,stime,etime):
        #calculate vrect min /max for all XCE twin time
        xceEtime = etime*1000
        print((stime*1000)-self.Plotstarttime)
        xceSindex = int((stime*1000)/AllChannelData['Interval'])
        xceEindex = int((etime*1000)/AllChannelData['Interval'])
        id = xceSindex
        Vrectmax = 0
        while id <= xceEindex:
            if round(abs(AllChannelData['RV']['displayDataChunk'][id]),4) > Vrectmax or Vrectmax==0: 
                Vrectmax = round(abs(AllChannelData['RV']['displayDataChunk'][id]),4)
            id+=1
        return [round(Vrectmax,3), id-1]
    def CalculateVoltPlotIndex(self,index,AllChannelData):
        return round(abs(AllChannelData['RV']['displayDataChunk'][index]),4)
    def check_measure(self,exp_val,obsr_val,comp=0):
        res = None
        compval=0
        exp_vals=[]
        if obsr_val != None:
            if len(exp_val)==1:
                exp_vals.append(exp_val[0])
                if comp =='GTEQL':
                    if  obsr_val >= exp_val[0]:
                        res =  'Pass'
                    else:  
                        res = 'Fail'
                    compval='>='
                elif comp =='LTEQL':
                    if  obsr_val <= exp_val[0]:
                        res =  'Pass'
                    else:  
                        res = 'Fail'
                    compval='<='
                elif comp =='EQL':
                    if  obsr_val == exp_val[0]:
                        res =  'Pass'
                    else:  
                        res = 'Fail'
                    compval='=='
                #add for rql,lseql
            else:
                exp_vals=exp_val
                if obsr_val >= exp_vals[0] and obsr_val <= exp_vals[1]:
                    res =  'Pass'
                else:  
                    res = 'Fail'
        else:
            res = 'Fail'
        return [exp_vals,res,compval]
    def ReserveBitChek(self,Allchecks,index):
        #check Reserve bit value for all DUT packets exp Mfg reserve both flow
        res =[]
        val = []
        expected = self.Json_TC['other_checks_details'][str(index)]['ReserveBitChek']['expected']
        if len(self.timing_map[index]['General'])>0:
            limit1 = [self.timing_map[index]['General']['PD'][0],self.timing_map[index]['General']['SD'][0]]
            id = limit1[0]
            while id < limit1[1]:
                if self.file_list[id].get('isTesterPkt') == False and self.file_list[id].get('isFWTestermessage')==False:
                    #find and check all reserve bits
                    for d1 in self.file_list[id]['header_Payload']['childelement']:
                        for d2 in d1['childelement']:
                            if 'Reserved' in d2['sDecodedValue']:
                                if d2['sRawData'] != expected:
                                    val.append(d2['sRawData'])
                                    res.append(str(self.file_list[id]['pktType'])+'@index='+str(id)+':'+str(d2['sDecodedValue'])+str(d2['sRawData']))
                id+=1
            Allchecks['ReserveBitChek']=','.join(val) if len(val)>0 else 'No Mismatch'
            Allchecks['ReserveBitChek_exp']='Reserved='+str(expected)
            Allchecks['ReserveBitChek_res']='Pass' if len(res)==0 else 'Fail'
            Allchecks['ReserveBitChek_remark']=','.join(res)
    def OffsetValueCheck(self,Allchecks,index):
        res =[]
        val = []
        expected = self.Json_TC['other_checks_details'][str(index)]['OffsetValue']['expected']
        if len(self.timing_map[index]['General'])>0:
            limit1 = [self.timing_map[index]['General']['PD'][0],self.timing_map[index]['General']['SD'][0]]
            id = limit1[0]
            while id < limit1[1]:
                if 'MPP_FOD' in self.file_list[id].get('pktType') and 'Offset applied:' in self.file_list[id].get('value'):
                    offsetlist = GeneralMethods.GetFloatFromStr(self.file_list[id].get('value'))
                    print(offsetlist)
                    if len(offsetlist)>0:
                        if offsetlist[1] != expected: 
                            val.append(offsetlist[1])
                            res.append(f"Found offset value {offsetlist[1]}, but the Expected value is {expected} ")
                id+=1
        Allchecks['OffsetValue']=','.join(map(str,val)) if len(val)>0 else 'No Mismatch'
        Allchecks['OffsetValue_exp']=str(expected)
        Allchecks['OffsetValue_res']='Pass' if len(res)==0 else 'Fail'
        Allchecks['OffsetValue_remark']=','.join(res)
    def CheckFinalResult(self):
        res=[]
        checklist = self.Json_TC['Result_checks']
        if len(checklist)==0:
            return 'NA'
        else:
            for check in checklist:
                if check in self.timing_map['Measures']:
                    if self.timing_map['Measures'][check+'_res']=='Fail':res.append('Fail')
                if check in self.timing_map['OtherChecks']:
                    if self.timing_map['OtherChecks'][check+'_res']=='Fail':res.append('Fail')
        return 'Fail' if len(res)>0 else 'Pass'
    #to ensure the PLA pck Rect. Power is in limit of +/- 100mW of measured W from plot
    def PLA_PrectCheck(self,Allchecks,index):
        val=[]
        if 'PT' in self.timing_map[index]:
            if 'PLA' in self.timing_map[index]['PT']:
                if len(self.timing_map[index]['PT']['PLA'])>0:
                    for PLA in self.timing_map[index]['PT']['PLA']:
                        res = self.CalculateVoltTwindow(PLA[0][0],self.AllChannelData,winsize=[19,21])
                        Volt=res[0]
                        Curnt = round(abs(self.AllChannelData3['RV']['displayDataChunk'][res[1]]),2)
                        Plot_P = round((Volt*Curnt),2)
                        #Get Power from pkt
                        res= GeneralMethods.GetFloatFromStr(self.file_list[PLA[0][0]]['header_Payload']['childelement'][2]['childelement'][0]['sDescription'])
                        Pkt_P = res[0]
                        if abs(Pkt_P-Plot_P) >= 0.100:
                            val.append(f"Diff:{round(abs(Pkt_P-Plot_P),3)}@{PLA[0][0]}")
        Allchecks['PLA_PLOTvsPKT']=','.join(map(str,val)) if len(val)>0 else 'No Mismatch'
        Allchecks['PLA_PLOTvsPKT_exp']="+/-100mW"
        Allchecks['PLA_PLOTvsPKT_res']='Pass' if len(val)==0 else 'Fail'
    def UpdateToJsonReport(self):
        self.FinalRepData.append({'Header':self.Header,'SeqResults':self.timing_map})
        #Sorting TBD -- Not req
        self.FinalRep.update_file(self.FinalRepData)
        #update extracts to consolidated JSON file
        #Avoid already validate data TBD
        if self.Header['SWVersion'] not in self.conRepData: self.conRepData[self.Header['SWVersion']]={}
        if self.Header['FWVersion'] not in self.conRepData[self.Header['SWVersion']]: self.conRepData[self.Header['SWVersion']][self.Header['FWVersion']]={}
        if self.Header['HWVersion'] not in self.conRepData[self.Header['SWVersion']][self.Header['FWVersion']]: self.conRepData[self.Header['SWVersion']][self.Header['FWVersion']][self.Header['HWVersion']]={}
        if self.Header['BoardNo'] not in self.conRepData[self.Header['SWVersion']][self.Header['FWVersion']][self.Header['HWVersion']]: 
            self.conRepData[self.Header['SWVersion']][self.Header['FWVersion']][self.Header['HWVersion']][self.Header['BoardNo']]={}
        if str(self.Header['DUTName'])+'_'+str(self.Header['DUTID']) not in self.conRepData[self.Header['SWVersion']][self.Header['FWVersion']][self.Header['HWVersion']][self.Header['BoardNo']]: 
            self.conRepData[self.Header['SWVersion']][self.Header['FWVersion']][self.Header['HWVersion']][self.Header['BoardNo']][str(self.Header['DUTName'])+'_'+str(self.Header['DUTID'])]={}
        if self.Header['DUTSL'] not in self.conRepData[self.Header['SWVersion']][self.Header['FWVersion']][self.Header['HWVersion']][self.Header['BoardNo']][str(self.Header['DUTName'])+'_'+str(self.Header['DUTID'])]: 
            self.conRepData[self.Header['SWVersion']][self.Header['FWVersion']][self.Header['HWVersion']][self.Header['BoardNo']][str(self.Header['DUTName'])+'_'+str(self.Header['DUTID'])][self.Header['DUTSL']]={}
        # if self.Header['DUTID'] not in self.conRepData[self.Header['SWVersion']][self.Header['FWVersion']][self.Header['HWVersion']][self.Header['BoardNo']][self.Header['DUTName']]: 
        #     self.conRepData[self.Header['SWVersion']][self.Header['FWVersion']][self.Header['HWVersion']][self.Header['BoardNo']][self.Header['DUTName']][self.Header['DUTID']]={}
        if self.Header['ChapterName'] not in self.conRepData[self.Header['SWVersion']][self.Header['FWVersion']][self.Header['HWVersion']][self.Header['BoardNo']][str(self.Header['DUTName'])+'_'+str(self.Header['DUTID'])][self.Header['DUTSL']]: 
            self.conRepData[self.Header['SWVersion']][self.Header['FWVersion']][self.Header['HWVersion']][self.Header['BoardNo']][str(self.Header['DUTName'])+'_'+str(self.Header['DUTID'])][self.Header['DUTSL']][self.Header['ChapterName']]={}
        if self.Header['Coil'] not in self.conRepData[self.Header['SWVersion']][self.Header['FWVersion']][self.Header['HWVersion']][self.Header['BoardNo']][str(self.Header['DUTName'])+'_'+str(self.Header['DUTID'])][self.Header['DUTSL']][self.Header['ChapterName']]: 
            self.conRepData[self.Header['SWVersion']][self.Header['FWVersion']][self.Header['HWVersion']][self.Header['BoardNo']][str(self.Header['DUTName'])+'_'+str(self.Header['DUTID'])][self.Header['DUTSL']][self.Header['ChapterName']][self.Header['Coil']]={} 
        if self.Header['TestcaseID'] not in self.conRepData[self.Header['SWVersion']][self.Header['FWVersion']][self.Header['HWVersion']][self.Header['BoardNo']][str(self.Header['DUTName'])+'_'+str(self.Header['DUTID'])][self.Header['DUTSL']][self.Header['ChapterName']][self.Header['Coil']]: 
            self.conRepData[self.Header['SWVersion']][self.Header['FWVersion']][self.Header['HWVersion']][self.Header['BoardNo']][str(self.Header['DUTName'])+'_'+str(self.Header['DUTID'])][self.Header['DUTSL']][self.Header['ChapterName']][self.Header['Coil']][self.Header['TestcaseID']]=[] 
        ConTCdata={"Header" : {
            "UID":self.Header['UID'],
            "TestcaseID":self.Header['TestcaseID'],
            "TestcaseName":self.Header['TestcaseName'],
            "Transmitter":self.Header['Transmitter'],
            "CapturePath":self.Header['CapturePath'],
            "ProjectName":self.Header['ProjectName'],
            "Run":self.Header['Run'],
            "TestLab":self.Header['TestLab'],
            "Engineer":self.Header['Engineer'],
            "TCresult":self.Header['TCresult']
        },
        'Timings':{},'Measures':{},'OtherChecks':{}}
        # ConTCdata['Timings']=self.timing_map['Timings']
        ConTCdata['Measures']=self.timing_map['Measures']
        ConTCdata['OtherChecks']=self.timing_map['OtherChecks']
        #check that smae tests already available in the report, if so update with new results.
        testPresent = False
        indexid = 0
        if len(self.conRepData[self.Header['SWVersion']][self.Header['FWVersion']][self.Header['HWVersion']][self.Header['BoardNo']][str(self.Header['DUTName'])+'_'+str(self.Header['DUTID'])][self.Header['DUTSL']][self.Header['ChapterName']][self.Header['Coil']][self.Header['TestcaseID']])>0:
            #already same tests avaialble , check same project name and run name avaiable in json
            for avatests in self.conRepData[self.Header['SWVersion']][self.Header['FWVersion']][self.Header['HWVersion']][self.Header['BoardNo']][str(self.Header['DUTName'])+'_'+str(self.Header['DUTID'])][self.Header['DUTSL']][self.Header['ChapterName']][self.Header['Coil']][self.Header['TestcaseID']]:
                if avatests['Header']['ProjectName'] == ConTCdata['Header']['ProjectName'] and avatests['Header']['Run'] == ConTCdata['Header']['Run']: 
                    testPresent = True
                    break
                indexid+=1
        if testPresent==False:
            self.conRepData[self.Header['SWVersion']][self.Header['FWVersion']][self.Header['HWVersion']][self.Header['BoardNo']][str(self.Header['DUTName'])+'_'+str(self.Header['DUTID'])][self.Header['DUTSL']][self.Header['ChapterName']][self.Header['Coil']][self.Header['TestcaseID']].append(ConTCdata)
            self.conRep.update_file(self.conRepData)
        else:
            #replace with new Testresults
            self.conRepData[self.Header['SWVersion']][self.Header['FWVersion']][self.Header['HWVersion']][self.Header['BoardNo']][str(self.Header['DUTName'])+'_'+str(self.Header['DUTID'])][self.Header['DUTSL']][self.Header['ChapterName']][self.Header['Coil']][self.Header['TestcaseID']][indexid]=ConTCdata
            self.conRep.update_file(self.conRepData)
    def BitsCheck(self,index,AllOtherChecks):
        reslt = []
        resvalue =[]
        expvalue = []
        for BITSck in self.Json_TC['other_checks_details'][str(index)]['BitsCheck']:
            # print(BITSck)
            if  BITSck['refPrevious'] ==True:
                limit = [0,self.timing_map[index]['General']['PD'][0]-1]
            else:
                if 'refNextAll' in BITSck:
                    limit = [self.timing_map[index]['General']['SD'][0],len(self.file_list)-1]
                else:
                    limit = [self.timing_map[index]['General']['PD'][0],self.timing_map[index]['General']['SD'][0]]
            # if BITSck['refPrevious']  == True:
            #     limit = [0,self.timing_map[index]['General']['PD'][0]-1]
            # else:
            #     limit = [self.timing_map[index]['General']['PD'][0],self.timing_map[index]['General']['SD'][0]]
            print("bits",limit)
            #find the packet to check bits
            id = limit[0]
            pktindex = 0
            while id < limit[1]:
                # if self.file_list[id]['isFWTestermessage'] != True and self.file_list[id]['isTesterPkt'] != True:
                if BITSck['packet'][1] is None:
                    if BITSck['packet'][0] in self.file_list[id].get('pktType'):
                        pktindex = id
                        break
                else:
                    if BITSck['packet'][0] in self.file_list[id].get('pktType') and BITSck['packet'][1] in self.file_list[id].get('value'):
                        pktindex = id
                        break
                id+=1
            #once get pkt index performe bits checks
            if pktindex != 0:
                for ck in BITSck['Checks']:
                    if ck =='NEG':
                        expvalue.append(str(BITSck['packet'][0])+'_'+str(BITSck['packet'][1])+':NEG='+str(BITSck['Checks'][ck]['expected']))
                        # print('neg',self.file_list[pktindex]['header_Payload']['childelement'][4]['childelement'][0]['sRawData'],BITSck['Checks'][ck]['expected'])
                        if self.file_list[pktindex]['header_Payload']['childelement'][4]['childelement'][0]['sRawData'] != BITSck['Checks'][ck]['expected']:
                             reslt.append('Fail')
                        resvalue.append(str(BITSck['packet'][0])+'_'+str(BITSck['packet'][1])+':NEG='+str(self.file_list[pktindex]['header_Payload']['childelement'][4]['childelement'][0]['sRawData']))
                    if ck == 'Mjrver':
                        expvalue.append(str(BITSck['packet'][0])+'_'+str(BITSck['packet'][1])+':Mjrver='+str(BITSck['Checks'][ck]['expected']))
                        if self.file_list[pktindex]['header_Payload']['childelement'][0]['childelement'][0]['sRawData'] != BITSck['Checks'][ck]['expected']:
                             reslt.append('Fail')
                        resvalue.append(str(BITSck['packet'][0])+'_'+str(BITSck['packet'][1])+':Mjrver='+str(self.file_list[pktindex]['header_Payload']['childelement'][0]['childelement'][0]['sRawData']))
                    if ck == 'Mnrver':
                        expvalue.append(str(BITSck['packet'][0])+'_'+str(BITSck['packet'][1])+':Mnrver='+str(BITSck['Checks'][ck]['expected']))
                        if self.file_list[pktindex]['header_Payload']['childelement'][0]['childelement'][1]['sRawData'] != BITSck['Checks'][ck]['expected']:
                             reslt.append('Fail')
                        resvalue.append(str(BITSck['packet'][0])+'_'+str(BITSck['packet'][1])+':Mnrver='+str(self.file_list[pktindex]['header_Payload']['childelement'][0]['childelement'][1]['sRawData']))
                    
                    if ck=='Restricted':
                        expvalue.append(str(BITSck['packet'][0])+'_'+str(BITSck['packet'][1])+':Restricted='+str(BITSck['Checks'][ck]['expected']))
                        if self.file_list[pktindex]['header_Payload']['childelement'][1]['childelement'][0]['sRawData'] != BITSck['Checks'][ck]['expected']:
                             reslt.append('Fail')
                        resvalue.append(str(BITSck['packet'][0])+'_'+str(BITSck['packet'][1])+':Restricted='+str(self.file_list[pktindex]['header_Payload']['childelement'][1]['childelement'][0]['sRawData']))
                    
                    if ck=='PCHtime':
                        expvalue.append(str(BITSck['packet'][0])+'_'+str(BITSck['packet'][1])+':PCHtime='+str(BITSck['Checks'][ck]['expected']))
                        if self.file_list[pktindex]['header_Payload']['childelement'][0]['childelement'][0]['sRawData'] != BITSck['Checks'][ck]['expected']:
                             reslt.append('Fail')
                        resvalue.append(str(BITSck['packet'][0])+'_'+str(BITSck['packet'][1])+':PCHtime='+str(self.file_list[pktindex]['header_Payload']['childelement'][0]['childelement'][0]['sRawData']))
                    if ck=='CLkpingValue':
                        expvalue.append(str(BITSck['packet'][0])+'_'+str(BITSck['packet'][1])+':CLkpingValue='+str(BITSck['Checks'][ck]['expected']))
                        if self.file_list[pktindex]['header_Payload']['childelement'][1]['childelement'][1]['sRawData'] != BITSck['Checks'][ck]['expected']:
                             reslt.append('Fail')
                        resvalue.append(str(BITSck['packet'][0])+'_'+str(BITSck['packet'][1])+':CLkpingValue='+str(self.file_list[pktindex]['header_Payload']['childelement'][1]['childelement'][1]['sRawData']))
                    if ck=='CLkdelay':
                        expvalue.append(str(BITSck['packet'][0])+'_'+str(BITSck['packet'][1])+':CLkdelay='+str(BITSck['Checks'][ck]['expected']))
                        if self.file_list[pktindex]['header_Payload']['childelement'][1]['childelement'][0]['sRawData'] != BITSck['Checks'][ck]['expected']:
                             reslt.append('Fail')
                        resvalue.append(str(BITSck['packet'][0])+'_'+str(BITSck['packet'][1])+':CLkdelay='+str(self.file_list[pktindex]['header_Payload']['childelement'][1]['childelement'][0]['sRawData']))
                    if ck=='CLkdetctPing':
                        expvalue.append(str(BITSck['packet'][0])+'_'+str(BITSck['packet'][1])+':CLkdetctPing='+str(BITSck['Checks'][ck]['expected']))
                        if self.file_list[pktindex]['header_Payload']['childelement'][1]['childelement'][1]['sRawData'] != BITSck['Checks'][ck]['expected']:
                             reslt.append('Fail')
                        resvalue.append(str(BITSck['packet'][0])+'_'+str(BITSck['packet'][1])+':CLkdetctPing='+str(self.file_list[pktindex]['header_Payload']['childelement'][1]['childelement'][1]['sRawData']))
                    if ck=='CLkReason':
                        expvalue.append(str(BITSck['packet'][0])+'_'+str(BITSck['packet'][1])+':CLkReason='+str(BITSck['Checks'][ck]['expected']))
                        if BITSck['Checks'][ck]['expected'] not in self.file_list[pktindex]['header_Payload']['childelement'][0]['childelement'][1]['sDescription']:
                             reslt.append('Fail')
                        resvalue.append(str(BITSck['packet'][0])+'_'+str(BITSck['packet'][1])+':CLkReason='+str(self.file_list[pktindex]['header_Payload']['childelement'][0]['childelement'][1]['sDescription']))
                    if ck=='NegoPwr':
                        exp = float(BITSck['Checks'][ck]['expected'][0])
                        expvalue.append(str(BITSck['packet'][0])+'_'+str(BITSck['packet'][1])+':NegoPwr='+str(exp))
                        negolist = GeneralMethods.GetFloatFromStr(self.file_list[pktindex]['header_Payload']['childelement'][2]['childelement'][1]['sDescription'])
                        res = self.check_measure(BITSck['Checks'][ck]['expected'],negolist[0],BITSck['Checks'][ck]['comp'])
                        if res[1] == 'Fail':
                            reslt.append('Fail')
                        resvalue.append(str(BITSck['packet'][0])+'_'+str(BITSck['packet'][1])+':NegoPwr='+str(negolist[0]))
                    if ck=='PotentialPow':
                        exp = '-'.join(map(str,BITSck['Checks'][ck]['expected']))
                        expvalue.append(str(BITSck['packet'][0])+'_'+str(BITSck['packet'][1])+':PotentialPow='+str(exp))
                        potnlist = GeneralMethods.GetFloatFromStr(self.file_list[pktindex]['header_Payload']['childelement'][1]['childelement'][1]['sDescription'])
                        res = self.check_measure(BITSck['Checks'][ck]['expected'],potnlist[0],BITSck['Checks'][ck]['comp'])
                        if res[1] == 'Fail':
                            reslt.append('Fail')
                        resvalue.append(str(BITSck['packet'][0])+'_'+str(BITSck['packet'][1])+':PotentialPow='+str(potnlist[0]))
                    #TPT
                    if ck=='SSvalue':
                        expvalue.append(str(BITSck['packet'][0])+'_'+str(BITSck['packet'][1])+':SSvalue='+str(BITSck['Checks'][ck]['expected']))
                        if int(self.file_list[pktindex]['header_Payload']['childelement'][0]['childelement'][0]['sRawData']) < BITSck['Checks'][ck]['expected'][0]:
                             reslt.append('Fail')
                        resvalue.append(str(BITSck['packet'][0])+'_'+str(BITSck['packet'][1])+':SSvalue='+str(self.file_list[pktindex]['header_Payload']['childelement'][0]['childelement'][0]['sRawData']))
                    if ck=='Ext':
                        expvalue.append(str(BITSck['packet'][0])+'_'+str(BITSck['packet'][1])+':Ext='+str(BITSck['Checks'][ck]['expected']))
                        if self.file_list[pktindex]['header_Payload']['childelement'][2]['childelement'][0]['sRawData'] != BITSck['Checks'][ck]['expected']:
                             reslt.append('Fail')
                        resvalue.append(str(BITSck['packet'][0])+'_'+str(BITSck['packet'][1])+':Ext='+str(self.file_list[pktindex]['header_Payload']['childelement'][2]['childelement'][0]['sRawData']))
                    if ck=='XIDvalue':
                        expvalue.append(str(BITSck['packet'][0])+'_'+str(BITSck['packet'][1])+':XIDvalue='+str(BITSck['Checks'][ck]['expected']))
                        if self.file_list[pktindex]['header_Payload']['childelement'][0]['childelement'][0]['sRawData'] != BITSck['Checks'][ck]['expected']:
                             reslt.append('Fail')
                        resvalue.append(str(BITSck['packet'][0])+'_'+str(BITSck['packet'][1])+':XIDvalue='+str(self.file_list[pktindex]['header_Payload']['childelement'][0]['childelement'][0]['sRawData']))
            
            AllOtherChecks['BitsCheck'] =  ','.join(resvalue) if len(resvalue)>0 else 'NA'
            AllOtherChecks['BitsCheck_exp'] = ','.join(expvalue) if len(expvalue)>0 else 'NA'
            AllOtherChecks['BitsCheck_res'] ='Fail' if len(reslt)>0 else 'Pass'
    def PacketCheck(self,index,AllOtherChecks):
        reslt = []
        resvalue =[]
        expvalue = []
        for pkt in self.Json_TC['other_checks_details'][str(index)]['PacketCheck']:
            AllOtherChecks['PacketCheck_res']='Fail'
            # print('pkt',pkt)
            evalue = str(pkt['packet'][0])+'_'+str(pkt['packet'][1])+';Phase: '+str(pkt['phase']) if pkt['packet'][1]!= None else str(pkt['packet'][0])+';Phase: '+str(pkt['phase'])
            pres = 'None'
            #check for packets through the PD-SD limit
            if 'refCustom' in pkt:
                limit = self.RefCustomeLimitforPkt(pkt,index)
            else:
                if  pkt['refPrevious'] ==True:
                    limit = [0,self.timing_map[index]['General']['PD'][0]]
                else:
                    if 'refNextAll' in pkt:
                        limit = [self.timing_map[index]['General']['SD'][0],len(self.file_list)-1]
                    else:
                        limit = [self.timing_map[index]['General']['PD'][0],self.timing_map[index]['General']['SD'][0]]
            print('limit',limit)
            if limit != None:
                id = limit[0]
                pkcount = 0
                pkvcount = 0
                pkTresp = []
                Pkttimes = []
                PktInter = []
                PkRes =[]
                PktVal = []
                expPkt = [pkt['packet'][0],pkt['packet'][1]]
                preEndTime = 0
                while id < limit[1]:
                    #check if its packet
                    if self.file_list[id].get('isFWTestermessage') ==False and self.file_list[id].get('isTesterPkt') ==False:
                        if expPkt[0] in self.file_list[id].get('pktType') and expPkt[1] in self.file_list[id].get('value') if expPkt[1] is not None else expPkt[0] in self.file_list[id].get('pktType'):
                            # print(pkt['phase'],id,'-',self.file_list[id].get('description'))
                            if pkt['phase'] != None:
                                if pkt['phase'] == self.file_list[id].get('description'):
                                    pres = self.file_list[id].get('pktType')+'_'+self.file_list[id].get('value') if expPkt[1] is not None else self.file_list[id].get('pktType')
                                    pres=pres+'@'+str(id)+';Phase: '+str(pkt['phase'])
                                    if 'Pkt_count' in pkt: pkcount +=1
                                    if 'Pkt_Value' in pkt: PktVal.append(self.file_list[id].get('value').split('-')[0])
                                    if preEndTime!=0 : PktInter.append([round((self.file_list[id].get('startTime')*1000)-preEndTime,2),id])
                                    preEndTime=self.file_list[id].get('stopTime')*1000
                                    #to check proper resp for pkt
                                    rid = id+1
                                    resstatus = False
                                    #    print('resps',rid)
                                    while rid < limit[1]:
                                        # print(file_list[rid].get('pktType'))
                                        if self.file_list[rid].get('isTesterPkt') == False and self.file_list[rid].get('isFWTestermessage')== True:
                                            PkRes.append([self.file_list[rid].get('pktType'),rid])
                                            pkTresp.append([round((self.file_list[rid]['startTime']-self.file_list[id]['stopTime'])*1000,2),id])
                                            resstatus=True
                                            break
                                        elif self.file_list[rid].get('isTesterPkt') == False and self.file_list[rid].get('isFWTestermessage')== False:
                                            break
                                        rid+=1
                                    if resstatus==False: 
                                        PkRes.append(['NoResponse',rid-1])
                                    id=rid
                                else:id+=1
                        else:id+=1
                    else: 
                        id+=1
                if 'Pkt_response' in pkt:
                    evalue = evalue+';Response:'+'|'.join(pkt['Pkt_response'])
                    if len(PkRes)>0:
                        TPkRes=[]
                        for rs in PkRes:
                            if rs[0] not in pkt['Pkt_response']:
                                TPkRes.append('@'.join(map(str,rs)))
                        if len(TPkRes)>0:
                            reslt.append('Fail')
                            pres=pres+';Response:'+','.join(TPkRes)
                        else:pres=pres+';Response:'+'No mismatch'
                        # if any(rs not in pkt['Pkt_response'] for rs in PkRes): reslt.append('Fail')
                    else:
                        if 'NOResp' not in pkt['Pkt_response']:
                            reslt.append('Fail')
                        pres=pres+';Response:None'
                if 'Pkt_count' in pkt:
                    evalue = evalue+';Count:'+str(pkt['Pkt_count'])
                    pres=pres+';Count:'+str(pkcount)
                    if pkcount < pkt['Pkt_count']:reslt.append('Fail')
                if 'Pkt_Value' in pkt:
                    evalue = evalue+';Value:'+','.join(map(str,pkt['Pkt_Value']))
                    pres=pres+';Value:'+','.join(map(str,PktVal))
                    if any(rs not in pkt['Pkt_Value'] for rs in PktVal):
                        reslt.append('Fail')
                if 'Pkt_Tresponse' in pkt:
                    evalue = evalue+';Tresponse:'+'-'.join(str(a) for a in pkt['Pkt_Tresponse'])+'ms'
                    if len(pkTresp)>0:
                        TpkTresp=[]
                        for rs in pkTresp:
                            if rs[0] < pkt['Pkt_Tresponse'][0] or rs[0] > pkt['Pkt_Tresponse'][1]:
                                TpkTresp.append(str(rs[0])+'@'+str(rs[1]))
                        if len(TpkTresp)>0:
                            reslt.append('Fail')
                            pres=pres+';Tresponse:'+','.join(TpkTresp)
                        else:pres=pres+';Tresponse:'+'No mismatch'
                        # pres=pres+';Tresponse:'+'|'.join(str(a) for a in pkTresp)
                        # if any(rs < pkt['Pkt_Tresponse'][0] or rs > pkt['Pkt_Tresponse'][1] for rs in pkTresp): reslt.append('Fail')
                    else:
                        pres=pres+';Tresponse:None'
                        reslt.append('Fail')
                if 'Pkt_Interval' in pkt:
                    TPktInter=[]
                    evalue = evalue+';Interval:'+'-'.join(str(a) for a in pkt['Pkt_Interval'])+'ms'
                    if len(PktInter)>0:
                        for rs in PktInter:
                            if rs[0] < pkt['Pkt_Interval'][0] or rs[0] > pkt['Pkt_Interval'][1]:
                                TPktInter.append(str(rs[0])+'@'+str(rs[1]))
                        if len(TPktInter)>0:
                            reslt.append('Fail')
                            pres=pres+';Interval:'+','.join(TPktInter)
                        else:pres=pres+';Interval:'+'No mismatch'
                        # pres=pres+';Interval:'+'|'.join(str(a) for a in PktInter)
                        # if any(rs != pkt['Pkt_Interval'] for rs in PktInter): reslt.append('Fail')
                    else:
                        pres=pres+';Interval:None'
                        reslt.append('Fail')
                expvalue.append(evalue)
                resvalue.append(pres)
            AllOtherChecks['PacketCheck_exp'] = ','.join(expvalue)
            AllOtherChecks['PacketCheck'] = ','.join(resvalue)
            AllOtherChecks['PacketCheck_res'] = 'Pass' if len(reslt) == 0 else 'Fail'
    def GetCloakPkts(self,index,id,packets):
        # print('clk',id,len(self.file_list))
        clkseq =0
        self.timing_map[index]['Cloak']={}
        while id < len(self.file_list)-1:
            print(id)
            # self.timing_map[index]['Cloak'][clkseq]={}
            if 'Cloak' in self.file_list[id].get('pktType') and self.file_list[id].get('isFWTestermessage') == False and self.file_list[id].get('isTesterPkt') == False:
                print('clkpkt',id)
                clkseq+=1
                tid = id+1
                while tid < len(self.file_list)-1:
                    if self.file_list[tid].get('isFWTestermessage') == False and self.file_list[tid].get('isTesterPkt') == True:
                            if all(rs not in self.file_list[tid].get('pktType') for rs in packets['CLK']['Response']):
                                self.timing_map[index]['Cloak'][clkseq]=[[id,self.file_list[id].get('startTime'),self.file_list[id].get('stopTime')]]
                            else:
                                self.timing_map[index]['Cloak'][clkseq] = [[id,self.file_list[id].get('startTime'),self.file_list[id].get('stopTime')],[tid,self.file_list[tid].get('pktType'),self.file_list[tid].get('startTime'),self.file_list[tid].get('stopTime')]]
                            break
                    elif self.file_list[tid].get('isFWTestermessage') == False and self.file_list[tid].get('isTesterPkt') == False:
                        self.timing_map[index]['Cloak'][clkseq] =[[id,self.file_list[id].get('startTime'),self.file_list[id].get('stopTime')]]
                        # print('Received Pkt instead of response')
                        break
                    tid+=1
                id=tid
                #find next clk flow
                #1.Find next PD
                PD = self.GetPacketDetails(packet='Ping Initiated',limit=[id,len(self.file_list)])
                if len(PD)>1:
                    #2.Get Cloak Packet
                    CLK = self.GetPacketDetails(packet='Cloak',limit=[PD[2],PD[2]+1])
                    if len(CLK)> 1:
                        id = CLK[2]
                    else:
                        print('CLK ILL')
                        #clk not received hence move all packets to the Illigal
                        id=PD[2]+1
                        while True:
                            if self.file_list[id].get('isFWTestermessage') == False and self.file_list[id].get('isTesterPkt') == True:
                                pkt = [id,self.file_list[id].get('pktType'),self.file_list[id].get('value'),self.file_list[id].get('startTime'),self.file_list[id].get('stopTime')]
                                resp =None
                                tmpid = id+1
                                #check for response
                                while tmpid < len(self.file_list)-1:
                                    if self.file_list[tmpid].get('isFWTestermessage') == False and self.file_list[tmpid].get('isTesterPkt') == True:
                                        break
                                    elif self.file_list[tmpid].get('isFWTestermessage') == False and self.file_list[tmpid].get('isTesterPkt') == False:
                                        resp = [tmpid,self.file_list[tmpid].get('pktType'),self.file_list[tmpid].get('startTime'),self.file_list[tmpid].get('stopTime')]
                                    tmpid+=1
                                self.timing_map[index]['Illegal'].append([pkt,resp])
                            if any(rs in self.file_list[id].get('pktType') for rs in ['Test_Stop','Shutdown']): break
                            id+=1
                else:
                    id+=1
                    break
            else:id+=1
        print(self.timing_map[index])
    def RefCustomeLimitforPkt(self,pkt,index):
        sindex = None
        eindex = None
        reslimit = []
        if pkt['refCustom']['Type'] =='PktAFPeriod':
            #find packet
            expPkt = pkt['refCustom']['values']['Packet']
            phase = pkt['refCustom']['values']['phase']
            phstatus = 0
            limit = [self.timing_map[index]['General']['PD'][0],self.timing_map[index]['General']['SD'][0]]
            id = limit[0]
            while id < limit[1]:
                if phase == None:
                    phstatus =1
                else:
                    if phase == self.file_list[id].get('description'):phstatus=1
                if phstatus==1:
                    if expPkt[0] in self.file_list[id].get('pktType') and expPkt[1] in self.file_list[id].get('value') if expPkt[1] is not None else expPkt[0] in self.file_list[id].get('pktType'):
                        sindex = id
                        #find duration
                        maxtime = (self.file_list[id].get('stopTime')*1000)+pkt['refCustom']['values']['duration']
                        tid = id+1
                        while tid< limit[1]:
                            if (self.file_list[tid]['startTime']*1000) >= maxtime:
                                eindex = tid
                                break
                            tid+=1
                        break
                id+=1
        elif pkt['refCustom']['Type'] == 'PktWithCnt':
            expPkt = pkt['refCustom']['values']['Packet']
            Pktcnt = pkt['refCustom']['values']['Count']
            limit = [self.timing_map[index]['General']['PD'][0],self.timing_map[index]['General']['SD'][0]]
            id = limit[0]
            eindex=limit[1]
            strtpkt_status = 0
            while id < limit[1]:
                if expPkt[1] is not None:
                    if expPkt[0] in self.file_list[id].get('pktType') and expPkt[1] in self.file_list[id].get('value'): 
                        strtpkt_status=1
                        break
                else:
                    if expPkt[0] in self.file_list[id].get('pktType'):
                        strtpkt_status=1
                        break
                id+=1
            if strtpkt_status==1:
                pkt = pkt['packet']
                id2 = id
                cnt = 0
                while id2 < limit[1]:
                    if pkt[1] is not None:
                        if pkt[0] in self.file_list[id2].get('pktType') and pkt[1] in self.file_list[id2].get('value'): 
                            cnt+=1
                            if cnt == Pktcnt: break
                    else:
                        if pkt[0] in self.file_list[id2].get('pktType'):
                            cnt+=1
                            if cnt == Pktcnt: break
                    id2+=1
                eindex = id2+1
            sindex = id
        elif pkt['refCustom']['Type'] == "SoonAFPkt":
            expPkt = pkt['refCustom']['values']['Packet']
            limit = [self.timing_map[index]['General']['PD'][0],self.timing_map[index]['General']['SD'][0]]
            epkt = self.GetPacketDetails(packet=expPkt[0],limit=limit)
            if len(epkt)>1:
                sindex = epkt[2]
                #check that next is a packet
                id = sindex+1
                while id < limit[1]:
                    if self.file_list[id]['isTesterPkt'] == False and self.file_list[id]['isFWTestermessage'] == False:
                        eindex = id+1
                        break
                    id+=1
        if sindex != None:
            if eindex != None:
                return [sindex,eindex]
            else:
                return [sindex,limit[1]]
        else: return None  
    def EyeDigramCheck(self,AllOtherChecks,index):
        AllOtherChecks['Npass'] = None
        AllOtherChecks['Npass_exp'] = int(self.Json_TC['other_checks_details'][str(index)]['Npass']['expected'])
        AllOtherChecks['Npass_res'] = "Fail"

        AllOtherChecks['EyeDigramCheck_Phase']=[]
        AllOtherChecks['EyeDigramCheck_Phase_res']='Fail'
        Expvalue_phase = self.Json_TC['other_checks_details'][str(index)]['EyeDigramCheck_Phase']
        AllOtherChecks['EyeDigramCheck_Phase_exp']=f"Phase:AmplitudeDiff>={Expvalue_phase['AmplitudeDiff'][0]},SNR>={Expvalue_phase['SNR'][0]},Fclk={'-'.join(map(str,Expvalue_phase['Fclk']))},HalfBitPeriod={'-'.join(map(str,Expvalue_phase['HalfBitPeriod']))},EyeWidth>={Expvalue_phase['EyeWidth'][0]}"
        AllOtherChecks['EyeDigramCheck_Magnitude']=[]
        AllOtherChecks['EyeDigramCheck_Magnitude_res']='Fail'
        Expvalue_mag = self.Json_TC['other_checks_details'][str(index)]['EyeDigramCheck_Magnitude']
        AllOtherChecks['EyeDigramCheck_Magnitude_exp']=f"Phase:AmplitudeDiff>={Expvalue_mag['AmplitudeDiff'][0]},SNR>={Expvalue_mag['SNR'][0]},Fclk={'-'.join(map(str,Expvalue_mag['Fclk']))},HalfBitPeriod={'-'.join(map(str,Expvalue_mag['HalfBitPeriod']))},EyeWidth>={Expvalue_mag['EyeWidth'][0]}"
        Npass_Phase = 0
        Npass_magnitude = 0
        res = []
        check_res_mag =[]
        check_res_phase=[]
        EyEdigpath = None
        EyeResult={"Phase":{},"Magnitude":{}}
        #Update Exp
        Expvals = []
        TCfolderList = self.TracePath.split("\\")
        path = "\\".join(TCfolderList[0:len(TCfolderList)-1])
        #Unzip Eyedig file
        for subdir, dirs, files in os.walk(path):
            for file in files:
                if file.endswith('.GrlEyeInfo'):
                    if os.path.exists(os.path.join(subdir,'EyeDebugInfo')):
                        EyEdigpath = os.path.join(subdir,'EyeDebugInfo')
                    else:
                        #Perform unzip
                        with zipfile.ZipFile(os.path.join(subdir,file), 'r') as zip_ref:
                            zip_ref.extractall(os.path.join(subdir,'EyeDebugInfo'))
                        EyEdigpath = os.path.join(subdir,'EyeDebugInfo')
        if EyEdigpath is not None:
            MagnitudeResultCSV = []
            PhaseResultCSV = []
            Temresult = {"Phase":{},"Magnitude":{}}
            for subdir, dirs, files in os.walk(path):
                for file in files:
                    if 'Eye_Magnitude_' in file and file.endswith("Results_EYE.csv"):
                        MagnitudeResultCSV.append(os.path.join(subdir,file))
                    if 'Eye_Phase' in file and file.endswith("Results_EYE.csv"):
                        PhaseResultCSV.append(os.path.join(subdir,file))
            if len(MagnitudeResultCSV) >0:
                for MagPath in MagnitudeResultCSV:
                    PktName = (MagPath.split("\\")[len(MagPath.split("\\"))-2]).split("_TS")[0]
                    Temresult["Magnitude"][PktName]={}
                    # reading the CSV file
                    data = open(MagPath)
                    csvFile = csv.reader(data)
                    #update csvdata to res
                    for lines in csvFile:
                        if len(lines)>0:
                            if 'AmplitudeHigh' in lines: Temresult["Magnitude"][PktName]['AmplitudeHigh'] = float(lines[1])
                            if 'AmplitudeLow' in lines: Temresult["Magnitude"][PktName]['AmplitudeLow'] = float(lines[1])
                            if 'SNR' in lines: Temresult["Magnitude"][PktName]['SNR'] = float(lines[1])
                            if 'Fclk' in lines: Temresult["Magnitude"][PktName]['Fclk'] = float(lines[1])
                            if 'HalfBitPeriod' in lines: Temresult["Magnitude"][PktName]['HalfBitPeriod'] = float(lines[1])
                            if 'EyeWidth' in lines: Temresult["Magnitude"][PktName]['EyeWidth'] = float(lines[1])
            if len(PhaseResultCSV) >0:
                for MagPath in PhaseResultCSV:
                    PktName = (MagPath.split("\\")[len(MagPath.split("\\"))-2]).split("_TS")[0]
                    Temresult['Phase'][PktName]={}
                    # reading the CSV file
                    data = open(MagPath)
                    csvFile = csv.reader(data)
                    #update csvdata to res
                    for lines in csvFile:
                        if len(lines)>0:
                            if 'AmplitudeHigh' in lines: Temresult['Phase'][PktName]['AmplitudeHigh'] = float(lines[1])
                            if 'AmplitudeLow' in lines: Temresult['Phase'][PktName]['AmplitudeLow'] = float(lines[1])
                            if 'SNR' in lines: Temresult['Phase'][PktName]['SNR'] = float(lines[1])
                            if 'Fclk' in lines: Temresult['Phase'][PktName]['Fclk'] = float(lines[1])
                            if 'HalfBitPeriod' in lines: Temresult['Phase'][PktName]['HalfBitPeriod'] = float(lines[1])
                            if 'EyeWidth' in lines: Temresult['Phase'][PktName]['EyeWidth'] = float(lines[1])
            if len(Temresult['Magnitude'])>0:
                try:
                    for pkts in Temresult['Magnitude']:
                        Ampdiff = round((Temresult['Magnitude'][pkts]['AmplitudeHigh']-Temresult['Magnitude'][pkts]['AmplitudeLow'])*1000,2)
                        EyeResult['Magnitude'][pkts]={}
                        EyeResult['Magnitude'][pkts]['Amplitude Diff'] = f"{Ampdiff}|>={Expvalue_mag['AmplitudeDiff'][0]}|Pass" if Ampdiff >= Expvalue_mag['AmplitudeDiff'][0] else f"{Ampdiff}|>={Expvalue_mag['AmplitudeDiff'][0]}|Fail"
                        EyeResult['Magnitude'][pkts]['SNR'] = f"{Temresult['Magnitude'][pkts]['SNR']}|>={Expvalue_mag['SNR'][0]}|Pass" if Temresult['Magnitude'][pkts]['SNR'] >= Expvalue_mag['SNR'][0] else f"{Temresult['Magnitude'][pkts]['SNR']}|>={Expvalue_mag['SNR'][0]}|Fail"
                        EyeResult['Magnitude'][pkts]['Fclk'] = f"{Temresult['Magnitude'][pkts]['Fclk']}|{Expvalue_mag['Fclk'][0]}-{Expvalue_mag['Fclk'][1]}|Pass" if Temresult['Magnitude'][pkts]['Fclk'] >= Expvalue_mag['Fclk'][0] and Temresult['Magnitude'][pkts]['Fclk'] <= Expvalue_mag['Fclk'][1] else f"{Temresult['Magnitude'][pkts]['Fclk']}|{Expvalue_mag['Fclk'][0]}-{Expvalue_mag['Fclk'][1]}|Fail"
                        EyeResult['Magnitude'][pkts]['HalfBitPeriod'] = f"{Temresult['Magnitude'][pkts]['HalfBitPeriod']}|{Expvalue_mag['HalfBitPeriod'][0]}-{Expvalue_mag['HalfBitPeriod'][1]}|Pass" if Temresult['Magnitude'][pkts]['HalfBitPeriod'] >= Expvalue_mag['HalfBitPeriod'][0] and Temresult['Magnitude'][pkts]['HalfBitPeriod'] <= Expvalue_mag['HalfBitPeriod'][1] else f"{Temresult['Magnitude'][pkts]['HalfBitPeriod']}|{Expvalue_mag['HalfBitPeriod'][0]}-{Expvalue_mag['HalfBitPeriod'][1]}|Fail"
                        EyeResult['Magnitude'][pkts]['EyeWidth'] = f"{Temresult['Magnitude'][pkts]['EyeWidth']}|>={Expvalue_mag['EyeWidth'][0]}|Pass" if Temresult['Magnitude'][pkts]['EyeWidth'] >= Expvalue_mag['EyeWidth'][0] else f"{Temresult['Magnitude'][pkts]['EyeWidth']}|>={Expvalue_mag['EyeWidth'][0]}|Fail"
                except Exception as e:
                    pass 
            if len(Temresult['Phase'])>0:
                try:
                    for pkts in Temresult['Phase']:
                        Ampdiff = round((Temresult['Phase'][pkts]['AmplitudeHigh']-Temresult['Phase'][pkts]['AmplitudeLow'])*1000,2)
                        EyeResult['Phase'][pkts]={}
                        EyeResult['Phase'][pkts]['Amplitude Diff'] = f"{Ampdiff}|>={Expvalue_phase['AmplitudeDiff'][0]}|Pass" if Ampdiff >= Expvalue_phase['AmplitudeDiff'][0] else f"{Ampdiff}|>={Expvalue_phase['AmplitudeDiff'][0]}|Fail"
                        EyeResult['Phase'][pkts]['SNR'] = f"{Temresult['Phase'][pkts]['SNR']}|>={Expvalue_phase['SNR'][0]}|Pass" if Temresult['Phase'][pkts]['SNR'] >= Expvalue_phase['SNR'][0] else f"{Temresult['Phase'][pkts]['SNR']}|>={Expvalue_phase['SNR'][0]}|Fail"
                        EyeResult['Phase'][pkts]['Fclk'] = f"{Temresult['Phase'][pkts]['Fclk']}|{Expvalue_phase['Fclk'][0]}-{Expvalue_phase['Fclk'][1]}|Pass" if Temresult['Phase'][pkts]['Fclk'] >= Expvalue_phase['Fclk'][0] and Temresult['Phase'][pkts]['Fclk'] <= Expvalue_phase['Fclk'][1] else f"{Temresult['Phase'][pkts]['Fclk']}|{Expvalue_phase['Fclk'][0]}-{Expvalue_phase['Fclk'][1]}|Fail"
                        EyeResult['Phase'][pkts]['HalfBitPeriod'] = f"{Temresult['Phase'][pkts]['HalfBitPeriod']}|{Expvalue_phase['HalfBitPeriod'][0]}-{Expvalue_phase['HalfBitPeriod'][1]}|Pass" if Temresult['Phase'][pkts]['HalfBitPeriod'] >= Expvalue_phase['HalfBitPeriod'][0] and Temresult['Phase'][pkts]['HalfBitPeriod'] <= Expvalue_phase['HalfBitPeriod'][1] else f"{Temresult['Phase'][pkts]['HalfBitPeriod']}|{Expvalue_phase['HalfBitPeriod'][0]}-{Expvalue_phase['HalfBitPeriod'][1]}|Fail"
                        EyeResult['Phase'][pkts]['EyeWidth'] = f"{Temresult['Phase'][pkts]['EyeWidth']}|>={Expvalue_phase['EyeWidth'][0]}|Pass" if Temresult['Phase'][pkts]['EyeWidth'] >= Expvalue_phase['EyeWidth'][0] else f"{Temresult['Phase'][pkts]['EyeWidth']}|>={Expvalue_phase['EyeWidth'][0]}|Fail"
                except Exception as e:
                    pass 
        #Phase result
        resindx = -1
        res = []
        for Pkt in EyeResult['Phase']:
            resindx+=1
            res.append(Pkt+':'+EyeResult['Phase'][Pkt]['Amplitude Diff']+','+EyeResult['Phase'][Pkt]['SNR']+','+EyeResult['Phase'][Pkt]['Fclk']+','+EyeResult['Phase'][Pkt]['HalfBitPeriod']+','+EyeResult['Phase'][Pkt]['EyeWidth'])
            if 'Fail' in res[resindx]: check_res_phase.append("Fail")
            if 'Fail' not in res[resindx]: Npass_Phase+=1
        AllOtherChecks['EyeDigramCheck_Phase'] = ';'.join(res)
        AllOtherChecks['EyeDigramCheck_Phase_res'] = 'Fail' if len(check_res_phase)>0 and len(res)>0 else 'Pass'
        #Magnitude result
        resindx = -1
        res = []
        for Pkt in EyeResult['Magnitude']:
            resindx+=1
            res.append(Pkt+':'+EyeResult['Magnitude'][Pkt]['Amplitude Diff']+','+EyeResult['Magnitude'][Pkt]['SNR']+','+EyeResult['Magnitude'][Pkt]['Fclk']+','+EyeResult['Magnitude'][Pkt]['HalfBitPeriod']+','+EyeResult['Magnitude'][Pkt]['EyeWidth'])
            if 'Fail' in res[resindx]: check_res_mag.append("Fail")
            if 'Fail' not in res[resindx]: Npass_magnitude+=1
        AllOtherChecks['EyeDigramCheck_Magnitude'] = ';'.join(res)
        AllOtherChecks['EyeDigramCheck_Magnitude_res'] = 'Fail' if len(check_res_mag)>0 and len(res)>0 else 'Pass'
        AllOtherChecks['Npass'] = f"Npass_Phase: {Npass_Phase}, Npass_magnitude: {Npass_magnitude}"
        if (Npass_Phase+Npass_magnitude) >= AllOtherChecks['Npass_exp']:AllOtherChecks['Npass_res'] ='Pass'
    def update_TClogs(self,logtype,log):
        dt_object = datetime.fromtimestamp(datetime.now().timestamp())
        self.TClogs.append([str(dt_object),logtype,log])



