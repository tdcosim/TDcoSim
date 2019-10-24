import sys
import linecache
import pdb

import numpy as np
from scipy.integrate import ode

from tdcosim.model.opendss.opendss_data import OpenDSSData
from tdcosim.model.opendss.model.pvderaggregation.procedure.pvder_procedure import PVDERProcedure


class PVDERAggregatedModel:
    def __init__(self):         
        OpenDSSData.data['DNet']['DER'] = {}
        OpenDSSData.data['DNet']['DER']['PVDERData'] = {}
        OpenDSSData.data['DNet']['DER']['PVDERMap'] = {}                
        self._pvders = {}


    def setup(self, S0, V0):
        try:
            # set the random number seed
            
            randomSeed = 2500             
            np.random.seed(randomSeed)

            #Set Default Values      
            # each pvder produces 46 kw at pf=1
            OpenDSSData.data['DNet']['DER']['PVDERData']['PNominal'] = OpenDSSData.config['myconfig']['DERParameters']['power_rating'] * OpenDSSData.config['myconfig']['DERParameters']['pvderScale']
            OpenDSSData.data['DNet']['DER']['PVDERData']['QNominal'] = 0 * OpenDSSData.config['myconfig']['DERParameters']['pvderScale']

            rating=0 # rating will be in kVA as Default
            for entry in S0['P']:
                if OpenDSSData.config['myconfig']['DERParameters']['solarPenetrationUnit']=='kva':
                    rating+=abs(S0['P'][entry]+S0['Q'][entry]*1j)
                elif OpenDSSData.config['myconfig']['DERParameters']['solarPenetrationUnit']=='kw':
                    rating+=S0['P'][entry]
            # number of 50 kVA solar installtions required            
            nSolar=int(np.ceil((rating/OpenDSSData.data['DNet']['DER']['PVDERData']['PNominal'])*OpenDSSData.config['myconfig']['solarPenetration']))            

            # create instances of pvder            
            for n in range(nSolar):
                self._pvders[n]=PVDERProcedure()
           
            # find all three phase nodes
            threePhaseNode=[]
            for node in V0:
                count=0
                for phase in V0[node]:
                    count+=1
                if count==3 and node not in OpenDSSData.config['myconfig']['DERParameters']['avoidNodes']: # three phase node
                    threePhaseNode.append(node)

            # now map each solar to the available nodes            
            nThreePhaseNode=len(threePhaseNode)
            for entry in self._pvders:
                thisKey=threePhaseNode[np.random.randint(0,nThreePhaseNode)]
                if thisKey not in OpenDSSData.data['DNet']['DER']['PVDERMap']:
                    OpenDSSData.data['DNet']['DER']['PVDERMap'][thisKey]={}
                    OpenDSSData.data['DNet']['DER']['PVDERMap'][thisKey]['nSolar_at_this_node']=0
                OpenDSSData.data['DNet']['DER']['PVDERMap'][thisKey][OpenDSSData.data['DNet']['DER']['PVDERMap'][thisKey]['nSolar_at_this_node']]=entry
                OpenDSSData.data['DNet']['DER']['PVDERMap'][thisKey]['nSolar_at_this_node']+=1
                self._pvders[entry].setup(thisKey,V0[thisKey])  #Pass both node id and node voltage during DER setup

            for entry in OpenDSSData.data['DNet']['DER']['PVDERMap']:
                thisNode=OpenDSSData.data['DNet']['DER']['PVDERData'][entry]={}
                thisNode['Vmag']={}

            self.pvIDIndex=self._pvders.keys() # index for variables based on ID
            self.pvIDIndex.sort()# sort the index and use this as the order

            y0=[]; t0=0.0
            for n in range(len(self.pvIDIndex)):
                y0.extend(self._pvders[self.pvIDIndex[n]]._pvderModel.lastSol)

            self.integrator=ode(self.funcval,self.jac).set_integrator('vode',method='bdf',rtol=1e-4,atol=1e-4)
            self.integrator.set_initial_value(y0,t0)

            return OpenDSSData.data['DNet']['DER']['PVDERMap']
        except Exception as e:
            OpenDSSData.log("Failed Setup PVDERAGG")


    def funcval(self,t,y,nEqs=23):
        fvalue=[]
        for n in range(len(self.pvIDIndex)):
            fvalue.extend(self._pvders[self.pvIDIndex[n]]._pvderModel.sim.ODE_model(y[n*nEqs:(n+1)*nEqs],t))
        return fvalue

    def jac(self,t,y,nEqs=23):
        nPVDER=len(self.pvIDIndex)
        J=np.zeros((nPVDER*nEqs,nPVDER*nEqs))# zero out at every call to avoid stray values
        for n in range(nPVDER):
            thisJ=self._pvders[self.pvIDIndex[n]]._pvderModel.sim.jac_ODE_model(y,t)
            row,col=np.where(thisJ)
            J[n*nEqs+row,n*nEqs+col]=thisJ[thisJ!=0]
        return J

    def run(self, V,nEqs=23,dt=1/120.):
        try:
            P = {}
            Q = {}
            # prerun for all pvder instances at this node
            for node in OpenDSSData.data['DNet']['DER']['PVDERMap']:# compute solar injection at each node
                lowSideNode='{}_tfr'.format(node)
                Va = V[lowSideNode]['a']
                Vb = V[lowSideNode]['b']
                Vc = V[lowSideNode]['c']

                for pv in OpenDSSData.data['DNet']['DER']['PVDERMap'][node]:
                    if pv!='nSolar_at_this_node':
                        pvID=OpenDSSData.data['DNet']['DER']['PVDERMap'][node][pv]                        
                        thisPV=self._pvders[pvID]
                        thisPV.prerun(Va,Vb,Vc)

            # single large integrator for all pvder instances
            y=self.integrator.integrate(self.integrator.t+dt)

            # postrun for all pvder instances
            for node in OpenDSSData.data['DNet']['DER']['PVDERMap']:# compute solar injection at each node
                sP=0; sQ=0
                for pv in OpenDSSData.data['DNet']['DER']['PVDERMap'][node]:
                    if pv!='nSolar_at_this_node':
                        pvID=OpenDSSData.data['DNet']['DER']['PVDERMap'][node][pv]
                        assert pvID in self.pvIDIndex, "pvID not found in self.pvIDIndex"
                        thisPV=self._pvders[pvID]
                        n=self.pvIDIndex.index(pvID)
                        sol=np.append(thisPV._pvderModel.lastSol,y[n*nEqs:(n+1)*nEqs])
                        sol=sol.reshape((-1,nEqs))
                        val=thisPV.postrun(sol,[self.integrator.t-dt,self.integrator.t])
                        sP-=val.real# -ve load => generation
                        sQ-=val.imag
                P[node] = sP
                Q[node] = sQ
                OpenDSSData.data['DNet']['DER']['PVDERData'][node]['Vmag']['a']=Va
                OpenDSSData.data['DNet']['DER']['PVDERData'][node]['Vmag']['b']=Vb
                OpenDSSData.data['DNet']['DER']['PVDERData'][node]['Vmag']['c']=Vc
            
            return P, Q

        except Exception as e:
            OpenDSSData.log("Failed run the pvder aggregated model")
            OpenDSSData.log(e)
            

