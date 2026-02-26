function res=get_mpc(field,column_name,row_index)
% Input:
% field -- bus, branch, gen, etc.
% column_name -- name of the column within the field, ex, vm for bus.vm.
% row_index (optional) -- when provided will return only the row/rows index requested. Can be a scalar or an array.
% sample call:
% vm=get_mpc('bus','vm')
% vm5=get_mpc('bus','vm',5)

global mpc
global c

if nargin==3
	res=mpc.(field)(row_index,c.(field).(column_name));
else
	res=mpc.(field)(:,c.(field).(column_name));
end
