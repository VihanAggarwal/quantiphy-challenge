import json,numpy as np
D=json.load(open('/home/user/quantiphy-challenge/research/next/audit3/internet_07/remeasure/linefit.json'))
fr=np.array(D['fr']); c=np.array(D['c'],float); R=np.array(D['R'])
# center track: c for >=61, frames 59,60 from R - w_lin/2
w61=R[fr==61][0]-np.array(D['L'])[fr==61][0]
cc=c.copy()
for i in (59,60):
    k=np.where(fr==i)[0][0]
    x=R[k]-230
    for _ in range(10): x=R[k]-(w61+(x-c[fr==61][0])*(-0.056))/2
    cc[k]=x
print('c59,c60',cc[fr==59],cc[fr==60])
# marker deltas rel frame 100 (template matching results)
dL={55:5.06,56:4.98,57:5.52,59:4.02,67:0.67,68:0.66,69:0.09,70:-0.35,71:-0.83,72:-1.17,73:-1.47,74:-1.79,75:-2.02,76:-2.02,77:-2.03,78:-2.03,79:-1.69,80:-1.41,81:-0.67,82:0.16}
dR0={55:-0.14,56:-0.09,57:-0.17,58:0.12,59:0.06,60:0.0,61:0.17,62:0.27,63:0.80,64:0.94,65:1.16,66:1.68,67:2.06,68:2.47,69:3.09,70:3.07,71:3.39,72:3.72,73:4.08,75:4.71,81:0.35,82:-0.68}
dR={k:v+5.72 for k,v in dR0.items()}
F=np.arange(55,83)
def interp(d):
    ks=np.array(sorted(d)); vs=np.array([d[k] for k in ks]); return np.interp(F,ks,vs)
L1=interp(dL); R1=interp(dR)
# variant 2: fixed zoom centre model for L gap (60-66) using R: dL = dL57 - mu*(xc-410), mu=(dR-dR57)/(1580-xc)
xc=1130.; base_L=np.mean([5.06,4.98,5.52,4.02]); base_R=np.mean([dR[k] for k in (55,56,57,58,59)])
L2=L1.copy()
for j,f in enumerate(F):
    if 60<=f<=66:
        mu=(R1[j]-base_R)/(1580-xc); L2[j]=base_L-mu*(xc-410)
R2=R1.copy()
for j,f in enumerate(F):
    if f in (74,76,77,78,79,80):
        # mu from L: dL = base_L - mu*(xc-410)
        mu=(base_L-L1[j])/(xc-410); R2[j]=base_R+mu*(1580-xc)
for j,f in enumerate(F): print(f,'L1 %.2f R1 %.2f | L2 %.2f R2 %.2f'%(L1[j],R1[j],L2[j],R2[j]))
fps=30.
def kin(x,lo,hi,deg):
    m=(fr>=lo)&(fr<=hi)&~np.isnan(x); t=(fr[m]-65)/fps; p=np.polyfit(t,x[m],deg); dp=np.polyder(p)
    v=np.array([np.polyval(dp,(f-65)/fps) for f in (60,63,66,69)]); P=lambda f: np.polyval(p,(f-65)/fps)
    rms=np.sqrt(np.sum((x[m]-np.polyval(p,t))**2)/(m.sum()-deg-1))
    dv=v[3]-v[0]
    return rms,v,dv,np.array([P(63)-P(60),P(69)-P(63),P(75)-P(69)])
res={}
for name,(Lm,Rm) in {'raw':(None,None),'zoom_lin':(L1,R1),'zoom_model':(L2,R2)}.items():
    x=cc.copy()
    if Lm is not None:
        for j,f in enumerate(fr):
            if np.isnan(x[j]): continue
            k=np.where(F==f)[0][0]
            d=Lm[k]+(Rm[k]-Lm[k])*(x[j]-410)/1170
            x[j]=x[j]-d
    print('==',name)
    for lo,hi,deg in ((59,72,2),(60,72,2),(61,72,2),(59,79,2),(59,79,3),(61,79,3),(59,75,2),(60,70,2)):
        rms,v,dv,disp=kin(x,lo,hi,deg)
        print('  %d-%d deg%d rms %.2f v %s dv %.0f a %.0f R %s disp/dv %s'%(lo,hi,deg,rms,np.round(v),dv,dv/.3,np.round(v/dv,3),np.round(disp/dv,4)))
    res[name]=x.tolist()
json.dump(dict(fr=fr.tolist(),**res),open('/home/user/quantiphy-challenge/research/next/audit3/internet_07/remeasure/tracks_final.json','w'))
