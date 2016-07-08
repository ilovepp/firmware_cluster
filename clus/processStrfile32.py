# -*- coding: utf-8 -*-
import networkx as nx
import crcmod
import random
import time
import pymongo
from bson.objectid import ObjectId
import networkx as nx
#import matplotlib.pyplot as plt
import itertools
import math
import binascii
import csv
import six.moves.cPickle as pickle
from collections import Counter

# 计算字符串的CRC校验码
def countCRC32(instr):
	return binascii.crc32(instr)


def save_data(prob,name):
	fid = open(name,'wb')
	pickle.dump(prob,fid)
	fid.close()

def get_data(name):
	f = open(name,'rb')
	result = pickle.load(f)
	f.close()
	return result




def createHashDic(hashNum = 200):

	minA = 0
	maxA = 100
	minB = 0
	maxB = 2**32-1

	aList, bList= [], []
	for i in range(hashNum):
		aList.append(random.randint(minA, maxA))
		bList.append(random.randint(minB, maxB))
	return aList,bList


def loadData(addr):
	crcList = []
	with open(addr) as ifile:
		for line in ifile:
			crcList.append(int(line[:-1]))
	return crcList


def crc2Grid(crcList,aList,bList,p,hashNum,d):
	GridDic = {}
	IndexList = []
	for i in range(hashNum):
		IndexList.append(min([int((aList[i] * crcItem + bList[i]) % p) for crcItem in crcList]))
		#IndexList save the min of the all crc-map for crcList of a binary,and the range is 200
	for j in range(hashNum/d):
		str5 = ' '.join([str(t) for t in IndexList[d*j:d*(j+1)]])
		GridDic['Gridx'+str(j)] = countCRC32(str5)
		# for each d index, we turn them to a crc32 code with GridDic.
		# Gridx0-Gridx39.
	return IndexList,GridDic


def createGridFileDic(aList,bList,p,hashNum,d):
	count = 0
	GridFileDic = {}
	conn = pymongo.MongoClient('localhost',27017)
	filesList = list(conn['test']['files'].find()) #518441
	for fileItem in filesList:
		addr = rootaddr + '//' + fileItem['StrFileName'] #the path of each binary
		try:
			crcList = loadData(addr)
			if len(crcList) != 0:
				IndexList,GridDic = crc2Grid(crcList,aList,bList,p,hashNum,d)
				GridFileDic[str(fileItem['_id'])] = GridDic
				conn['test']['files'].update({'_id':fileItem['_id']},{'$set':GridDic}) # save the 40 into db
				print count,'   ',fileItem['StrFileName']
				count += 1
		except:
			errorList.append(fileItem['StrFileName']) # cleared
	return GridFileDic # a dic for the key is id and the value is 40


#def countGroup(GridFileDic,hashNum,d):
def countGroup(hashNum,d):
	conn = pymongo.MongoClient('localhost',27017)
	if 1: # rebuild GridFileDic
		GridFileList = list(conn.test.files.find())
		GridFileDic = {}
		for item in GridFileList:
			itemDic= {}
			try:# protect the null
				for i in range(hashNum/d):
					itemDic['Gridx'+str(i)] = item['Gridx'+str(i)]
			except:
				pass
			if len(itemDic.keys())!=0:
				GridFileDic[str(item['_id'])] = itemDic
	print len(GridFileDic.keys())
	writeToFile(str(len((GridFileDic.keys()))))

	nodeList = GridFileDic.keys() #str(id)
	edgeListAll = []

	conn.test.result.remove()
	flst = []
	for i in range(hashNum/d): #for each Gridx 40
		time0 = time.time()
		print i
		writeToFile(str(i))
		GridIValueSet = set([item['Gridx'+str(i)] for item in GridFileDic.values()])
		writeToFile("the number of value for each bucket: "+str(len(GridIValueSet)))
		for valueItem in GridIValueSet:
			ClassItem = [item for item in GridFileDic.keys() if GridFileDic[item]['Gridx'+str(i)] == valueItem]
			writeToFile("the number of a bucket: "+str(len(ClassItem)))
			flst.append({'GridId':i, 'GridValue':valueItem, 'ClassItem':ClassItem})
			conn.test.result.insert_one({'GridId':i, 'GridValue':valueItem, 'ClassItem':ClassItem})
			edgeListAll.append(ClassItem)
		time1 = time.time()
		print time1-time0
		writeToFile(str(time1-time0))

	#conn.test.result.insert(flst) # maybe cannot insert_all, we need the insert_one

	return nodeList,edgeListAll


