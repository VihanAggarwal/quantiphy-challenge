import json,numpy as np
cx,cy=640.0,360.0; D=0.040
Ww=json.load(open('wrow.json')); Wt=json.load(open('wtop.json'))
ks=np.arange(36,49); c=ks+2; t=c/25.
x=np.array([Ww[str(k)][1][0] for k in ks]); yrow=np.array([Ww[str(k)][1][1] for k in ks]); d=np.array([2*Ww[str(k)][1][2] for k in ks])
ytop=np.array([Wt[str(k)]['ytop'] for k in ks])
good=~np.isin(ks,[41,42,43])
# smooth d with quadratic in t
pd=np.polyfit(t,d,2); ds=np.polyval(pd,t)
print('d resid',(d-ds).round(2))
yc_top=ytop+ds/2
print('yc from top+R',yc_top.round(2)); print('yc row      ',yrow.round(2))
for name,yc,m in [('row',yrow,np.ones_like(good)),('top+R',yc_top,good)]:
    s,b=np.polyfit(d[m],yc[m],1)
    print(name,'regression yc = %.3f d + %.2f  -> y_h=%.1f, hc=%.4f m'%(s,b,b,s*D))
# ToF anchor: capture 38 = video 36 centre range 1.373 (surface 1.353 + r)
def run(f,yh,ycsel,label):
    yc=ycsel
    r=np.c_[(x-cx)/f,(yc-cy)/f,np.ones_like(x)]
    Rc=1.353+0.02
    Z38=Rc/np.linalg.norm(r[0])
    # size route
    Zs=Z38*ds[0]/ds if False else Z38*d[0]/d
    Zs_sm=Z38*ds[0]/ds
    # plane route (zero roll): Z = hc*f/(y-yh) anchored at frame 0 via smoothed fit
    Zp=(yc[0]-yh)*Z38/(yc-yh)
    outs=[]
    for nm,Z in [('size-raw',Zs),('size-smooth',Zs_sm),('plane',Zp)]:
        P=Z[:,None]*r
        i40=2; i41=3
        raw=np.linalg.norm(P[i41]-P[i40])*2500
        fits=[]
        for lo,hi,deg in [(38,44,1),(38,46,2),(38,50,2),(38,50,1)]:
            mm=(c>=lo)&(c<=hi)&(good if nm=='plane' and label=='top+R' else True)
            V=np.array([np.polyval(np.polyder(np.polyfit(t[mm],P[mm,j],deg)),40.5/25) for j in range(3)])*100
            fits.append('%d-%d/%d:%.1f[vx%.1f vz%.1f]'%(lo,hi,deg,np.linalg.norm(V),V[0],V[2]))
        outs.append('%s raw=%.1f '%(nm,raw)+' '.join(fits))
    print('f=%d yh=%.0f yc=%s Z38=%.4f'%(f,yh,label,Z38)); [print('   ',o) for o in outs]
for f in [711,770]:
    for yh in [348,351,355,360]:
        run(f,yh,yrow,'row')
        run(f,yh,yc_top,'top+R')
