import numpy as np, sys
W='/home/user/quantiphy-challenge/research/next/audit3/sim2_04/'
i=int(sys.argv[1]); P=float(sys.argv[2]); nh=int(sys.argv[3]); n0=int(sys.argv[4]); n1=int(sys.argv[5])
r=np.loadtxt(W+f'trk_{i}.txt')
n=r[:,0]; sel=(n>=n0)&(n<=n1)&np.isfinite(r[:,1])
for name,col in [('xmin',1),('xmax',2),('cx',5),('bcx',None)]:
    y=(r[:,1]+r[:,2])/2 if col is None else r[:,col]
    nn=n[sel]; yy=y[sel]
    cols=[np.ones_like(nn),nn,nn**2]
    for k in range(1,nh+1):
        cols+= [np.sin(2*np.pi*k*nn/P), np.cos(2*np.pi*k*nn/P)]
    A=np.stack(cols,1)
    c,*_=np.linalg.lstsq(A,yy,rcond=None)
    res=yy-A@c
    a_pf=2*c[2]; a_ps=a_pf*576
    print(f'{name:5s} a={a_pf:.4f} px/f^2 = {a_ps:.1f} px/s^2  b={c[1]:.3f} vertex n={-c[1]/(2*c[2]):.2f} rms={res.std():.2f}')