#def countGroup(GridFileDic,hashNum,d):
def countGroup2(hashNum,d):
	conn = pymongo.MongoClient('localhost',27017)
	time0 = time.time()
	if 1: # rebuild GridFileDic
		GridFileList = list(conn.test.files.find())
		GridFileDic = {}
		for item in GridFileList:
			itemDic= {}
			try:# protect the null
				for i in range(hashNum/d):
					itemDic['Gridx'+str(i)] = item['Gridx'+str(i)]
			except:
				pass
			if len(itemDic.keys())!=0:
				GridFileDic[str(item['_id'])] = itemDic
	time1 = time.time()
	print len(GridFileDic.keys())
	writeToFile("The number of files: "+str(len((GridFileDic.keys()))))
	writeToFile("Get all data from db: "+str(time1-time0))

	nodeList = GridFileDic.keys() #str(id)
	edgeListAll = []

	conn.test.result.remove()
	flst = []
	for i in range(hashNum/d): #for each Gridx 40
		time0 = time.time()
		print i
		writeToFile("solve the Gridx: "+str(i))
		GridIValueSet = set([item['Gridx'+str(i)] for item in GridFileDic.values()])
		writeToFile("the number of value for each bucket: "+str(len(GridIValueSet)))

		mapDic = {}
		for item in GridFileDic.keys():
			value = GridFileDic[item]['Gridx' + str(i)]
			try:
				mapDic[value].append(item)
			except:
				mapDic[value] = []
				mapDic[value].append(item)

		writeToFile("the solve time: "+str(len(mapDic)))
		writeToFile(" ")

		ClassItem = []
		for valueItem in mapDic.keys():
			ClassItem = mapDic[valueItem]
			conn.test.result.insert_one({'GridId': i, 'GridValue': valueItem, 'ClassItem': ClassItem})
			edgeListAll.append(ClassItem)

		time1 = time.time()
		print time1-time0
		writeToFile("The time of countGroup: "+str(time1-time0))

	#conn.test.result.insert(flst) # maybe cannot insert_all, we need the insert_one

	return nodeList,edgeListAll



def countConnectGraph(nodeList,edgeListAll):
	g= nx.Graph()
	g.add_nodes_from(nodeList)
	for item in edgeListAll:
		g.add_edges_from(itertools.combinations(item,2))
	nx.connected_components(g)

	result = []
	for item in nx.connected_components(g):
		result.append(list(item))

	#writeToFile()
	conn = pymongo.MongoClient('localhost', 27017)

	idmapstr = {}
	for Index in range(len(result)):
		for j in result[Index]:
			conn.test.files.update({'_id':ObjectId(j)},{'$set':{'classx':Index}})
			idmapstr[j] = Index

	infoResult = list(conn.test.result.find())
	for i in range(len(infoResult)):
		conn.test.result.update({'_id':infoResult[i]['_id']},{'$set':{'classx':idmapstr[infoResult[i]['ClassItem'][0]]}})


def findPre(x): #find the parent of x
	r = x
	while(pre[r] != r):
		r = pre[r]

	#路径压缩
	i = x
	while(pre[i]!=r):
		j = pre[i]
		pre[i] = r
		i = j
	return r

def mix(x,y):
	fx = findPre(x)
	fy = findPre(y)
	if(fx!=fy):
		pre[fx] = fy


def preCompress(pre):
	for x in pre.keys():
		r = x
		while(pre[r] != r):
			r = pre[r]

		i = x
		while(pre[i]!=r):
			j = pre[i]
			pre[i] = r
			i = j


