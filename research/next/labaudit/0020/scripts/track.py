# 2D tracks of jar (white) and toy (yellow) in o, s, x renders; prints centroids per frame
import cv2, numpy as np, json, sys
d='/home/user/quantiphy-challenge/research/next/labaudit/0020/'
def masks(im,pref):
    hsv=cv2.cvtColor(im,cv2.COLOR_BGR2HSV).astype(int)
    h,s,v=hsv[...,0],hsv[...,1],hsv[...,2]
    yel=(h>=18)&(h<=40)&(s>80)&(v>110)
    wht=(s<45)&(v>200)
    if pref=='x':
        b,g,r=[im[...,k].astype(int) for k in range(3)]
        green=(g>150)&(r<130)&(b<130)
        yel&=~green; wht&=~green
    wht[:, 850:]=0; wht[640:,:]=0
    return yel.astype(np.uint8),wht.astype(np.uint8)
def blob(m,prev,maxd=90,minarea=40):
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    best=None
    for k in range(1,n):
        if st[k,4]<minarea: continue
        dd=np.hypot(*(cen[k]-prev)) if prev is not None else 0
        if dd>maxd: continue
        sc=st[k,4]-2*dd
        if best is None or sc>best[0]: best=(sc,k)
    if best is None: return None
    k=best[1]; return [float(cen[k][0]),float(cen[k][1]),int(st[k,4]),int(st[k,2]),int(st[k,3])]
out={}
for pref in ['','s','x']:
    tj={}; tt={}
    pj=np.array([306.,510.]); pt=np.array([648.,136.])
    for i in range(49):
        im=cv2.imread(d+f'frames/0020{pref}_f{i:02d}.png')
        y,w=masks(im,pref)
        bj=blob(w,pj,maxd=130); bt=blob(y,pt)
        if bj: pj=np.array(bj[:2]); tj[i]=bj
        if bt: pt=np.array(bt[:2]); tt[i]=bt
    out[pref or 'o']={'jar':tj,'toy':tt}
    print('render',pref or 'o')
    for i in range(9,30):
        print(i,'jar',[round(x,1) for x in tj[i]] if i in tj else None,'toy',[round(x,1) for x in tt[i]] if i in tt else None)
json.dump(out,open(d+'tracks.json','w'))
