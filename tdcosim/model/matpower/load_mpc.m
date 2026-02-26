function res=load_mpc(casename)
global mpc
%####
casename
mpc=loadcase(casename);

res.success=1;
