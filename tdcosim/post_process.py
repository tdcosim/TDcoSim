from __future__ import division
import os
import string
import json
import pdb

import xlsxwriter

from tdcosim.global_data import GlobalData


class PostProcess(object):
#===================================================================================================
	def __init__(self):
		super().__init__()
		return None

#===================================================================================================
	def generate_report(self,simData,fname=None,sim=None):
		try:
			# defaults
			if not fname:
				fname=os.path.join(simData.config['outputConfig']['outputDir'],
				'report_{}.xlsx'.format(simData.config['outputConfig']['simID']))
			if not sim:
				sim=simData.config['simulationConfig']['simType']

			wb=xlsxwriter.Workbook(fname)
			bold=wb.add_format({'bold':True})
			red=wb.add_format({'font_color':'red'})
			data=simData.data

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
			for t in simData.data['monitorData']:
				for node in simData.data['monitorData'][t]:
					if node not in ws:
						ws[node]=wb.add_worksheet('feeder_{}'.format(node))

			t=simData.data['monitorData'].keys()
			t.sort()
			colMap={}; colMap['time']=0
			for node in simData.data['monitorData'][t[0]]:
				ws[node].write(0,0,'time')
				count=1
				items=simData.data['monitorData'][t[0]][node].keys()
				items.sort()
				for item in items:
					if item.lower()=='vmag' or item.lower()=='vang':
						for distNode in simData.data['monitorData'][t[0]][node][item].keys():
							for phase in ['a','b','c']:
								colName=item.lower()+'_{}_{}'.format(distNode,phase)
								ws[node].write(0,count,colName)
								colMap[colName]=count
								count+=1
					elif item.lower()=='der':
						for distNode in simData.data['monitorData'][t[0]][node][item].keys():
							for varName in ['P','Q']:
								colName=item.lower()+'_{}_{}'.format(distNode,varName)
								ws[node].write(0,count,colName)
								colMap[colName]=count
								count+=1

			row=1
			for entry in t:# write data
				for node in simData.data['monitorData'][entry]:
					ws[node].write(row,colMap['time'],entry)
					for item in simData.data['monitorData'][entry][node]:
						if item.lower()=='vmag' or item.lower()=='vang':
							for distNode in simData.data['monitorData'][entry][node][item].keys():
								for phase in ['a','b','c']:
									colName=item.lower()+'_{}_{}'.format(distNode,phase)
									if phase in simData.data['monitorData'][entry][node][item][distNode]:
										ws[node].write(row,colMap[colName],
										simData.data['monitorData'][entry][node][item][distNode][phase])
						elif item.lower()=='der':
							for distNode in simData.data['monitorData'][entry][node][item].keys():
								for varName in ['P','Q']:
									colName=item.lower()+'_{}_{}'.format(distNode,varName)
									if varName in simData.data['monitorData'][entry][node][item][distNode]:
										ws[node].write(row,colMap[colName],
										simData.data['monitorData'][entry][node][item][distNode][varName])
				row+=1# increase counter at every t

			wb.close()
		except:
			print("Unexpected error:", sys.exc_info()[0])
			GlobalData.log(msg='Failed to generate report')

#===================================================================================================
	def generate_dataframe(self,simData,scenarioid='1'):
		try:
			data=simData.data
			df=pd.DataFrame(columns=['scenario','t','tnodeid','dfeederid','dnodeid','property',
			'value'])

			t_all=list(data['TNet']['Dynamic'].keys())
			t_all.sort()
			t=[]; tnodeid=[]; dfeederid=[]; dnodeid=[]; prop=[]; val=[]

			for thisT in t_all:
				for node in data['TNet']['Dynamic'][thisT]['S']:
					t.append(thisT)
					val.append(data['TNet']['Dynamic'][thisT]['S'][node]['P'])
					prop.append('P')
					tnodeid.append(node)
					t.append(thisT)
					val.append(data['TNet']['Dynamic'][thisT]['S'][node]['Q'])
					prop.append('Q')
					tnodeid.append(node)
					t.append(thisT)
					val.append(data['TNet']['Dynamic'][thisT]['V'][node])
					prop.append('Vmag')
					tnodeid.append(node)

			df.loc[:,'t']=t; df.loc[:,'tnodeid']=tnodeid
			df.loc[:,'property']=prop; df.loc[:,'value']=val
			df.loc[:,'scenario']=scenarioid
			df.t=df.t.map(lambda x:float(x))

			return df
		except:
			print("Unexpected error:", sys.exc_info()[0])



