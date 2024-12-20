#DB export for analysis & reports
from MainModule import JsonOperations
from datetime import datetime
class ExportforZoho():
    def __init__(self):
        self.conRep = JsonOperations('Results/Consolidated/Consolidated.json')
        self.conRepData = self.conRep.read_file()
        self.ExportMain()

    def ExportMain(self):
        Header = {"UID":[],"SWversion":[],"FWversion":[],"HWversion":[],'BoardNo':[],'DUTname':[],'DUTID':[],'ChapterName':[],'Position':[],'ProjectName':[],'Run':[],'TestID':[],'TestcaseName':[],'TestResult':[]}
        Measures = {'UID':[],'Dscr':[],"Expected":[],'Value':[],'Result':[]}
        for SW in self.conRepData:
                for FW in self.conRepData[SW]:
                        for HW in self.conRepData[SW][FW]:
                                for BD in self.conRepData[SW][FW][HW]:
                                        for DUTN in self.conRepData[SW][FW][HW][BD]:
                                                for DUTID in self.conRepData[SW][FW][HW][BD][DUTN]:
                                                        for ch in self.conRepData[SW][FW][HW][BD][DUTN][DUTID]:
                                                                for pos in self.conRepData[SW][FW][HW][BD][DUTN][DUTID][ch]:
                                                                        for tests in self.conRepData[SW][FW][HW][BD][DUTN][DUTID][ch][pos]:
                                                                                for test in self.conRepData[SW][FW][HW][BD][DUTN][DUTID][ch][pos][tests]:
                                                                                    Header['UID'].append(test['Header']['UID'])
                                                                                    Header['SWversion'].append(SW)
                                                                                    Header['FWversion'].append(FW)
                                                                                    Header['HWversion'].append(HW)
                                                                                    Header['BoardNo'].append(BD)
                                                                                    Header['DUTname'].append(DUTN)
                                                                                    Header['DUTID'].append(DUTID)
                                                                                    Header['ChapterName'].append(ch)
                                                                                    Header['Position'].append(pos)
                                                                                    Header['ProjectName'].append(test['Header']['ProjectName'])
                                                                                    Header['Run'].append(test['Header']['Run'])
                                                                                    Header['TestID'].append(test['Header']['TestcaseID'])
                                                                                    Header['TestcaseName'].append(test['Header']['TestcaseName'])
                                                                                    Header['TestResult'].append(test['Header']['TCresult'])
                                                                                    #Update measures

        print(len(Header))


obj = ExportforZoho()