def countConnectGraph2():

	conn = pymongo.MongoClient('localhost', 27017)

	time0 = time.time()
	nodeList = [str(item['_id']) for item in list(conn.test.files.find({},{'_id':1}))]
	infoResult = list(conn.test.result.find({}, {'_id': 1,'ClassItem':1}))
	edgeListAll = [item['ClassItem'] for item in infoResult if len(item['ClassItem'])>1]
	time1 = time.time()

	writeToFile('The time of saving the node and edge from db: '+str(time1-time0))
	writeToFile('The number of node: '+str(len(nodeList)))
	writeToFile('The number of edgeList>1: '+str(len(edgeListAll)))



	# time2 = time.time()
	# g= nx.Graph()
	# g.add_nodes_from(nodeList)
	# for item in edgeListAll:
	# 	g.add_edges_from(itertools.combinations(item,2))
	# nx.connected_components(g)
	# time3 = time.time()
	# writeToFile(str(time3-time2))
	#
	# time4 = time.time()
	# result = []
	# for item in nx.connected_components(g):
	# 	result.append(list(item))
	# time5 = time.time()
	# writeToFile(str(time5 - time4))

	# time6 = time.time()
	# idmapstr = {}
	# for Index in range(len(result)):
	# 	for j in result[Index]:
	# 		conn.test.files.update({'_id':ObjectId(j)},{'$set':{'classx':Index}})
	# 		idmapstr[j] = Index
	#
	#
	# for i in range(len(infoResult)):
	# 	conn.test.result.update({'_id':infoResult[i]['_id']},{'$set':{'classx':idmapstr[infoResult[i]['ClassItem'][0]]}})
	# time7 = time.time()
	# writeToFile('save to the db: '+str(time7 - time6))


	time2 = time.time()
	for item in nodeList:
		pre[item] = item

	count = 1
	time11 = time.time()
	for edgeList in edgeListAll:
		if (count%10000 == 0):
			time22 = time.time()
			writeToFile('The No.x edgeList is soleved: '+str(count)+' '+str(time22-time11))
			time11 = time.time()
		count+= 1
		edgePairList= itertools.combinations(edgeList,2)
		for edgeItem in edgePairList:
			mix(edgeItem[0],edgeItem[1])
	time3 = time.time()
	writeToFile('The time of change the pre dic: '+str(time3-time2))


	time4 = time.time()
	preCompress(pre)
	time5 = time.time()
	writeToFile('The time of compress the pre dic: '+str(time5-time4))


	classStrNameSet = set(pre.values())
	writeToFile('The num of class: '+str(len(classStrNameSet)))
	strMapClass = {}
	classID = 1

	for classStrNameItem in classStrNameSet:
		strMapClass[classStrNameItem] = classID
		classID += 1

	# save the pre and strMapClass
	time66=time.time()
	save_data(pre,'pre.data')
	save_data(strMapClass,'strMapClass.data')
	time77 = time.time()
	writeToFile("OK,saved! "+ str(time77-time66))


	#get the data of pre and strMapClass
	# time33 = time.time()
	# pre = get_data('pre.data')
	# strMapClass = get_data('strMapClass.data')
	# infoResult = list(conn.test.result.find({}, {'_id': 1, 'ClassItem': 1}))
	# time44 = time.time()
	# writeToFile("OK,get the data! "+ str(time44-time33))

	time7 = time.time()

	for strIDItem in pre.keys():
		conn.test.files.update({'_id':ObjectId(strIDItem)},{'$set':{'classx':strMapClass[pre[strIDItem]]}})

	time8 = time.time()

	writeToFile('save to the files db: '+str(time8-time7))



	time9 = time.time()

	for i in range(len(infoResult)):
		conn.test.result.update({'_id':infoResult[i]['_id']},{'$set':{'classx':strMapClass[pre[infoResult[i]['ClassItem'][0]]]}})

	time10 = time.time()

	writeToFile('save to the result db: '+str(time10 - time9))



def findClass():
	conn = pymongo.MongoClient('localhost',27017)
	info = list(conn.test.files.find({'classx':{'$exists':True}}))
	classSet = set([item['classx'] for item in info])

	count = 0
	for i in range(max(classSet)):
		myList = [item['FileName'] for item in info if item['classx'] == i]
		mySet = set(myList)

		if len(mySet) > 1:
			print
			print 'ID: ',count
			print 'classID: ',i
			print len(mySet),'/',len(myList)
			print mySet
			print myList
			count += 1

def writeToFile(s):
	f= open('out3.txt','a')
	f.write(s+'\n')
	f.close()

def writeToCsv(a):
	with open('result.csv','a+') as file:
		file.write('%d,%d,%d,%s,%s,%d,%d\n'%(a[0],a[1],a[2],a[3],str(a[4]),a[5],a[6]))
	file.close()



def maxf(a):
	count = Counter(a)
	return count.most_common(1)


