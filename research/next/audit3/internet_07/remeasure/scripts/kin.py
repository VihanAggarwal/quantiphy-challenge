import json,numpy as np
C=json.load(open('/home/user/quantiphy-challenge/research/next/audit3/internet_07/remeasure/centers.json'))
fr=np.arange(55,80)
def track(b):
    c=np.array(C[b]['c']); cR=np.array(C[b]['cR'])
    x=np.where(np.isnan(c),cR,c); return x
X={b:track(b) for b in ('lo','lo2')}
X['avg']=(X['lo']+X['lo2'])/2
fps=30.0
def polyv(x,frames,deg,lo,hi):
    m=(frames>=lo)&(frames<=hi)
    t=(frames[m]-65)/fps
    p=np.polyfit(t,x[m],deg); dp=np.polyder(p)
    res=x[m]-np.polyval(p,t)
    return p,dp,np.sqrt(np.mean(res**2))
targets=[60,63,66,69]
for b,x in X.items():
    print('==',b)
    d=np.diff(x); print(' per-frame disp:',' '.join('%d:%.1f'%(i,v) for i,v in zip(fr[1:],d)))
    for deg,lo,hi in ((2,57,72),(2,58,70),(3,56,76),(3,57,79),(4,55,79),(2,60,69),(3,59,72)):
        p,dp,rms=polyv(x,fr,deg,lo,hi)
        v=[np.polyval(dp,(f-65)/fps) for f in targets]
        pos=lambda f: np.polyval(p,(f-65)/fps)
        a=(v[3]-v[0])/0.3
        print(' deg%d %d-%d rms %.2f  v(px/s) %s  a_avg %.0f  -> v_m/s %s  disp(px) 60-63 %.1f 63-69 %.1f 69-75 %.1f'%(deg,lo,hi,rms,np.round(v,0),a,np.round(np.array(v)*0.32/a,4),pos(63)-pos(60),pos(69)-pos(63),pos(75)-pos(69)))
