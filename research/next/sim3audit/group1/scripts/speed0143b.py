import json, numpy as np
yh=540.4; cx=959.6
d=json.load(open('scripts/simulation_0143_t2.json'))
top=np.array([o['top'] for o in d],float); xt=np.array([o['xt'] for o in d])
pk=np.array([0,12,25,37,49,62,75,87,98])
# refine peak frames: local min of top within +-3
ref=[]
for p in pk:
    lo,hi=max(0,p-3),min(99,p+3); seg=top[lo:hi+1]; m=seg.min(); idx=np.nonzero(seg==m)[0]+lo; ref.append(idx.mean())
ref=np.array(ref); print('peak frames',ref)
for f in [1723, 1776, 1890]:
    Hc=1.8/1.40; K=f*Hc
    Zp=np.array([K*0.40/(yh-np.interp(r,np.arange(100),top)) for r in ref])
    Xp=np.array([(np.interp(r,np.arange(100),xt)-cx)*z/f for r,z in zip(ref,Zp)])
    tp=ref/24
    seg=np.hypot(np.diff(Zp),np.diff(Xp)); s=np.concatenate([[0],np.cumsum(seg)])
    # stride means (2 steps) centred
    sm=[(round((tp[i]+tp[i+2])/2,2), round((s[i+2]-s[i])/(tp[i+2]-tp[i]),2)) for i in range(len(tp)-2)]
    # polynomial fit of s(t) (cubic), excluding first sample (turning start)
    c=np.polyfit(tp,s,3); dc=np.polyder(c); ddc=np.polyder(dc)
    print('f',f,'stride means',sm)
    print('    cubic: v(1)=%.2f v(2)=%.2f a(2.5)=%.2f  mean v 1-3.5s=%.2f'%(np.polyval(dc,1),np.polyval(dc,2),np.polyval(ddc,2.5),(s[-2]-s[1])/(tp[-2]-tp[1])))
