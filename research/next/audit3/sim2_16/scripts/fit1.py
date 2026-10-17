import numpy as np,sys
v=sys.argv[1]; a0=int(sys.argv[2]); a1=int(sys.argv[3])
T=np.load('/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/%s_tracks.npy'%v)
fps=24.
idx=np.arange(a0,a1)
t=idx/fps
for name,col in [('cx',4),('x0',0),('x1',2),('mid',None)]:
    y=T[idx,col] if col is not None else (T[idx,0]+T[idx,2])/2
    p=np.polyfit(t,y,2); r=y-np.polyval(p,t)
    print(name,'a=%.2f px/s2'%(2*p[0]),'rms %.3f'%r.std(),'t0 vertex %.3f'%(-p[1]/(2*p[0])))
