#!/usr/bin/env python

from __future__ import print_function
from capstone import *
import binascii
import sys
from numpy import *

_python3 = sys.version_info.major == 3

INST_KINDS_LIMIT=15


MIPS_BIG_LIST=[]
MIPS_LITTLE_LIST=[]
ARM_LIST=[]
PPC_BIG_LIST=[]
PPC_LITTLE_LIST=[]

MIPS_BIG_TEXT=[]
MIPS_LITTLE_TEXT=[]
ARM_TEXT=[]
PPC_BIG_TEXT=[]
PPC_LITTLE_TEXT=[]

all_tests = (
	(CS_ARCH_MIPS, CS_MODE_MIPS32 + CS_MODE_LITTLE_ENDIAN, "MIPS-Little",MIPS_LITTLE_LIST),
    (CS_ARCH_MIPS, CS_MODE_MIPS32 + CS_MODE_BIG_ENDIAN, "MIPS-Big",MIPS_BIG_LIST),
	
    (CS_ARCH_ARM, CS_MODE_ARM, "ARM",ARM_LIST),
        #(CS_ARCH_PPC, CS_MODE_BIG_ENDIAN, "PPC-Big",PPC_BIG_LIST),
	#(CS_ARCH_PPC, CS_MODE_LITTLE_ENDIAN, "PPC-Little",PPC_LITTLE_LIST),
)

def get_longest_text(assam_list):
	start=0
	end=-1
	result_start=0
	result_end=0
	while True:
		try:
			end = assam_list.index(".byte",end+1)
			if (end-start) > ( result_end -result_start ) and len(set(assam_list[start:end]))>INST_KINDS_LIMIT:
				result_start=start
				result_end=end
			start = end+1
		except:
			break
	return assam_list[result_start:result_end]

def observe_inst_per(text_list):
	for inst in set(text_list):
		if (100*text_list.count(inst)/len(text_list))>0:
			print("%-10s%d"%(inst,100*text_list.count(inst)/len(text_list)))

def stumpClassify(dataMatrix,dimen,threshVal,threshIneq):#just classify the data
    retArray = ones((shape(dataMatrix)[0],1))
    if threshIneq == 'lt':
        retArray[dataMatrix[:,dimen] <= threshVal] = -1.0
    else:
        retArray[dataMatrix[:,dimen] > threshVal] = -1.0
    return retArray

def adaClassify(datToClass,classifierArr):
    dataMatrix = mat(datToClass)#do stuff similar to last aggClassEst in adaBoostTrainDS
    m = shape(dataMatrix)[0]
    aggClassEst = mat(zeros((m,1)))
    #total_alpha=0;
    for i in range(len(classifierArr)):
        classEst = stumpClassify(dataMatrix,classifierArr[i]['dim'],\
                                 classifierArr[i]['thresh'],\
                                 classifierArr[i]['ineq'])#call stump classify
        aggClassEst += classifierArr[i]['alpha']*classEst
    return sign(aggClassEst)

MIPS_classifierArr=[{'dim': 5, 'ineq': 'lt', 'thresh': 10.800000000000001, 'alpha': 1.7680583497807631}, {'dim': 1, 'ineq': 'lt', 'thresh': 11.699999999999999, 'alpha': 1.960986668140657}, {'dim': 4, 'ineq': 'lt', 'thresh': 2.3999999999999999, 'alpha': 1.1115807814799172}, {'dim': 1, 'ineq': 'lt', 'thresh': 7.7999999999999998, 'alpha': 1.167086014371683}]

ARM_classifierArr=[{'dim': 1, 'ineq': 'lt', 'thresh': 2.6000000000000001, 'alpha': 2.454485820159878}, {'dim': 0, 'ineq': 'lt', 'thresh': 5.4000000000000004, 'alpha': 2.595551641120444}, {'dim': 4, 'ineq': 'lt', 'thresh': 3.3999999999999999, 'alpha': 2.684387915098299}, {'dim': 6, 'ineq': 'lt', 'thresh': 0.0, 'alpha': 1.6003074328667952}]


