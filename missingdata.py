import csv
import numpy as np
from sklearn import cross_validation
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import Ridge
from sklearn.preprocessing import normalize
from sklearn.preprocessing import Imputer

def loadData(filename):
	data = np.genfromtxt(filename, delimiter=',', dtype=None, loose=True, invalid_raise=False, skip_header=1)
	return data


def howManyMissing(data, col):
	missing = 0
	for i in data:
		if(i[col] == 0 or i[col] == ""):
			missing = missing + 1
	return missing

def getMissingDataCount(data):
	missing = {}
	for i in range(0,len(data[0])):
		missing[i] = howManyMissing(data, i)
	return missing

def featureNotThere(d, i):
	if(d[i] == 0 or d[i] == ""):
		return True
	return False

def dataDeletion(data):
	new_set = []
	for d in data:
		include = True
		for i in range(0,8):
			if(featureNotThere(d, i)):
				include = False
		if(featureNotThere(d,21)):
			include = False
		if(include):
			new_set.append(d)
	return new_set

def getMeanforFeatures(data):
	feature_means = []
	for i in xrange(len(data[0])):
		total = 0
		for d in data:
			total = total + float(d[i])
		total = total/len(data)
		feature_means.append(total)
	return feature_means

def dataFillMean(data, feature_means):
	new_set = []
	for d in data:
		for i in xrange(len(d)):
			if((i in range(0,8) or i == 21) and featureNotThere(d,i)):
				d[i] = feature_means[i]
		new_set.append(d)
	return new_set

def dataFillMeanIndicator(data, feature_means):
	new_set = []
	for d in data:
		ind = 0
		dn = []
		for i in xrange(len(d)):
			if((i in range(0,8) or i == 21) and featureNotThere(d,i)):
				d[i] = feature_means[i]
				ind = 1 
		for i in xrange(len(d)):
			if(i == 21):
				dn.append(ind)
			dn.append(d[i])
		new_set.append(np.array(dn))
	return new_set
				
def dataFillImputer(data):
	imp = Imputer(missing_values=0, strategy='most_frequent', axis=0)
	new_data = splitData(data)
	new_data = imp.fit_transform(np.array(new_data))
	new_data = new_data.tolist()
	data = rebuildData(data, new_data)
	return data
	
def splitData(data):
	new_set = []
	for d in data:
		new_d = []
		for i in xrange(len(d)):
			if(i in range(0,8) or i == 21):
				new_d.append(d[i])
		new_set.append(d)
	return new_set
			
def rebuildData(data, new_data):
	n = []
	print len(data)
	print len(new_data)
	for j in xrange(len(data)):
		new_d = []
		for i in xrange(len(data[j])):
			if(i in range(0,8)):
				new_d.append(new_data[j][i])
			elif(i == 21):
				new_d.append(new_data[j][8])
			else:
				new_d.append(data[j][i])
		n.append(new_d)
	return n

def extractOutput(data):
	X = []
	Y = []
	for d in data:
		tmp = d.tolist()
		Y.append(tmp[-1])
		X.append(np.array(tmp[:-1]))
	X = np.array(X)
	Y = np.array(Y)
	return (X,Y)

def getMeanError(pred, Y):
	MSE = 0
	for i in xrange(len(pred)):
		MSE = MSE + (pred[i] - Y[i])*(pred[i] - Y[i])
	return np.sqrt(MSE/float(len(pred)))
	
if __name__=='__main__':
	data = loadData("data/data/final_dataDec.csv")

	# CHOOSE HOW TO HANDLE MISSING DATA 
	#nData = dataDeletion(data)
	#nData = dataFillMean(data,getMeanforFeatures(data))
	#nData = dataFillMeanIndicator(data,getMeanforFeatures(data))
	#nData = dataFillImputer(data) #DOESNT WORK
	nData = data

	print len(nData)
	counts = getMissingDataCount(nData)
	print counts

	(X,Y) = extractOutput(nData)
	kf = cross_validation.KFold(len(Y), n_folds=4)
	accs = []
	for train_index, test_index in kf:
		#print("TRAIN:", train_index, "TEST:", test_index)
		X_train, X_test = X[train_index], X[test_index]
		Y_train, Y_test = Y[train_index], Y[test_index]
		clf = Ridge(alpha=1.5)
		clf.fit(X_train, Y_train) 
		acc = clf.predict(X_test)
		MSE = getMeanError(acc, Y_test)
		accs.append(MSE)
	print np.mean(accs)
