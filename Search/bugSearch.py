# -*- coding: UTF-8 -*-
import sys
import time
import os
from dbService import connectDB
from Similarity_CountSim import CountSim
from Predict_Net import prediction
import hashlib
from attr_info import attrListName,attrValueName


def count_predSim(BugFunctionList,FirmFunctionList):
	flst = []
	for  BugItem in BugFunctionList:
		for FirmItem in FirmFunctionList:
			eachSim = CountSim(BugItem,FirmItem) # order is import
			eachSim.countLabel()
			flst.append(eachSim.sim)
	return flst


#generate the form data
def count_formData(predSim):
	featureList =[]
	labelList = []
	try:
		for item2 in predSim:
			featureList.append([item2['sim_' + key] for key in attrListName + attrValueName])
			labelList.append(item2['Label'])
	except:
		for item2 in predSim:
			featureList.append([item2['sim_' + key] for key in attrListName + attrValueName])
		labelList = [0.0] * len(predSim)
	return featureList, labelList


def count_md5(s):
	fmd5 = hashlib.md5(s)
	return fmd5.hexdigest()

def main(thre = 0.5):
	TargetBinaryPath = sys.argv[1]
	BugBinaryPath = sys.argv[2]
	BugName = sys.argv[3]

	idaenginePath = '/home/changqing/IDAPro/idal64'
	BugPlugPath = '/home/changqing/Desktop/Search/BugPlug.py'
	TargetPlugPath = '/home/changqing/Desktop/Search/TargetPlug.py'

	dbName = 'firmware'
	BugCollectionName = 'BugFeature'
	TargetCollectionName = 'TargetFeature'

	BugFlag = count_md5(BugBinaryPath+' '+BugName)
	TargetFlag = count_md5(TargetBinaryPath)

	analyseFlag = BugBinaryPath[-4:]=='.i64' and TargetBinaryPath[-4:]=='.i64'

	if analyseFlag:
		BugId0Path = BugBinaryPath[:-4]+'.id0'
		BugId1Path = BugBinaryPath[:-4]+'.id1'
		BugNamPath = BugBinaryPath[:-4]+'.nam'
		BugTilPath = BugBinaryPath[:-4]+'.til'


		if os.path.exists(BugId0Path):
			os.system("rm %s"%(BugId0Path))
		if os.path.exists(BugId1Path):
			os.system("rm %s"%(BugId1Path))
		if os.path.exists(BugNamPath):
			os.system("rm %s"%(BugNamPath))
		if os.path.exists(BugTilPath):
			os.system("rm %s"%(BugTilPath))

		os.system("%s -A -S'%s %s %s ' %s"%( idaenginePath, BugPlugPath, BugName, BugFlag, BugBinaryPath))

		if os.path.exists(BugId0Path):
			os.system("rm %s"%(BugId0Path))
		if os.path.exists(BugId1Path):
			os.system("rm %s"%(BugId1Path))
		if os.path.exists(BugNamPath):
			os.system("rm %s"%(BugNamPath))
		if os.path.exists(BugTilPath):
			os.system("rm %s"%(BugTilPath))

		TargetId0Path = TargetBinaryPath[:-4]+'.id0'
		TargetId1Path = TargetBinaryPath[:-4]+'.id1'
		TargetNamPath = TargetBinaryPath[:-4]+'.nam'
		TargetTilPath = TargetBinaryPath[:-4]+'.til'

		if os.path.exists(TargetId0Path):
			os.system("rm %s"%(TargetId0Path))

		if os.path.exists(TargetId1Path):
			os.system("rm %s"%(TargetId1Path))

		if os.path.exists(TargetNamPath):
			os.system("rm %s"%(TargetNamPath))

		if os.path.exists(TargetTilPath):
			os.system("rm %s"%(TargetTilPath))

		os.system("%s -A -S'%s %s' %s"%( idaenginePath, TargetPlugPath, TargetFlag,TargetBinaryPath))

		if os.path.exists(TargetId0Path):
			os.system("rm %s"%(TargetId0Path))

		if os.path.exists(TargetId1Path):
			os.system("rm %s"%(TargetId1Path))

		if os.path.exists(TargetNamPath):
			os.system("rm %s"%(TargetNamPath))

		if os.path.exists(TargetTilPath):
			os.system("rm %s"%(TargetTilPath))


		conn = connectDB()
		BugFunctionList = list(conn[dbName][BugCollectionName].find({'BugFlag':BugFlag}))
		TargetFunctionList = list(conn[dbName][TargetCollectionName].find({'TargetFlag':TargetFlag}))

		#print len(BugFunctionList)
		#print len(TargetFunctionList)

		predSimList = []
		probList = []

		if len(BugFunctionList) != 0 and len(TargetFunctionList) != 0:
			predSimList = count_predSim(BugFunctionList, TargetFunctionList)# order is import
			featureList,labelList = count_formData(predSimList)
			probList = prediction(featureList,labelList)


		for i in range(len(probList)):
			if probList[i] >= thre:
				print predSimList[i]['Func_Name_target'],': ',probList[i]

		conn[dbName][BugCollectionName].remove({'BugFlag':BugFlag})
		conn[dbName][TargetCollectionName].remove({'TargetFlag':TargetFlag})

if __name__ == "__main__":
	main()
