import cv2, numpy as np, sys, json
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit2/0014/scripts')
from frames import load
T=json.load(open('/home/user/quantiphy-challenge/research/next/labaudit2/0014/track_bgdiff.json'))
for r in ['x','s']:
    fr=load(r); bg=np.median(np.stack([f.astype(np.float32) for f in fr[28:49]]),0)
    out=[]
    for k in [0,9,12,13,14,15,16]:
        u,v=T[r][k]['wcen']
        d=np.abs(fr[k].astype(np.float32)-bg).sum(2)
        ws=[]
        for dy in range(-3,4):
            y=int(round(v))+dy
            row=d[y,int(u)-30:int(u)+30]
            mx=np.percentile(row,95); half=mx/2
            idx=np.nonzero(row>half)[0]
            if len(idx): 
                i0,i1=idx[0],idx[-1]
                l=i0-1+(half-row[i0-1])/(row[i0]-row[i0-1]); rr=i1+(row[i1]-half)/(row[i1]-row[i1+1])
                ws.append(rr-l)
        w=np.median(ws); out.append((k,round(w,1)))
    print(r,out)
    for k,w in out:
        if k in (0,): print('  f0 width',w,'-> D at 1.818 (surface) ~', round(100*w*(1.818+0.033)/711,2),'(centre range) /',round(100*w*1.818/711,2))
        if k==14: print('  f14 width',w,'-> D at 1.7288 surface',round(100*w*1.7288/711,2),' centre-range',round(100*w*(1.7288+0.033)/711,2))
