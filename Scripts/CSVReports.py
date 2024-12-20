from Scripts.MainModule import JsonOperations
import xlsxwriter
from datetime import datetime
class CSVreport():
    def __init__(self,filters,mode='TPR'):
        self.mode = mode
        self.conRep = JsonOperations(r'Results\Consolidated\Consolidated.json')
        self.conRepData = self.conRep.read_file()
        self.fltr =filters
        self.JMOI = JsonOperations('json/MOIJson.json')
        self.JMOIData = self.JMOI.read_file()
        self.Gnameli = []
        # self.apptimings = ["twake","tstart","tsilent","tresponse","tintervalXCE-XCE","treceviedPLA-PLA"]
        self.apptimings = ["twake","tstart","tresponse"]
        self.PrepareReportData()
        #
        now = datetime.now()
        timestamp = now.strftime("%d%m%Y_%H%M%S")
        self.Reprot_loc = './Results/MPP Excel Results/'
        self.Wb = xlsxwriter.Workbook(self.Reprot_loc+'_'+str(self.fltr['SW'][0])+'_'+str(self.fltr['FW'][0])+'_CTS_Validation_Report'+timestamp+'.xlsx')
        self.Ws = self.Wb.add_worksheet("Details")
        #Formats 
        self.Heading1 = self.Wb.add_format({'bold': True, 'font_color': '#FFFFFF','bg_color':'#833C0C','center_across':True,'border':True})
        self.Heading2 = self.Wb.add_format({'bold': True, 'font_color': '#000000','bg_color':'#F4B084','center_across':True,'border':True})
        self.Heading3 = self.Wb.add_format({'bold': True, 'font_color': '#000000','bg_color':'#F8CBAD','center_across':True,'border':True})
        self.Pass_frmt = self.Wb.add_format({'font_color': '#000000','bg_color':'#00B050','border':True})
        self.Fail_frmt = self.Wb.add_format({'font_color': '#000000','bg_color':'#FF0000','border':True})
        self.INCL_frmt = self.Wb.add_format({'font_color': '#000000','bg_color':'#F79646','border':True})
        self.NA_frmt = self.Wb.add_format({'font_color': '#000000','bg_color':'#BFBFBF','border':True,'center_across':True})
        self.exp_frmt =self.Wb.add_format({'font_color': '#000000','bg_color':'#F79646','border':True,'center_across':True})
        self.exportReport()
        self.Ws.autofit()
        self.Wb.close()
    def PrepareReportData(self):
        for SW in self.conRepData:
            if SW in self.fltr['SW']:
                for FW in self.conRepData[SW]:
                    if FW in self.fltr['FW']:
                        for HW in self.conRepData[SW][FW]:
                            if HW in self.fltr['HW']:
                                for BD in self.conRepData[SW][FW][HW]:
                                    if BD in self.fltr['Board']:
                                        for DUTN in self.conRepData[SW][FW][HW][BD]:
                                            if DUTN in self.fltr['DUTname']:
                                                for DUTID in self.conRepData[SW][FW][HW][BD][DUTN]:
                                                    if DUTID in self.fltr['DUTID']:
                                                        for ch in self.conRepData[SW][FW][HW][BD][DUTN][DUTID]:
                                                            if ch in self.fltr['Chap']:
                                                                for pos in self.conRepData[SW][FW][HW][BD][DUTN][DUTID][ch]:
                                                                    if pos in self.fltr['Coil']:
                                                                        for tests in self.conRepData[SW][FW][HW][BD][DUTN][DUTID][ch][pos]:
                                                                            if tests in self.fltr['Tests']:
                                                                                for test in self.conRepData[SW][FW][HW][BD][DUTN][DUTID][ch][pos][tests]:
                                                                                    test["Header"]['SW'] = SW
                                                                                    test["Header"]['FW'] = FW
                                                                                    test["Header"]['HW'] = HW
                                                                                    test["Header"]['BD'] = BD
                                                                                    test["Header"]['DUTN'] = DUTN
                                                                                    test["Header"]['DUTID'] = DUTID
                                                                                    test["Header"]['ch'] = ch
                                                                                    test["Header"]['pos'] = pos
                                                                                    self.Gnameli.append(test)
        # print(self.Gnameli)
    def exportReport(self):
        Header1 = ["Sno","SWversion","FWversion","HWverison","BoardNo","DUT Name","DUT ID","ChapterName","Position","ProjectName","Run",
                   "TestcaseName","TestResult"]
        TimeHeader=["Flow","Timing Desc","Timing Exp.","Timing Val.","Timing Result"]
        MesHeader=["Flow","Measure Desc","Measure Exp.","Measure Val.","Measure Result"]
        OthrHeader=["Flow","OtherCheck Desc","OtherCheck Exp.","OtherCheck Val.","OtherCheck Result"]
        row =0
        col =0
        #fill Headers
        row+=1
        for i in Header1:
            self.Ws.write(row,col, i,self.Heading3)
            col+=1
        self.Ws.merge_range(row-1,0,row-1,col-1,"Header",self.Heading1)
        #Timings
        if self.fltr['Timings']==True:
            for i in TimeHeader:
                self.Ws.write(row,col, i,self.Heading3)
                col+=1
            self.Ws.merge_range(row-1,col-5,row-1,col-1,"Timings",self.Heading1)
        #Measures
        if self.fltr['Measures']==True:
            for i in MesHeader:
                self.Ws.write(row,col, i,self.Heading3)
                col+=1
            self.Ws.merge_range(row-1,col-5,row-1,col-1,"Measures",self.Heading1)
        #others
        if self.fltr['Others']==True:
            for i in OthrHeader:
                self.Ws.write(row,col, i,self.Heading3)
                col+=1
            self.Ws.merge_range(row-1,col-5,row-1,col-1,"Otherchecks",self.Heading1)
        row+=1
        #Values
        sno=1
        row=2
        if len(self.Gnameli)>0:
            for ts in self.Gnameli:
                testid = self.GetTestIDByName(ts['Header']['TestcaseName'])
                Json_TC = self.JMOIData[self.mode][testid] 
                col =12
                #Update Timings
                timrow = row
                if self.fltr['Timings']==True:
                    # for flw in self.apptimings:
                        # flwrow = timrow
                    if len(ts['Timings'])>0:
                        for tm in self.apptimings:
                            # self.Ws.write(timrow,col+1,flw)
                            self.Ws.write(timrow,col+2,tm)
                            self.Ws.write(timrow,col+3,ts['Timings'][tm+'_exp'])
                            self.Ws.write(timrow,col+4,ts['Timings'][tm])
                            self.UpdateResults(timrow,col+5,ts['Timings'][tm+'_res'])
                            timrow+=1
                            # print(row,col,timrow)
                    col=col+5
                #update Measures
                mesrow=row
                if self.fltr['Measures']==True:
                    if len(Json_TC['App_Measures'])>0:
                        for mes in Json_TC['App_Measures']:
                            self.Ws.write(mesrow,col+2,mes)
                            self.Ws.write(mesrow,col+3,ts['Measures'][mes+'_exp'])
                            if ts['Measures'][mes] is not None:
                                self.Ws.write(mesrow,col+4,ts['Measures'][mes])
                            else:
                                self.Ws.write(mesrow,col+4,'None')
                            self.UpdateResults(mesrow,col+5,ts['Measures'][mes+'_res'])
                            mesrow+=1
                    col=col+5
                #Update Other checks
                otrow=row
                if self.fltr['Others']==True:
                    # if all(rs in Json_TC['other_checks_details'] for rs in ['1','2']):
                    if len(Json_TC['other_checks_details'])>0:
                        for othck in Json_TC['other_checks_details']:
                            # self.Ws.write(otrow,col+1,flw)
                            self.Ws.write(otrow,col+2,othck)
                            self.Ws.write(otrow,col+3,ts['OtherChecks'][othck+'_exp'])
                            self.Ws.write(otrow,col+4,ts['OtherChecks'][othck])
                            self.UpdateResults(otrow,col+5,ts['OtherChecks'][othck+'_res'])
                            otrow+=1
                ###Update Header
                rowmax=max([mesrow,otrow,timrow])
                hcol=0
                if abs(rowmax-row)<=1:
                    self.Ws.write(row,hcol,sno)
                    hcol+=1
                    self.Ws.write(row,hcol,ts['Header']['SW'])
                    hcol+=1
                    self.Ws.write(row,hcol,ts['Header']['FW'])
                    hcol+=1
                    self.Ws.write(row,hcol,ts['Header']['HW'])
                    hcol+=1
                    self.Ws.write(row,hcol,ts['Header']['BD'])
                    hcol+=1
                    self.Ws.write(row,hcol,ts['Header']['DUTN'])
                    hcol+=1
                    self.Ws.write(row,hcol,ts['Header']['DUTID'])
                    hcol+=1
                    self.Ws.write(row,hcol,ts['Header']['ch'])
                    hcol+=1
                    self.Ws.write(row,hcol,ts['Header']['pos'])
                    hcol+=1
                    self.Ws.write(row,hcol,ts['Header']['ProjectName'])
                    hcol+=1
                    self.Ws.write(row,hcol,ts['Header']['Run'])
                    hcol+=1
                    self.Ws.write(row,hcol,ts['Header']['TestcaseName'])
                    hcol+=1
                    self.UpdateResults(row,hcol,ts['Header']['TCresult'])
                    sno+=1
                    row+=1
                else:
                    self.Ws.merge_range(row,hcol,rowmax-1,hcol,sno)
                    hcol+=1
                    self.Ws.merge_range(row,hcol,rowmax-1,hcol,ts['Header']['SW'])
                    hcol+=1
                    self.Ws.merge_range(row,hcol,rowmax-1,hcol,ts['Header']['FW'])
                    hcol+=1
                    self.Ws.merge_range(row,hcol,rowmax-1,hcol,ts['Header']['HW'])
                    hcol+=1
                    self.Ws.merge_range(row,hcol,rowmax-1,hcol,ts['Header']['BD'])
                    hcol+=1
                    self.Ws.merge_range(row,hcol,rowmax-1,hcol,ts['Header']['DUTN'])
                    hcol+=1
                    self.Ws.merge_range(row,hcol,rowmax-1,hcol,ts['Header']['DUTID'])
                    hcol+=1
                    self.Ws.merge_range(row,hcol,rowmax-1,hcol,ts['Header']['ch'])
                    hcol+=1
                    self.Ws.merge_range(row,hcol,rowmax-1,hcol,ts['Header']['pos'])
                    hcol+=1
                    self.Ws.merge_range(row,hcol,rowmax-1,hcol,ts['Header']['ProjectName'])
                    hcol+=1
                    self.Ws.merge_range(row,hcol,rowmax-1,hcol,ts['Header']['Run'])
                    hcol+=1
                    self.Ws.merge_range(row,hcol,rowmax-1,hcol,ts['Header']['TestcaseName'])
                    hcol+=1
                    self.UpdateResults_Range(row,hcol,rowmax-1,hcol,ts['Header']['TCresult'])
                    sno+=1
                    row=rowmax
                
    def GetTestIDByName(self,Testname):
        for ts in self.JMOIData[self.mode]:
            # if '_TD_' in ts:
            if self.JMOIData[self.mode][ts]['Testcase_Name'] == Testname:
                return ts
    def UpdateResults(self,row,col,value):
        if value in ['Pass','PASS']:
            self.Ws.write(row,col,value,self.Pass_frmt)
        elif value in ['Fail','FAIL']:
            self.Ws.write(row,col,value,self.Fail_frmt)
        elif value in ['Inconclusive','INCONCLUSIVE','NA']:
            self.Ws.write(row,col,value,self.INCL_frmt)    
    def UpdateResults_Range(self,srow,scol,erow,ecol,value):
        if value in ['Pass','PASS']:
            self.Ws.merge_range(srow,scol,erow,ecol,value,self.Pass_frmt)
        elif value in ['Fail','FAIL']:
            self.Ws.merge_range(srow,scol,erow,ecol,value,self.Fail_frmt)
        elif value in ['Inconclusive','INCONCLUSIVE','NA']:
            self.Ws.merge_range(srow,scol,erow,ecol,value,self.INCL_frmt)
    


# fltr = {'SW': ['1.2.2.15'], 'FW': ['7.0.0.9'], 'HW': ['E-2.6'], 'Board': ['GRL-C3-2019012'], 'DUTname': ['_'], 'DUTID': [''], 'Chap': ['Disconnected Load tests'], 'Coil': ['TPR_1A', 'TPR_1B', 'TPR_1C', 'TPR_1D'], 'Tests': ['TD_6_1_1_3a', 'TD_6_1_1_3b', 'TD_6_1_1_3c', 'TD_6_1_1_3d'], 'Timings': True, 'Measures': True, 'Others': True}
# CSVreport(fltr)

# CSVreport.ExportCTSChecks()