def judge_MIPS(text_list):
	input_list=[]
	if "move" in text_list:
		move_per=100*text_list.count("move")/len(text_list)
	else:
		move_per=0
	if "lw" in text_list:
		lw_per=100*text_list.count("lw")/len(text_list)
	else:
		lw_per=0
	if "jal" in text_list:
		jal_per=100*text_list.count("jal")/len(text_list)
	else:
		jal_per=0
	if "jalr" in text_list:
		jalr_per=100*text_list.count("jalr")/len(text_list)
	else:
		jalr_per=0
	if "lui" in text_list:
		lui_per=100*text_list.count("lui")/len(text_list)
	else:
		lui_per=0
	if "addiu" in text_list:
		addiu_per=100*text_list.count("addiu")/len(text_list)
	else:
		addiu_per=0
	if "nop" in text_list:
		nop_per=100*text_list.count("nop")/len(text_list)
	else:
		nop_per=0
	if "sw" in text_list:
		sw_per=100*text_list.count("sw")/len(text_list)
	else:
		sw_per=0
	#print("%d	%d	%d	%d	%d	%d	%d	%d	-1"%(move_per,lw_per,jal_per,jalr_per,lui_per,addiu_per,nop_per,sw_per))
	input_list.append(move_per)
	input_list.append(lw_per)
	input_list.append(jal_per)
	input_list.append(jalr_per)
	input_list.append(lui_per)
	input_list.append(addiu_per)
	input_list.append(nop_per)
	input_list.append(sw_per)
	return adaClassify(input_list,MIPS_classifierArr)

def judge_ARM(text_list):
	input_list=[]
	if "ldr" in text_list:
		ldr_per=100*text_list.count("ldr")/len(text_list)
	else:
		ldr_per=0
	if "add" in text_list:
		add_per=100*text_list.count("add")/len(text_list)
	else:
		add_per=0
	if "mov" in text_list:
		mov_per=100*text_list.count("mov")/len(text_list)
	else:
		mov_per=0
	if "cmp" in text_list:
		cmp_per=100*text_list.count("cmp")/len(text_list)
	else:
		cmp_per=0
	if "bl" in text_list:
		bl_per=100*text_list.count("bl")/len(text_list)
	else:
		bl_per=0
	if "str" in text_list:
		str_per=100*text_list.count("str")/len(text_list)
	else:
		str_per=0
	if "beq" in text_list:
		beq_per=100*text_list.count("beq")/len(text_list)
	else:
		beq_per=0
	#print("%d	%d	%d	%d	%d	%d	%d	-1"%(ldr_per,add_per,mov_per,cmp_per,bl_per,str_per,beq_per))
	input_list.append(ldr_per)
	input_list.append(add_per)
	input_list.append(mov_per)
	input_list.append(cmp_per)
	input_list.append(bl_per)
	input_list.append(str_per)
	input_list.append(beq_per)
	return adaClassify(input_list,ARM_classifierArr)

file_object=open(sys.argv[1],'rb')
CODE=file_object.read()
file_object.close()

for arch, mode, comment, assam_list in all_tests:
	md = Cs(arch, mode)
	md.syntax = 0
	md.skipdata = True
	for insn in md.disasm(CODE, 0x1000):
		assam_list.append(insn.mnemonic)

MIPS_LITTLE_TEXT=get_longest_text(MIPS_LITTLE_LIST)
if judge_MIPS(MIPS_LITTLE_TEXT)==mat(([1])):
	print("MIPS-Little")
	sys.exit(0)

MIPS_BIG_TEXT=get_longest_text(MIPS_BIG_LIST)
if judge_MIPS(MIPS_BIG_TEXT)==mat(([1])):
	print("MIPS-Big")
	sys.exit(0)

ARM_TEXT=get_longest_text(ARM_LIST)
if judge_ARM(ARM_TEXT)==mat(([1])):
	print("ARM")
	sys.exit(0)

	
