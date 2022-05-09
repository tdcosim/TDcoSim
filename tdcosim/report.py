from __future__ import division
import os
import string
import json
import uuid
import pdb
import re
import time
import copy

import six
import xlsxwriter
import pandas as pd
import numpy as np


def generate_output(GlobalData,excel=True,dataframe=True,config=True):
	try:
		if excel:
			fpath=os.path.join(GlobalData.config['outputConfig']['outputDir'],'report.xlsx')
			generate_excel_report(GlobalData,fpath)
		if dataframe:
			outputConfig=GlobalData.config['outputConfig']
			scenario=outputConfig['scenarioID'] if 'scenarioID' in outputConfig else None
			generate_dataframe(GlobalData,scenario)
		if config:
			save_config(GlobalData)
	except:
		raise


def generate_excel_report(GlobalData,fpath=None,sim=None):
	try:
		# defaults
		if not fpath:
			fpath=os.path.join(GlobalData.config['outputConfig']['outputDir'],
			'report_{}.xlsx'.format(GlobalData.config['outputConfig']['simID']))
		if not sim:
			sim=GlobalData.config['simulationConfig']['simType']

		wb=xlsxwriter.Workbook(fpath)
		bold=wb.add_format({'bold':True})
		red=wb.add_format({'font_color':'red'})
		data=GlobalData.data

		f_colnum=lambda count:[alphabet+'{}'.format(count) for alphabet in string.ascii_uppercase]

		if sim == 'dynamic':
			ws=wb.add_worksheet('TNet_results')
			colHeader=['Time','BusID','P','Q','Vmag']
			colNumber=[]; count=1

			while len(colNumber)<len(colHeader):
				colNumber.extend(f_colnum(count))
				count+=1

			for col,val in zip(colNumber,colHeader):
				ws.write(col,val,bold)

			row=1
			t_all=data['TNet']['Dynamic'].keys()
			t_all.sort()
			for t in t_all:
				for busID in data['TNet']['Dynamic'][t]['S']:
					ws.write(row,0,t)
					ws.write(row,1,busID)
					ws.write(row,2,data['TNet']['Dynamic'][t]['S'][busID]['P'])
					ws.write(row,3,data['TNet']['Dynamic'][t]['S'][busID]['Q'])
					ws.write(row,4,data['TNet']['Dynamic'][t]['V'][busID])
					row+=1

		elif sim=='static':
			colHeader=['dispatch_number','bus_number','P','Q','Vmag']
			ws={}
			# find all the distribution nodes
			staticData=data['static']
			for node in staticData[0]['S']:
				if node not in ws:
					ws[node]=wb.add_worksheet('qsts_results_{}'.format(node))

			for node in ws:
				for n in range(len(colHeader)):
					ws[node].write(0,n,colHeader[n])

			staticDataKeys=staticData.keys()
			if six.PY3:
				staticDataKeys=list(staticDataKeys)
			staticDataKeys.sort()
			row=1
			for dispatch in staticDataKeys:
				for node in staticData[dispatch]['S']:
					ws[node].write(row,0,dispatch)
					ws[node].write(row,1,node)
					ws[node].write(row,2,staticData[dispatch]['S'][node]['P'])
					ws[node].write(row,3,staticData[dispatch]['S'][node]['Q'])
					ws[node].write(row,4,staticData[dispatch]['V'][node])
				row+=1

		# add monitor data
		ws={}
		for t in GlobalData.data['monitorData']:
			for node in GlobalData.data['monitorData'][t]:
				if node not in ws:
					ws[node]=wb.add_worksheet('feeder_{}'.format(node))

		t=GlobalData.data['monitorData'].keys()
		if six.PY3:
			t=list(t)
		t.sort()
		colMap={}; colMap['time']=0
		for node in GlobalData.data['monitorData'][t[0]]:
			ws[node].write(0,0,'time')
			count=1
			items=GlobalData.data['monitorData'][t[0]][node].keys()
			if six.PY3:
				items=list(items)
			items.sort()
			for item in items:
				if item.lower()=='vmag' or item.lower()=='vang':
					for distNode in GlobalData.data['monitorData'][t[0]][node][item].keys():
						for phase in ['a','b','c']:
							colName=item.lower()+'_{}_{}'.format(distNode,phase)
							ws[node].write(0,count,colName)
							colMap[colName]=count
							count+=1
				elif item.lower()=='der':
					for distNode in GlobalData.data['monitorData'][t[0]][node][item].keys():
						for varName in ['P','Q']:
							colName=item.lower()+'_{}_{}'.format(distNode,varName)
							ws[node].write(0,count,colName)
							colMap[colName]=count
							count+=1

		row=1
		for entry in t:# write data
			for node in GlobalData.data['monitorData'][entry]:
				ws[node].write(row,colMap['time'],entry)
				for item in GlobalData.data['monitorData'][entry][node]:
					if item.lower()=='vmag' or item.lower()=='vang':
						for distNode in GlobalData.data['monitorData'][entry][node][item].keys():
							for phase in ['a','b','c']:
								colName=item.lower()+'_{}_{}'.format(distNode,phase)
								if phase in GlobalData.data['monitorData'][entry][node][item][distNode]:
									ws[node].write(row,colMap[colName],
									GlobalData.data['monitorData'][entry][node][item][distNode][phase])
					elif item.lower()=='der':
						for distNode in GlobalData.data['monitorData'][entry][node][item].keys():
							for varName in ['P','Q']:
								colName=item.lower()+'_{}_{}'.format(distNode,varName)
								if varName in GlobalData.data['monitorData'][entry][node][item][distNode]:
									ws[node].write(row,colMap[colName],
									GlobalData.data['monitorData'][entry][node][item][distNode][varName])
			row+=1# increase counter at every t

		wb.close()
	except:
		print("Failed generate report")							
		raise

