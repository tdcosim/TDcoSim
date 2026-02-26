function res=run_mpc(alg)
global mpc

if strcmpi(alg,'runpf')
	mpc=runpf(mpc);
elseif strcmpi(alg,'rundcpf')
	mpc=rundcpf(mpc);
elseif strcmpi(alg,'runopf')
	mpc=runopf(mpc);
elseif strcmpi(alg,'rundcopf')
	mpc=rundcpf(mpc);
end

res.success=1;
