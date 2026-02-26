function res=set_mpc(field,column_name,value,row_index)
global mpc
global c

if nargin==4
	mpc.(field)(row_index,c.(field).(column_name))=value;
else
	mpc.(field)(:,c.(field).(column_name))=value;
end

res.success=1;
