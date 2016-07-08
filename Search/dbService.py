__author__ = 'changqing'

import pymongo

def connectDB():
	#id = "10.10.12.82"
	id = 'localhost'
	return pymongo.MongoClient(id, 27017)

