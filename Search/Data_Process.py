__author__ = 'qingqing'
import six.moves.cPickle as pickle
import theano
import numpy

def save_data(prob,name):

    fid = open(name,'wb')
    pickle.dump(prob,fid)
    fid.close()


def get_data(name):

    f = open(name,'rb')
    result = pickle.load(f)
    f.close()
    return result


def list2dic(Feature):
    flst = {}
    for item in Feature:
        flst[item['Func_Name']] = item
    return flst


def shared_dataset(data_xy, borrow=True):

    data_x, data_y = data_xy
    shared_x = theano.shared(numpy.asarray(data_x, dtype=theano.config.floatX), borrow=borrow)
    shared_y = theano.shared(numpy.asarray(data_y, dtype=theano.config.floatX), borrow=borrow)
    return (shared_x, T.cast(shared_y, 'int32'))


# def turnType(DataList):
#
#     featureList = []
#     labelList = []
#     for item in DataList:
#         featureList.append([item[key] for key in soriType + ssetType + sreCfgNumType + sreCfgListType])
#         labelList.append(item['label'])
#
#     #train_set_x, train_set_y = shared_dataset((featureList,labelList))
#     #return (train_set_x,train_set_y)
#     return ((featureList,labelList))


if __name__ == "__main__":
    prob = [[1,2,3],[4,5,6],[7,8,9]]
    filePath = 'cqn.txt'
    #save_data(prob,filePath)
    for i in get_data(filePath):
        print i
