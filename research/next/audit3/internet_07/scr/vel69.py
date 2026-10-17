import numpy as np
W='/home/user/quantiphy-challenge/research/next/audit3/internet_07/'
cam=np.loadtxt(W+'cam69t.txt'); ok=~np.isin(cam[:,0],[73]); cf=cam[ok,0]; tx=cam[ok,1]; k=cam[ok,3]
def sm(y,x,h=2): return np.array([np.median(y[np.abs(cf-xi)<=h]) for xi in x])
fps=30.013
e=np.loadtxt(W+'edges69.txt'); f=e[:,0]; mid=(e[:,1]+e[:,2])/2
b=np.loadtxt(W+'tr69b.txt'); 
tracks={'mid':(f,mid)}
for j,n in ((2,'h63'),(3,'h69'),(4,'h75'),(5,'k66')):
    tracks[n]=(b[:,0],b[:,j])
def vel(fr,x,fc,h=3):
    m=(np.abs(fr-fc)<=h)&np.isfinite(x)
    t=(fr[m]-fc)/fps; c=np.polyfit(t,x[m],2); return c[1], 2*c[0]
for comp in (False,True):
    print('==== camera compensated' if comp else '==== raw')
    for n,(fr,x) in tracks.items():
        x=x.copy()
        if comp:
            TX=sm(tx,fr); K=sm(k,fr); x=(x-TX-960)/(1+K)+960
        g=dict(zip(fr,x))
        # positions at 0.1 s grid
        P={fc:g.get(fc,np.nan) for fc in (60,63,66,69,72,75)}
        vs={}
        for fc in (60,63,66,69):
            h=3
            if n=='mid' and fc==60: vs[fc]=np.nan; continue
            vs[fc]=vel(fr,x,fc,h)[0]
        a_inst=(vs[69]-vs[60])/0.3 if np.isfinite(vs[60]) else (vs[69]-vs[63])/0.2
        # global quadratic fit 60-72 (or 61-72 for mid)
        lo=61 if n=='mid' else 59
        m=(fr>=lo)&(fr<=72)&np.isfinite(x); t=fr[m]/fps; c=np.polyfit(t,x[m],2)
        vq=np.polyval(np.polyder(c),[60/fps,63/fps,66/fps,69/fps])
        d=[P[63]-P[60],P[69]-P[63],P[75]-P[69]]
        # forward-difference velocity convention
        print('%-4s v_loc(60,63,66,69)=%s  a_loc=%.0f | quad%d-72 a=%.0f v=%s | disp(2.0-2.1,2.1-2.3,2.3-2.5)=%s  fwd a=(d23_24-d20_21)/.03=%s'%(
            n,np.round([vs[60],vs[63],vs[66],vs[69]],0),a_inst,lo,2*c[0],np.round(vq,0),np.round(d,1),
            np.round((g.get(72,np.nan)-g.get(69,np.nan)-(P[63]-P[60]))/0.03,0)))
