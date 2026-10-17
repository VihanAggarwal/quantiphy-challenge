import json,numpy as np,sys
D=json.load(open('/home/user/quantiphy-challenge/research/next/audit3/internet_07/remeasure/linefit.json'))
fr=np.array(D['fr']); c=np.array(D['c'],float); cR=np.array(D['cR']); cL=np.array(D['cL'],float)
fps=30.
tracks={'c(62+)':np.where(fr>=62,c,np.nan),'c62+&cR<62':np.where(fr>=62,c,cR),'cR':cR,'cL':np.where(fr>=62,cL,np.nan)}
def fit(x,deg,lo,hi):
    m=(fr>=lo)&(fr<=hi)&~np.isnan(x)
    t=(fr[m]-65)/fps; p=np.polyfit(t,x[m],deg)
    return p,np.sqrt(np.sum((x[m]-np.polyval(p,t))**2)/(m.sum()-deg-1))
for name,x in tracks.items():
    print('==',name)
    print('  disp',' '.join('%.1f'%v for v in np.diff(x)))
    for deg,lo,hi in ((2,56,72),(2,58,72),(2,60,70),(3,56,79),(3,58,76),(3,60,79),(4,55,79),(2,62,72),(3,62,79)):
        p,rms=fit(x,deg,lo,hi); dp=np.polyder(p)
        v=np.array([np.polyval(dp,(f-65)/fps) for f in (60,63,66,69)])
        P=lambda f: np.polyval(p,(f-65)/fps)
        dv=v[3]-v[0]; Rr=v/dv
        print('  deg%d %d-%d rms %.2f v0 %.0f dv %.0f a %.0f R %s | disp/dv(s): %.4f %.4f %.4f'%(deg,lo,hi,rms,v[0],dv,dv/.3,np.round(Rr,3),(P(63)-P(60))/dv,(P(69)-P(63))/dv,(P(75)-P(69))/dv))