def countNumInClass():
	time1= time.time()
	conn = pymongo.MongoClient('localhost',27017)
	info = list(conn.test.files.find({'classx': {'$exists': True}},{'_id':1,'classx':1,'FileName':1,'Manufacturer':1,'FileMd5':1}))
	time2 = time.time()
	writeToFile("get the data from db: "+str(time2-time1))


	time3 = time.time()
	classSet = set([item['classx'] for item in info])
	print len(classSet)
	numDic ={}
	for classItem in classSet:
		numDic[classItem] = {}
		numDic[classItem]['FileNum'] = 0

		numDic[classItem]['FileNameList'] = []
		numDic[classItem]['FileNameSet'] = []
		numDic[classItem]['FileNameNum'] = 0
		numDic[classItem]['FileNameMax'] = []

		numDic[classItem]['FacturerNameList'] = []
		numDic[classItem]['FacturerNameSet'] = []
		numDic[classItem]['FileNameNum'] = 0

		numDic[classItem]['FileMd5List'] = []
		numDic[classItem]['FileMd5Set'] = []
		numDic[classItem]['FileMd5Num'] = 0


	for Item in info:
		classItem = Item['classx']
		numDic[classItem]['FileNum'] += 1
		numDic[classItem]['FileNameList'].append(Item['FileName'])
		numDic[classItem]['FacturerNameList'].append(Item['Manufacturer'])
		numDic[classItem]['FileMd5List'].append(Item['FileMd5'])

	time4 = time.time()
	writeToFile("first solve the dic: " + str(time4 - time3))

	time5 = time.time()
	for Item in numDic.keys():
		numDic[Item]['FileNameSet'] = list(set(numDic[Item]['FileNameList']))
		numDic[Item]['FileNameNum'] = len(numDic[Item]['FileNameSet'])
		numDic[Item]['FileNameMax'] = maxf(numDic[Item]['FileNameList'])

		numDic[Item]['FacturerNameSet'] = list(set(numDic[Item]['FacturerNameList']))
		numDic[Item]['FacturerNameNum'] = len(numDic[Item]['FacturerNameSet'])

		numDic[Item]['FileMd5Set'] = list(set(numDic[Item]['FileMd5List']))
		numDic[Item]['FileMd5Num'] = len(numDic[Item]['FileMd5Set'])

		resultList = [Item,
					  numDic[Item]['FileNum'], # the num of files
					  numDic[Item]['FileNameNum'], # the num of different files
					  numDic[Item]['FileNameMax'][0][0], # the max  FileName
					  numDic[Item]['FileNameMax'][0][1], # the num of the max FileName
					  numDic[Item]['FacturerNameNum'], # the num of different Factor
					  numDic[Item]['FileMd5Num']] # the num of different md5
		writeToCsv(resultList)

	time6 = time.time()
	writeToFile("Second solve the dic: " + str(time6 - time5))





errorList = []
rootaddr = '/home/cy/Desktop/firmware_cluster/output'
pre = {}

if __name__ == "__main__":
	time1 = time.time()
	d = 5 #格子多大
	hashNum = 200 #哈希函数的个数

	p = 2**32-1

	if 1:
		#aList,bList = createHashDic(hashNum)
		#time2 = time.time()
		#print '生成hashAB的时间： ',time2-time1
		#writeToFile('生成hashAB的时间： '+ str(time2-time1))

		#GridFileDic = createGridFileDic(aList,bList,p,hashNum,d)
		#time3 = time.time()
		#print '生成GridFileDic的时间： ',time3-time2,len(GridFileDic)
		#print errorList
		#writeToFile('生成GridFileDic的时间： '+ str(time3-time2) + ' '+str(len(GridFileDic)))


		#

		#nodeList, edgeListAll = countGroup(GridFileDic,hashNum,d)
		# nodeList, edgeListAll = countGroup2(hashNum,d)
		#time4 = time.time()
		# print '分桶时间： ',time4 - time3
		# writeToFile('分桶时间： '+str(time4 - time3))

		#countConnectGraph(nodeList,edgeListAll)
		# countConnectGraph2()
		# time5 = time.time()
		# print '连通子图： ',time5-time4
		# writeToFile('连通子图： '+str(time5-time4))

	#findClass()
	#writeClass()
	#printClass()
		countNumInClass()