def save_config(GlobalData):
	try:
		removeID=['f_err','f_out','proc','conn']
		for thisNode in GlobalData.data['DNet']['Nodes']:
			for thisRemoveID in removeID:
				_=GlobalData.data['DNet']['Nodes'][thisNode].pop(thisRemoveID)

		fpath=os.path.join(GlobalData.config['outputConfig']['outputDir'],'options.json')
		data={'data':GlobalData.data,'config':GlobalData.config}
		if GlobalData.config['simulationConfig']['simType']=='dynamic':
			_=data['data'].pop('monitorData')
		if 'Dynamic' in data['data']['TNet']:
			_=data['data']['TNet'].pop('Dynamic')
		json.dump(data,open(fpath,'w'),indent=3)
	except:
		raise

def generate_dataframe(GlobalData,scenario=None,saveFile=True):
	try:
		####TODO: This is a temp fix for psspy import issue.
		# psseConfig->installLocation is set in psse_model, if tdcosim.report, which uses psspy and dyntools,
		# is imported when this module is loaded it could result in a) import error, b) wrong version
		# imported or c) everything works fine because psse path is already set and the user is still
		# pointing to the same path using psseConfig->installLocation. As a temp workaround lazy load  
		import psspy
		import dyntools

		if not scenario:
			scenario=uuid.uuid4().hex

		monData=GlobalData.data['monitorData']

		t=monData.keys()
		if six.PY3:
			t=list(t)
		t.sort()
		data={'t':[],'tnodeid':[],'tnodesubid':[],'dfeederid':[],'dnodeid':[],'property':[],'value':[]}
		dataStr='scenario,t,tnodeid,tnodesubid,dfeederid,dnodeid,property,value\n'
		for thisTime in t:
			for thisTDInterface in monData[thisTime]:
				for thisProp in monData[thisTime][thisTDInterface]:
					for thisNodeID in monData[thisTime][thisTDInterface][thisProp]:
						for thisSubProp in monData[thisTime][thisTDInterface][thisProp][thisNodeID]:
							data['t'].append(thisTime)
							data['tnodeid'].append(str(thisTDInterface))
							data['dnodeid'].append(thisNodeID)
							data['property'].append(thisProp+'_'+thisSubProp)
							data['value'].append(monData[thisTime][thisTDInterface][thisProp][thisNodeID][thisSubProp])
							dataStr+='{},{},{},{},{},{},{},{}\n'.format(scenario,thisTime,thisTDInterface,'','',thisNodeID,\
							thisProp+'_'+thisSubProp,monData[thisTime][thisTDInterface][thisProp][thisNodeID][thisSubProp])

		outputConfig=GlobalData.config['outputConfig']
		if 'Dynamic' in GlobalData.data['TNet']:
			for thisTime in GlobalData.data['TNet']['Dynamic']:
				for thisTnodeid in GlobalData.data['TNet']['Dynamic'][thisTime]['S']:
					for thisDnodeid in GlobalData.data['TNet']['Dynamic'][thisTime]['S'][thisTnodeid]['derX']:
						thisDerX=GlobalData.data['TNet']['Dynamic'][thisTime]['S'][thisTnodeid]['derX'][thisDnodeid]['0']####only use one PV to reduce data size
						vt_filt_val=thisDerX[3]
						data['t'].append(thisTime)
						data['tnodeid'].append(str(thisTnodeid))
						data['dnodeid'].append(thisDnodeid)
						data['property'].append('vt_filt_fast_der')
						data['value'].append(vt_filt_val)
						dataStr+='{},{},{},{},{},{},{},{}\n'.format(scenario,thisTime,thisTnodeid,'','',thisDnodeid,\
						'vt_filt_fast_der',vt_filt_val)
			data['scenario']=[scenario]*len(data['t'])
			data['dfeederid']=['1']*len(data['t'])
			data['tnodesubid']=['']*len(data['t'])
			df_monitorData=pd.DataFrame(data)

		if GlobalData.config['simulationConfig']['simType']=='dynamic':
			stride=2
			fname=outputConfig['outputfilename'].split('.')[0]+'.out'
			outfile=os.path.join(outputConfig['outputDir'],fname)
			outfile=outfile.encode('ascii')
			psseVersion=psspy.psseversion()[1]
			if psseVersion==33:
				chnfobj = dyntools.CHNF(outfile,0)
				_, ch_id, ch_data = chnfobj.get_data()
			elif psseVersion==35:
				chnfobj = dyntools.CHNF(outfile,outvrsn=0)
				_, ch_id, ch_data = chnfobj.get_data()
			
			events=GlobalData.config['simulationConfig']['dynamicConfig']['events']
			eventTimes=list(set([events[thisEvent]['time'] for thisEvent in events]))
			eventTimes.remove(max(eventTimes))
	
			t=np.array(ch_data['time'])
			ind=np.arange(len(t))
			indFilt=[]
			for thisEventTime in eventTimes:
				indTemp=np.where(np.bitwise_and(t>=thisEventTime-1e-6,t<=thisEventTime+1e-6))[0].tolist()
				if len(indFilt)==0:
					indFilt+=ind[0:indTemp[0]:stride].tolist()+indTemp
				else:
					indFilt+=ind[indFilt[-1]+1:indTemp[0]:stride].tolist()+indTemp
			if not indFilt:
				indFilt=ind[0::stride].tolist()
			else:
				indFilt+=ind[indFilt[-1]+1::stride].tolist()
			indFilt=np.array(indFilt)

			symbols=[ch_id[entry] for entry in ch_id]
			properties=list(set([ch_id[entry].split(' ')[0] for entry in ch_id]))
			nodes=list(set([ch_id[entry].split(' ')[1][0:ch_id[entry].split(' ')[1].find(
			'[')].replace(' ','') for entry in ch_id if 'Time' not in ch_id[entry]]))

			tnodeid=[]; tnodesubid=[]; props=[]; value=[]; count=0
			ch_id_keys=ch_id.keys()
			if six.PY3:
				ch_id_keys=list(ch_id_keys)

			for entry in ch_id_keys:
				if not isinstance(entry,str):
					prop=re.findall('[\w]{1,}',ch_id[entry])[0]
					node=re.findall('[\d]{1,}',ch_id[entry])[0]
					if prop.isalnum():
						prop=prop.replace(node,'')	
					if prop!='VOLT':
						tnodesubid.extend([re.findall('[\d]{1,}',ch_id[entry])[-1]]*len(indFilt))
					else:
						tnodesubid.extend(['']*len(indFilt))
					value.extend(np.array(ch_data[entry])[indFilt])
					props.extend([prop]*len(indFilt))
					tnodeid.extend([node]*len(indFilt))
					count+=1

			t_all=[]
			t_all.extend(t[indFilt].tolist()*count)

			df=pd.DataFrame(columns=['scenario','t','tnodeid','tnodesubid','dfeederid','dnodeid','property',
			'value'])
			df['t'],df['tnodeid'],df['tnodesubid'],df['property'],df['value']=t_all,tnodeid,tnodesubid,props,value
			df['scenario']=[scenario]*len(t_all)
			df=df.append(df_monitorData,ignore_index=True,sort=False)

			dataStr+='\n'.join([','.join([str(item) for item in entry]) for entry in zip([scenario]*len(t_all),t_all,tnodeid,tnodesubid,['']*len(t_all),['']*len(t_all),props,value)])

			# updates for der_p_total and der_q_total
			df,data_der_PQ=get_der_total_injection(df,GlobalData)
			if data_der_PQ['der_P']:
				for thisProp in data_der_PQ:
					data_der=data_der_PQ[thisProp]
					dataStr+='\n'
					dataStr+='\n'.join([','.join([str(item) for item in entry]) for entry in zip(data_der['scenario'],
					data_der['t'],data_der['tnodeid'],data_der['tnodesubid'],data_der['dfeederid'],
					data_der['dnodeid'],data_der['property'],data_der['value'])])

			df,deraNodes=update_dera_nodes(df,GlobalData)

			for node in deraNodes:
				node=str(node)
				dataStr=re.sub(r'([\w]{1,},[\d.]{1,},[\d.]{1,},[\w\d]{0,},[\w\d]{0,}),'+node+',POWR',r'\1,'+node+',der_p_total',dataStr)
				dataStr=re.sub(r'([\w]{1,},[\d.]{1,},[\d.]{1,},[\w\d]{0,},[\w\d]{0,}),'+node+',VARS',r'\1,'+node+',der_q_total',dataStr)

		elif GlobalData.config['simulationConfig']['simType']=='static':
			data['dfeederid']=['1']*len(data['t'])
			data['tnodesubid']=['']*len(data['t'])
			data['scenario']=[scenario]*len(data['t'])
			df=pd.DataFrame(data)
			
			dataStr+='\n'.join([','.join([str(item) for item in entry]) for entry in zip(data['scenario'],data['t'],
			data['tnodeid'],data['tnodesubid'],data['dfeederid'],data['dnodeid'],data['property'],data['value'])])

		f=open(os.path.join(outputConfig['outputDir'],'df.csv'),'w')
		f.write(dataStr)
		f.close()

		fpath=os.path.join(outputConfig['outputDir'],'df_pickle')
		try:
			print("Trying to save TDcoSim dataframe as a .pkl file")
			df.to_pickle(fpath+".pkl")
			fpath+='.pkl'
		except MemoryError:
			print("Saving to .CSV file due to .pkl memory error")
			df.to_csv(fpath+".csv",index=False)
			fpath+='.csv'
		print("Successfully saved as {}...".format(fpath))

		return df
	except:
		raise

