__author__ = 'qingqing'
from Similarty_Function import *

class CountSim():

    attrName = ['Func_Name', 'Func_Addr']
    attrListName = ['Func_PathList', 'Func_InDegreeList', 'Func_OutDegreeList', 'Func_AllDegreeList']
    attrValueName =['Func_AvePath', 'Func_AveInDegree', 'Func_AveOutDegree', 'Func_AveAllDegree', 'Func_MaxInDegree', \
                    'Func_MaxOutDegree', 'Func_MaxAllDegree', 'Func_Node', 'Func_Edge', 'Func_strNum', 'Func_FrameSize', \
                    'Func_AllEtp', 'Func_Entropy', 'Func_CfgEntropy', 'Func_E', 'Func_Cc', 'Func_Jmp', 'Func_Jmpp', \
                    'Func_CodeSize', 'Func_InstSize', 'Func_Density', 'Func_Diameter', 'Func_CallFromNums', \
                    'Func_CallFromTimes', 'Func_CallToNums', 'Func_CallToTimes']
    attrSetName = ['Func_StrList']


    def __init__(self,d1,d2):
        self.sim = {}
        self.countSimAttr(d1,d2)


    def countSimAttr(self,d1,d2):
        for i in self.attrName:
            self.sim[i+'_bug'] = d1[i]  #bug and target
            self.sim[i+'_target'] = d2[i]
        for i in self.attrValueName:
            self.sim['sim_'+i] = numSim(d1[i],d2[i])
        for i in self.attrListName:
            self.sim['sim_'+i] = longSim(d1[i],d2[i])
        for i in self.attrSetName:
            self.sim['sim_'+i] = jaccardSim(d1[i],d2[i])


    def countLabel(self):
        if self.sim['Func_Name_bug'] == self.sim['Func_Name_target']:
            self.label = 1
        else: self.label = 0
        self.sim['Label'] = self.label






