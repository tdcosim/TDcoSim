function res=run_mpc(alg)
global mpc

tic

mpopt=mpoption;
mpopt.out.all=0;

if strcmpi(alg,'runpf')
	mpc=runpf(mpc,mpopt);
elseif strcmpi(alg,'rundcpf')
	mpc=rundcpf(mpc,mpopt);
elseif strcmpi(alg,'runopf')
	mpc=runopf(mpc,mpopt);
elseif strcmpi(alg,'rundcopf')
	mpc=rundcpf(mpc,mpopt);
end
toc

res.success=1;
