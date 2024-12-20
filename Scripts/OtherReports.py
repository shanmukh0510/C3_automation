
from Scripts.MainModule import JsonOperations
import xlsxwriter
from datetime import datetime
class XLreport():
    def __init__(self,mode='TPT',name="Test"):
        self.Mode = mode
        self.JMOI = JsonOperations('json/MOIJson.json')
        self.JMOIData = self.JMOI.read_file()
        #Create File
        now = datetime.now()
        timestamp = now.strftime("%d%m%Y_%H%M%S")
        self.Reprot_loc = './Results/MPP Excel Results/'
        self.Wb = xlsxwriter.Workbook(self.Reprot_loc+'_'+name+'_'+timestamp+'.xlsx')
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
        if name == 'CTS Checks':
            self.ExportCTSChecks()
        self.Ws.autofit()
        self.Wb.close()
    #Export CTS checks
    def ExportCTSChecks(self):
        ExportRes = []
        apptimings = ['twake','tsilent','tstart','tresponse']
        for TC in self.JMOIData[self.Mode]:
            # print(TC)
            if 'Status' in self.JMOIData[self.Mode][TC]:
                if self.JMOIData[self.Mode][TC]['Status']==True:
                    TCdata = self.JMOIData[self.Mode][TC]
                    res = {}
                    #Header
                    res['TC_id']=TCdata['TC_id']
                    res['Testcase_Name']=TCdata['Testcase_Name']
                    res['TC_Chapter'] = TCdata['TC_Chapter']
                    res['Coils'] = TCdata['Coils']
                    res['PowerProfile'] = ','.join(TCdata['PowerProfile'])
                    #Timings
                    res['Timings']={}
                    for times in apptimings:
                        if times in TCdata:
                            res['Timings'][times]=f"{TCdata[times][0]-TCdata[times][1]}-{TCdata[times][0]+TCdata[times][1]}"
                        else:
                            res['Timings'][times]=f"{self.JMOIData['default_Values'][times][0]-self.JMOIData['default_Values'][times][1]}-{self.JMOIData['default_Values'][times][0]+self.JMOIData['default_Values'][times][1]}"
                    #Mesures
                    res['Measures']={}
                    for mes in TCdata['App_Measures']:
                        if 'expected' in TCdata['App_Measures'][mes]:
                            if type(TCdata['App_Measures'][mes]['expected'])==list:
                                if len(TCdata['App_Measures'][mes]['expected'])==2:
                                    res['Measures'][mes]=f"Expected: {'-'.join(map(str,TCdata['App_Measures'][mes]['expected']))}"
                                if len(TCdata['App_Measures'][mes]['expected'])==1:
                                    comp = ""
                                    if TCdata['App_Measures'][mes]["comp"]=="LT":comp="<"
                                    if TCdata['App_Measures'][mes]["comp"]=="GT":comp=">"
                                    if TCdata['App_Measures'][mes]["comp"]=="EQL":comp="=="
                                    if TCdata['App_Measures'][mes]["comp"]=="LTEQL":comp="<="
                                    if TCdata['App_Measures'][mes]["comp"]=="GTEQL":comp=">="
                                    res['Measures'][mes] =f"Expected: {comp}{TCdata['App_Measures'][mes]['expected'][0]}"
                                #if 'packet' in TCdata['App_Measures'][mes]:remarks.append(f"Consider from/on {TCdata['App_Measures'][mes]['packet']} packet.")
                                if 'refPrevious' in  TCdata['App_Measures'][mes]:res['Measures'][mes] = f"{res['Measures'][mes]}; Check condition on previous flow"
                                # if 'TwinSize' in TCdata['App_Measures'][mes]:remarks.append(f"Consider the Twindow time for the measurement is {}")
                    #Otherchecks
                    res['Others']={}
                    for otr in TCdata['other_checks_details']:
                        if otr=='PacketCheck':
                            allpkts =[]
                            for pkt in TCdata['other_checks_details'][otr]:
                                pktlist =[]
                                if pkt['packet'][1] is None:
                                    pktlist.append("Packet : "+pkt['packet'][0])
                                else:pktlist.append("Packet : "+pkt['packet'][0]+"_"+pkt['packet'][1])
                                if 'phase' in pkt:pktlist.append(f"Phase:{pkt['phase']}")
                                if 'Pkt_count' in pkt:pktlist.append(f"Pkt_count:{pkt['Pkt_count']}")
                                allpkts.append(','.join(pktlist))
                            res['Others'][otr]=';'.join(allpkts)
                        elif otr == "SRQResponse":
                            res['Others'][otr] = f"Packet: {TCdata['other_checks_details'][otr]['value']}, Response:{TCdata['other_checks_details'][otr]['expected'][0]}"
                        elif otr == "SRQReserved":
                            res['Others'][otr] = f"Packet: {TCdata['other_checks_details'][otr]['value']}, Reserved Bit:{TCdata['other_checks_details'][otr]['expected'][0]}"
                        elif otr == "PacketLimit":
                            res['Others'][otr] = f"Packet: {','.join(TCdata['other_checks_details'][otr]['expected'])}"
                            if len(TCdata['other_checks_details'][otr]['LimitPkt']) ==1:
                                res['Others'][otr] = f"{res['Others'][otr]}, Consider from  {TCdata['other_checks_details'][otr]['LimitPkt'][0][0]}"
                            else: res['Others'][otr] = f"{res['Others'][otr]}, Consider from  {TCdata['other_checks_details'][otr]['LimitPkt'][0][0]} to {TCdata['other_checks_details'][otr]['LimitPkt'][1][0]}"
                        else:
                            if 'expected' in TCdata['other_checks_details'][otr]:
                                if type(TCdata['other_checks_details'][otr]['expected'])==list:
                                    if len(TCdata['other_checks_details'][otr]['expected'])==2:
                                        res['Others'][otr]='-'.join(map(str,TCdata['other_checks_details'][otr]['expected']))
                                    if len(TCdata['other_checks_details'][otr]['expected'])==1:
                                        comp = ""
                                        if TCdata['other_checks_details'][otr]["comp"]=="LT":comp="<"
                                        if TCdata['other_checks_details'][otr]["comp"]=="GT":comp=">"
                                        if TCdata['other_checks_details'][otr]["comp"]=="EQL":comp="=="
                                        if TCdata['other_checks_details'][otr]["comp"]=="LTEQL":comp="<="
                                        if TCdata['other_checks_details'][otr]["comp"]=="GTEQL":comp=">="
                                        res['Others'][otr] =f"{comp}{TCdata['other_checks_details'][otr]['expected'][0]}"
                                else:
                                    res['Others'][otr] = TCdata['other_checks_details'][otr]['expected']
                                if 'refPrevious' in  TCdata['other_checks_details'][otr]:f"{res['Others'][otr]};Check condition on previous flow"
                    #Testcase Pass/Fail checks.
                    res['PassFail'] = ','.join(TCdata['Result_checks'])
                    #Testcase Inconclusive checks
                    ExportRes.append(res)
        if len(ExportRes) >0:
            Header1 = ["Sno","TestID","TestName","Chapter","Power Profile","Coil"]
            Header2 = ["Timing Checks","Measure Checks","Other Checks"]
            Header3 = ["Description","Expected"]
            row =0
            col = 0
            #Fill Headers1
            row+=1
            for i in Header1:
                self.Ws.write(row,col,i,self.Heading3)
                col+=1
            self.Ws.merge_range(row-1,0,row-1,col-1,"Header",self.Heading1) 
            #Fill header2
            for i in Header2:
                for j in Header3:
                    self.Ws.write(row,col,j,self.Heading3)
                    col+=1
                self.Ws.merge_range(row-1,col-2,row-1,col-1,i,self.Heading1)
            #fill Values
            Sno =1
            row=2
            col=0
            for ts in ExportRes:
                self.Ws.write(row,col,Sno)
                self.Ws.write(row,col+1,ts['TC_id'])
                self.Ws.write(row,col+2,ts['Testcase_Name'])
                self.Ws.write(row,col+3,ts['TC_Chapter'])
                self.Ws.write(row,col+4,ts['PowerProfile'])
                self.Ws.write(row,col+5,ts['Coils'])
                #Timing Checks
                if len(ts['Timings'])>0:
                    trow = row
                    for Timings in ts['Timings']:
                        self.Ws.write(trow,col+6,Timings)
                        self.Ws.write(trow,col+7,ts['Timings'][Timings])
                        trow+=1
                    # row = trow-1
                #Measure checks
                if len(ts['Measures'])>0:
                    mrow = row
                    for mes in ts['Measures']:
                        self.Ws.write(mrow,col+8,mes)
                        self.Ws.write(mrow,col+9,ts['Measures'][mes])
                        mrow+=1
                    # row = mrow-1
                #Others checks
                if len(ts['Others'])>0:
                    orow = row
                    for otr in ts['Others']:
                        self.Ws.write(orow,col+10,otr)
                        self.Ws.write(orow,col+11,ts['Others'][otr])
                        orow+=1
                    # row = orow-1
                Sno+=1
                row =  max(trow,mrow,orow)

# Obj = XLreport(name="CTS Checks")
# Obj.ExportCTSChecks()