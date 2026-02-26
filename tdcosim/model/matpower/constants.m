function c=constants()

busHeader={"bus_id","type","pd","qd","gs","bs","area","vm","va","basekv","zone","vmax","vmin"};
branchHeader={"fbus","tbus","r","x","b","rateA","rateB","rateC","ratio","angle","status","angmin","angmax"};
genHeader={"bus","Pg","Qg","Qmax","Qmin","Vg","mBase","status","Pmax","Pmin","Pc1","Pc2","Qc1min","Qc1max","Qc2min","Qc2max","ramp_agc","ramp_10","ramp_30","ramp_q","apf"};
gencostHeader={"startup","shutdown","n","c2","c1","c0"};

c=struct();
c.bus=struct();

for n=1:length(busHeader)
	c.bus.(busHeader{n})=uint8(n);
end

for n=1:length(branchHeader)
	c.branch.(branchHeader{n})=uint8(n);
end

for n=1:length(genHeader)
	c.gen.(genHeader{n})=uint8(n);
end

for n=1:length(gencostHeader)
	c.gencost.(gencostHeader{n})=uint8(n);
end