'''





def writeClass():
	conn = pymongo.MongoClient('10.10.12.82',27017)
	infoFile = list(conn.test.files.find())
	infoResult = list(conn.test.result.find())
	IdList = [item['_id'] for item in infoResult]
	print len(IdList)
	FileIdList = [ObjectId(item['ClassItem'][0]) for item in infoResult]
	print len(FileIdList)
	ClassList=[]
	for j in FileIdList:
		ClassList.append([item['class'] for item in infoFile if item['_id'] == j][0])
	print len(ClassList)
	for i in range(len(IdList)):
		print i
		conn.test.result.update({'_id':IdList[i]},{'$set':{'class':ClassList[i]}})


def printClass():

	conn = pymongo.MongoClient('10.10.12.82',27017)

	infoFile = list(conn.test.files.find())
	infoResult = list(conn.test.result.find())

	FileDic = {}
	for item in infoFile:
		FileDic[item['_id']] = item['StrFileName']

	if 1:
		classList = [item['class'] for item in infoResult]
		classList.sort()
		classSet = set(classList)
		count = 0
		for theclass in classSet:
			FileNameSet = set([item['FileName'] for item in infoFile if item['class'] == theclass])
			FileList = [item['StrFileName'] for item in infoFile if item['class'] == theclass]
			Num = len(FileNameSet)
			if Num!=1:
				print
				print 'Id: ',count
				print 'ClassId: ',theclass
				print 'FileNameSetNum: ',Num
				print 'FileNameSet: ',FileNameSet
				print 'FileNum: ',len(FileList)
				print 'bucketNum: ',classList.count(theclass)
				count += 1
				edgeListAll2 = [item['ClassItem'] for item in infoResult if item['class'] == theclass ]
				nodeList = []
				nodeDic = {}
				edgeListAll = []
				for item1 in edgeListAll2:
					edgeList = []
					for item2 in item1:
						StrFileName = FileDic[ObjectId(item2)]
						nodeList.append(StrFileName)
						nodeDic[StrFileName]=theclass
						edgeList.append(StrFileName)
					edgeListAll.append(edgeList)
				# g = nx.Graph()
				# g.add_nodes_from(nodeList)
				# print 'buckekList: '
				# for item in edgeListAll:
				# 	print item
				# for item in edgeListAll:
				# 	g.add_edges_from(itertools.combinations(item,2))
				#
				# dis = 0.2/math.sqrt(len(nodeList))
				# pos = nx.fruchterman_reingold_layout(g, k = dis, iterations = 8, scale=50.0, center = 25.0)
				# nx.draw(g, pos, node_size = 40, node_color='y')
				# # plt.savefig("path")
				# # plt.close('all')
				# plt.show()
				writeCsv2(nodeDic,edgeListAll)
	# 全部
	if 0:
		nodeDic = {}
		for item in infoFile:
			nodeDic[item['StrFileName']] = item['class']
		edgeListAll = [item['ClassItem'] for item in infoResult]
		writeCsv(nodeDic,edgeListAll,0)



def writeCsv(nodeDic,edgeListAll,flag = 0):
	nodeCsvAddr = 'node.csv'
	edgeCsvAddr = 'edge.csv'
	nodeHead = ['Id','Label','Mondularity Class']
	with open(nodeCsvAddr,'wb')as file:
		writer=csv.writer(file)
		writer.writerow(nodeHead)
		countNode = 1
		for strItem in nodeDic.keys():
			file.write("%d,%s,%s\n"%(countNode,strItem,nodeDic[strItem]))
			countNode += 1
		file.close()

	edgeHead = ['Source', 'Target', 'Type', 'Id']
	with open(edgeCsvAddr,'wb')as file:
		writer=csv.writer(file)
		writer.writerow(edgeHead)
		countEdge = 1
		for edgeList in edgeListAll:
			for item in itertools.combinations(edgeList,2):
				file.write("%s,%s,%s,%d\n"%(item[0],item[1],"Undirected",countEdge))
		file.close()

def writeCsv2(nodeDic,edgeListAll,flag = 0):
	className= nodeDic[nodeDic.keys()[0]]
	nodeCsvAddr = 'J:\output4\\node' + str(className) + '.csv'
	edgeCsvAddr = 'J:\output4\edge' + str(className) + '.csv'
	nodeHead = ['Id','Label','Mondularity Class']
	strFileNameMapID = {}
	with open(nodeCsvAddr,'wb')as file:
		writer=csv.writer(file)
		writer.writerow(nodeHead)
		countNode = 1
		for strItem in nodeDic.keys():
			strClass = strItem[strItem.find('_')+1:]
			file.write("%d,%s,%s\n"%(countNode,strItem,strClass))
			strFileNameMapID[strItem] = countNode
			countNode += 1
		file.close()

	edgeHead = ['Source', 'Target', 'Type', 'Id']
	with open(edgeCsvAddr,'wb')as file:
		writer=csv.writer(file)
		writer.writerow(edgeHead)
		countEdge = 1
		edge2Set = set()
		for edgeList in edgeListAll:
			for item in itertools.combinations(edgeList,2):
				edge2Set.add((strFileNameMapID[item[0]],strFileNameMapID[item[1]]))
		edge2List = list(edge2Set)
		for countEdge in range(len(edge2List)):
			file.write("%s,%s,%s,%d\n"%(edge2List[countEdge][0],edge2List[countEdge][1],"Undirected",countEdge+1))
		file.close()

'''


