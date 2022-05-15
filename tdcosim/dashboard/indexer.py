from __future__ import division
import os
import sys
import json
import pickle
import io
import pdb
import time
from multiprocessing import Process, Queue, cpu_count

import pandas as pd
import numpy as np


class Indexer(object):

	def get_index_from_string(self,indObj,dataStr,stride,dfRowOffset):
		cols=dataStr.split(',')
		if cols[2] not in indObj['tnodeid']:
			indObj['tnodeid'][cols[2]]=[]
		if indObj['tnodeid'][cols[2]] and indObj['tnodeid'][cols[2]][-1][1]==dfRowOffset-1:
			indObj['tnodeid'][cols[2]][-1][1]=dfRowOffset+stride-1
		else:
			indObj['tnodeid'][cols[2]].append([dfRowOffset,dfRowOffset+stride-1])

		if cols[5] not in indObj['dnodeid']:
			indObj['dnodeid'][cols[5]]=[]
		if indObj['dnodeid'][cols[5]] and indObj['dnodeid'][cols[5]][-1][1]==dfRowOffset-1:
			indObj['dnodeid'][cols[5]][-1][1]=dfRowOffset+stride-1
		else:
			indObj['dnodeid'][cols[5]].append([dfRowOffset,dfRowOffset+stride-1])

		if cols[6] not in indObj['property']:
			indObj['property'][cols[6]]=[]
		if indObj['property'][cols[6]] and indObj['property'][cols[6]][-1][1]==dfRowOffset-1:
			indObj['property'][cols[6]][-1][1]=dfRowOffset+stride-1
		else:
			indObj['property'][cols[6]].append([dfRowOffset,dfRowOffset+stride-1])

	def _get_continous_ind(self,ind):
		diff=ind[1::]-ind[:-1:]
		indJump=np.asarray(diff!=1).nonzero()[0]+1
		indJump=np.array([0]+indJump.tolist()+[len(ind)-1])

		res=[]
		for n in range(len(indJump)-1):
			res.append([int(ind[indJump[n]]),int(ind[indJump[n+1]-1])])
		res[-1][-1]+=1
		return res

	def gather_all_indices(self,fpath,columns=['tnodeid','property'],multiproc=False,nProc=2):
		"""Main entry point for gathering relevant indices"""
		assert '.csv' in fpath,'fpath should point to a csv file'
		res={}

		if not multiproc:
			dtype={'dfeederid':'object','dnodeid':'object','property':'object','scenario':'object',
			't':'float64','tnodeid':'object','tnodesubid':'object','value':'float64'}
			df=pd.read_csv(fpath,dtype=dtype)

			if df.tnodeid.dtype!='object':
				df.tnodeid=df.tnodeid.astype('object')
			
			for thisColumn in columns:
				res[thisColumn]={}
				for entry in set(df[thisColumn]):
					if (thisColumn=='property' and entry.isupper()) or (thisColumn!='property'):
						thisDf=df[df[thisColumn]==entry]
						res[thisColumn][entry]=self._get_continous_ind(np.array(thisDf.index.tolist()))
			res['dfLen']=df.shape[0]
			res['ineq']=self._generate_ineq_ind_tree(df)
			res['pointer']=self._get_ind(fpath)

		elif multiproc:
			res=self._generate_ineq_ind_tree_multiproc(fpath,nProc=nProc,\
			get_continous_ind_obj=Indexer._get_continous_ind)
			res['pointer']=self._get_ind(fpath)
		
		return res

	def save_indexer_info(self,sourcePath,savePath=None,multiproc=True,nProc=None):
		"""Will gather the indices of the sourcePath csv file and save index information at savePath
		as a JSON file."""
		if not nProc and multiproc:
			nProc=cpu_count()
		if not savePath:
			savePath=sourcePath.replace('.csv','.json')
		res=self.gather_all_indices(sourcePath,multiproc,nProc)
		res=json.dumps(res)#### performance seems to be faster than json.dump for large dataset
		f=open(savePath,'w')
		f.write(res)
		f.close()

	def query(self,fpath,ind,tnodeidQry,propertyQry,valueQry=None):
		"""Main entry point for running queries"""
		# qry=[{'lhs':'tnodeid','comp':'eq','rhs':'1'},
		# {'lhs':'property','comp':'eq','rhs':'VOLT'},{'lhs':'value','comp':'le','rhs':1.0}]
		try:
			res=[]
			dfLen=ind['dfLen']
			rootNode=ind['ineq'][tnodeidQry][propertyQry]
			qryInd=[]
			if not valueQry:
				qryInd=range(rootNode['minmax'][0],rootNode['minmax'][1])
			else:
				qryInd=[]; binInd=[]
				if isinstance(valueQry,list) and len(valueQry)==2:
					valueQry={'comp':valueQry[0],'rhs':valueQry[1]}
				bins=np.array(rootNode['bins'])
				tree=rootNode['tree']
				if valueQry['comp']=='le':
					binInd=np.where(bins<=valueQry['rhs'])[0]
				elif valueQry['comp']=='ge':
					binInd=np.where(bins>=valueQry['rhs'])[0]
				for thisBinInd in binInd:
					if tree[thisBinInd+1]:
						qryInd+=range(tree[thisBinInd+1][0],tree[thisBinInd+1][1])
			qryInd=list(qryInd)
			qryInd.sort()

			dtype={'dfeederid':'object','dnodeid':'object','property':'object','scenario':'object',
			't':'float64','tnodeid':'object','tnodesubid':'object','value':'float64'}
			thisDf=pd.read_csv(io.StringIO(self._get_data(fpath,ind['pointer'],qryInd[0]+1,qryInd[-1]+1)),dtype=dtype)

			#### TODO: Need to run the result through pandas once to ensure correctness of result. Small overhead
			#### as the data size is small.

			return thisDf
		except:
			raise

	def _get_ind(self,fpath):
		f=open(fpath)
		res=[]
		data=f.readline()
		res.extend([len(data)+1])

		while data:
			data=f.readline()
			if len(data)>1:
				res.extend([len(data)+1])
		f.close()
		return res


	def _get_data(self,fpath,res,startInd,endInd):
		if not isinstance(res,np.ndarray):
			res=np.cumsum(res)

		assert endInd>=startInd
		f=open(fpath)
		header=f.read(res[0]-1)
		f.seek(res[startInd])
		data=header+f.read(res[endInd-1]-res[startInd-1]-(endInd-(startInd-1))-1)
		f.close()
		if isinstance(data,str) and sys.version_info.major==2:
			data=data.decode()
		return data

	def add_index_to_results_folder(self,folderPath,df=None):
		assert os.path.exists(folderPath)

		if not df:
			pklFilePath=os.path.join(folderPath,'df_pickle.pkl')
			assert os.path.exists(pklFilePath)
			df=pd.read_pickle(pklFilePath)

		csvFilePath=os.path.join(folderPath,'df.csv')
		df.to_csv(csvFilePath)

		ind=gather_all_indices(csvFilePath)
		indexFilePath=os.path.join(folderPath,'index.pkl')
		pickle.dump(ind,open(indexFilePath,'w'))

	def _generate_ineq_ind_tree(self,input,nBin=10):
		if isinstance(input,str):
			assert os.path.exists(input) and '.pkl' in input
			df=pd.read_pickle(input)
		elif isinstance(input,pd.DataFrame):
			df=input
		else:
			raise

		# first form tnode index
		res={thisTnodeid:{} for thisTnodeid in set(df.tnodeid)}
		for thisTnodeid in res:
			thisTnodeDf=df[df.tnodeid==thisTnodeid]
			for thisProp in set(df.property):
				if not thisProp.isupper():
					thisTnodeDnodeDf=thisTnodeDf[thisTnodeDf.dnodeid=='1']
				else:
					thisTnodeDnodeDf=thisTnodeDf
				thisDf=thisTnodeDnodeDf[thisTnodeDnodeDf.property==thisProp]
				if not thisDf.empty:
					valMax,valMin=thisDf.value.max(),thisDf.value.min()
					stepSize=(valMax-valMin)/nBin
					if valMax!=valMin:
						bins=np.arange(valMin,valMax,stepSize).tolist()
					else:
						bins=[valMax]
					res[thisTnodeid][thisProp]={'tree':{},'bins':bins,'minmax':[]}
					thisRes=res[thisTnodeid][thisProp]['tree']
					minVal=[]; maxVal=[]
					for n in range(1,len(bins)):
						thisDfBin=thisDf[(thisDf.value>=bins[n-1])&(thisDf.value<=bins[n])]
						if not thisDfBin.empty:
							thisRes[n]=[int(thisDfBin.index.min()),int(thisDfBin.index.max())]
							minVal.append(thisRes[n][0])
							maxVal.append(thisRes[n][1])
						else:
							thisRes[n]=[]
					if minVal and maxVal:
						res[thisTnodeid][thisProp]['minmax']=[int(min(minVal)),int(max(maxVal))]
		return res

	def _generate_ineq_ind_tree_multiproc(self,input,nBin=10,nProc=2,get_continous_ind_obj=None):
		k=[str(n) for n in range(1,68+1)]
		kProc=int(np.ceil(len(k)/nProc))

		q = Queue()
		procs=[]
		availableProps=['VOLT','POWR','PLOD','QLOD','SPD']
		for n in range(nProc):
			if n!=nProc-1:
				assignedTnodeid=False
				addDfLen=False
				if availableProps:
					assignedProp=availableProps.pop(0)
				else:
					assignedProp=None
				thisRes=[thisTnodeid for thisTnodeid in k[n*kProc:(n+1)*kProc]]
			else:
				assignedTnodeid=True
				addDfLen=True
				if availableProps:
					assignedProp=availableProps
				else:
					assignedProp=None
				thisRes=[thisTnodeid for thisTnodeid in k[n*kProc::]]
			procs.append(Process(target=self.mp_helper, args=(input,thisRes,nBin,q,get_continous_ind_obj,assignedTnodeid,assignedProp,addDfLen)))

		for p in procs:
			p.start()

		res={'ineq':{},'tnodeid':{},'property':{}}
		for n in range(nProc):
			temp=q.get()
			if 'eq' in temp and 'tnodeid' in temp['eq']:
				res['tnodeid'].update(temp['eq'].pop('tnodeid'))
			if 'eq' in temp and 'property' in temp['eq']:
				res['property'].update(temp['eq'].pop('property'))
				temp.pop('eq')
			if 'dfLen' in temp:
				res['dfLen']=temp['dfLen']
			res['ineq'].update(temp)

		for p in procs:
			p.join()
		return res

	def mp_helper(self,df,ind,nBin,q,get_continous_ind_obj=None,assignedTnodeid=False,assignedProp=None,addDfLen=False):
		dtype={'dfeederid':'object','dnodeid':'object','property':'object','scenario':'object',
		't':'float64','tnodeid':'object','tnodesubid':'object','value':'float64'}
		df=pd.read_csv(df,dtype=dtype)

		if df.tnodeid.dtype!='object':
			df.tnodeid=df.tnodeid.astype('object')

		res={}
		for thisTnodeid in ind:
			thisTnodeDf=df[df.tnodeid==thisTnodeid]
			res[thisTnodeid]={}
			for thisProp in set(df.property):
				if not thisProp.isupper():
					thisTnodeDnodeDf=thisTnodeDf[thisTnodeDf.dnodeid=='1']
				else:
					thisTnodeDnodeDf=thisTnodeDf
				thisDf=thisTnodeDnodeDf[thisTnodeDnodeDf.property==thisProp]
				if not thisDf.empty:
					valMax,valMin=thisDf.value.max(),thisDf.value.min()
					stepSize=(valMax-valMin)/nBin
					if valMax!=valMin:
						bins=np.arange(valMin,valMax,stepSize).tolist()
					else:
						bins=[valMax]
					res[thisTnodeid][thisProp]={'tree':{},'bins':bins,'minmax':[]}
					thisRes=res[thisTnodeid][thisProp]['tree']
					minVal=[]; maxVal=[]
					for n in range(1,len(bins)):
						thisDfBin=thisDf[(thisDf.value>=bins[n-1])&(thisDf.value<=bins[n])]
						if not thisDfBin.empty:
							thisRes[n]=[int(thisDfBin.index.min()),int(thisDfBin.index.max())]
							minVal.append(thisRes[n][0])
							maxVal.append(thisRes[n][1])
						else:
							thisRes[n]=[]
					if minVal and maxVal:
						res[thisTnodeid][thisProp]['minmax']=[int(min(minVal)),int(max(maxVal))]

		if assignedProp and isinstance(assignedProp,str):
			assignedProp=[assignedProp]
		res['eq']={}
		for thisColumn in ['tnodeid','property']:
			res['eq'][thisColumn]={}
			for entry in set(df[thisColumn]):
				if assignedTnodeid and thisColumn=='tnodeid':
					thisDf=df[df[thisColumn]==entry]
					res['eq'][thisColumn][entry]=get_continous_ind_obj(self,np.array(thisDf.index.tolist()))
				if assignedProp:
					for thisProp in assignedProp:
						if (thisColumn=='property' and entry.isupper()) and (entry==thisProp):
							thisDf=df[df[thisColumn]==entry]
							res['eq'][thisColumn][entry]=get_continous_ind_obj(self,np.array(thisDf.index.tolist()))

		if addDfLen:
			res['dfLen']=len(df)

		q.put(res)