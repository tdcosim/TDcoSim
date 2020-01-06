from __future__ import division
import string
import json
import pdb

import xlsxwriter


def generateReport(GlobalData,fname='report.xlsx',sim='dynamic'):
    wb=xlsxwriter.Workbook(fname)    
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


