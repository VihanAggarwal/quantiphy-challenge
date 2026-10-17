import numpy as np
W='/home/user/quantiphy-challenge/research/next/audit3/internet_07/'
fps=30.013
cam=np.loadtxt(W+'cam69t.txt'); ok=~np.isin(cam[:,0],[73]); cf=cam[ok,0]; tx=cam[ok,1]; k=cam[ok,3]
def sm(y,x,h=2): return np.array([np.median(y[np.abs(cf-xi)<=h]) for xi in x])
e=np.loadtxt(W+'edges69.txt'); hh=np.loadtxt(W+'hh69.txt')
routes={'A_mid':(e[:,0],(e[:,1]+e[:,2])/2),'B_handle':(hh[:,0],hh[:,2])}
cur={'h':10.5,'v20':0.3497,'v21':0.3789,'v22':0.4081,'v23':0.4373,'d1':3.652,'d2':8.126,'d3':9.313}
Hpx=(530,545,561)
rows=[]
for comp in (False,True):
    for rn,(fr,x) in routes.items():
        x=x.copy()
        if comp: x=(x-sm(tx,fr)-960)/(1+sm(k,fr))+960
        for lo,hi in ((62,72),(62,73),(63,73),(62,75)):
            m=(fr>=lo)&(fr<=hi)&np.isfinite(x); t=fr[m]/fps; c=np.polyfit(t,x[m],2); a=2*c[0]
            s=0.32/a
            v=[np.polyval(np.polyder(c),T)*s for T in (2.0,2.1,2.2,2.3)]
            X=lambda T: np.polyval(c,T)
            d=[(X(2.1)-X(2.0))*s*100,(X(2.3)-X(2.1))*s*100,(X(2.5)-X(2.3))*s*100]
            h=Hpx[1]*s*100
            vals=dict(h=h,v20=v[0],v21=v[1],v22=v[2],v23=v[3],d1=d[0],d2=d[1],d3=d[2])
            rows.append((('comp' if comp else 'raw'),rn,lo,hi,a,vals))
            print('%-4s %-8s %d-%d a=%5.0f  h=%.2f v=%.3f %.3f %.3f %.3f d=%.2f %.2f %.2f | ratio cur/this v20 %.2f d1 %.2f h %.2f'%(
                ('comp' if comp else 'raw'),rn,lo,hi,a,h,*v,*d,cur['v20']/v[0],cur['d1']/d[0],cur['h']/h))
