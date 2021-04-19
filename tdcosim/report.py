from __future__ import division
import os
import string
import json
import uuid
import pdb

import six
import xlsxwriter
import pandas as pd


def generate_output(GlobalData,excel=True,dataframe=True,config=False):
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

			dispatch=staticData.keys()
			dispatch.sort()
			row=1
			for dispatch in staticData:
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
		t.sort()
		colMap={}; colMap['time']=0
		for node in GlobalData.data['monitorData'][t[0]]:
			ws[node].write(0,0,'time')
			count=1
			items=GlobalData.data['monitorData'][t[0]][node].keys()
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

			data['scenario']=[scenario]*len(data['t'])
			data['dfeederid']=['1']*len(data['t'])
			data['tnodesubid']=['']*len(data['t'])
			df_monitorData=pd.DataFrame(data)

			stride=2
			outputConfig=GlobalData.config['outputConfig']
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

			symbols=[ch_id[entry] for entry in ch_id]
			properties=list(set([ch_id[entry].split(' ')[0] for entry in ch_id]))
			nodes=list(set([ch_id[entry].split(' ')[1][0:ch_id[entry].split(' ')[1].find(
			'[')].replace(' ','') for entry in ch_id if 'Time' not in ch_id[entry]]))

			tnodeid=[]; tnodesubid=[]; props=[]; value=[]; t=[]; count=0
			for entry in ch_id:
				if 'Time' not in ch_id[entry]:
					prop_node=ch_id[entry].split()
					prop,node=prop_node[0],prop_node[1]
					if prop!='VOLT':
						tnodesubid.extend([prop_node[-1][prop_node[-1].find(']')+1::].strip()]*\
						len(ch_data[entry][0::stride]))
						node=node[0:node.find('[')].strip()
					else:
						tnodesubid.extend(['']*len(ch_data[entry][0::stride]))
					value.extend(ch_data[entry][0::stride])
					props.extend([prop]*len(ch_data[entry][0::stride]))
					tnodeid.extend([node]*len(ch_data[entry][0::stride]))
					count+=1

			t.extend(ch_data['time'][0::stride]*count)

			df=pd.DataFrame(columns=['scenario','t','tnodeid','tnodesubid','dfeederid','dnodeid','property',
			'value'])
			df['t'],df['tnodeid'],df['tnodesubid'],df['property'],df['value']=t,tnodeid,tnodesubid,props,value
			df['scenario']=[scenario]*len(t)
			df=df.append(df_monitorData,ignore_index=True,sort=True)

			fpath=os.path.join(outputConfig['outputDir'],'df_pickle.pkl')
			df.to_pickle(fpath)

			return df
		except:
			raise