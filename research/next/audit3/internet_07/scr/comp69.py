import numpy as np
W='/home/user/quantiphy-challenge/research/next/audit3/internet_07/'
cam=np.loadtxt(W+'cam69t.txt'); cf=cam[:,0]
# drop frame 73 outlier (narrow xr, k~0) 
ok=~np.isin(cf,[73])
cf=cf[ok]; tx=cam[ok,1]; k=cam[ok,3]
def smooth(y,x,h=2):
    out=[]
    for xi in x:
        m=np.abs(cf-xi)<=h
        out.append(np.median(y[m]))
    return np.array(out)
fps=30.013
e=np.loadtxt(W+'edges69.txt'); f=e[:,0]
mid=(e[:,1]+e[:,2])/2
b=np.loadtxt(W+'tr69b.txt'); hb=dict(zip(b[:,0],b[:,3])); kb=dict(zip(b[:,0],b[:,5]))
h69=np.array([hb.get(v,np.nan) for v in f]); k66=np.array([kb.get(v,np.nan) for v in f])
for hs in (0,1,2,3):
    TX=smooth(tx,f,hs) if hs else np.interp(f,cf,tx); K=smooth(k,f,hs) if hs else np.interp(f,cf,k)
    print('--- camera smoothing half-window',hs)
    for name,x in (('mid',mid),('handleTM',h69),('knotTM',k66)):
        xc=(x-TX-960)/(1+K)+960
        row=[]
        for lo,hi in ((60,75),(62,75),(62,72),(63,72),(60,72),(62,77),(66,76)):
            for lab,xx in (('raw',x),('comp',xc)):
                m=(f>=lo)&(f<=hi)&np.isfinite(xx)
                t=f[m]/fps; c=np.polyfit(t,xx[m],2)
                row.append('%s %d-%d %5.0f'%(lab,lo,hi,2*c[0]))
        print(name,' | '.join(row))
TX=smooth(tx,f,2); K=smooth(k,f,2)
print('camera shift at mid position (px):',dict(zip(f.astype(int),np.round(TX+K*(mid-960),1))))