def get_der_total_injection(df,GlobalData):
	try:
		data4csv={}
		for thisProp in ['der_P','der_Q']:
			res=df[df.property==thisProp]
			data={}
			if not res.empty:
				data={'dfeederid':[],'dnodeid':[],'property':[],'scenario':[],'t':[],
				'tnodeid':[],'tnodesubid':[],'value':[]}
				for entry in set(res.tnodeid):
					thisRes=res[res.tnodeid==entry]
					res_value=None
					for thisDER in set(thisRes.dnodeid):
						thisDF=thisRes[thisRes.dnodeid==thisDER]
						thisDF=thisDF.sort_values(by='t')
						if isinstance(res_value,type(None)):
							res_value=thisDF.value.values
						else:
							res_value+=thisDF.value.values
					res_value=res_value*GlobalData.data['DNet']['Nodes'][int(entry)]['scale']
					data['value'].extend(res_value.tolist())
					data['t'].extend(thisDF.t.values.tolist())
					data['tnodeid'].extend([entry]*len(thisDF.t.values.tolist()))

				data['property']=['{}_total'.format(thisProp.lower())]*len(data['value'])
				data['scenario']=list(set(res.scenario))
				assert len(data['scenario'])==1
				data['scenario']=data['scenario']*len(data['value'])
				data['dfeederid']=['']*len(data['value'])
				data['dnodeid']=['']*len(data['value'])
				data['tnodesubid']=['']*len(data['value'])

				data4csv[thisProp]=copy.deepcopy(data)

				df_new=pd.DataFrame(data)
				if not df_new.empty: 
					df=df.append(df_new,ignore_index=True,sort=False)
					df.reindex()

		return df,data4csv
	except:
		raise

def update_dera_nodes(df,GlobalData):
	try:
		deraNodes=[]
		if 'dera' in GlobalData.config['simulationConfig']:
			for entry in GlobalData.config['simulationConfig']['dera']:
				deraNodes.extend(GlobalData.config['simulationConfig']['dera'][entry])
		
		for node in deraNodes:
			node=str(node)
			df.loc[(df.tnodeid==node)&(df.property=='POWR'),'property']='der_p_total'
			df.loc[(df.tnodeid==node)&(df.property=='VARS'),'property']='der_q_total'

		return df,deraNodes
	except:
		raise