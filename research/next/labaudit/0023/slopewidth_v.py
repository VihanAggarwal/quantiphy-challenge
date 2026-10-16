import cv2, numpy as np
from geo import *
from slope3d import board_model, hit_plane
H=0.0146
def vedges(fr,x):
    im=cv2.imread(f'frames/{fr}.png').astype(float); v=im[:,x-2:x+3].max(2).mean(1)
    hsv=cv2.cvtColor(cv2.imread(f'frames/{fr}.png'),cv2.COLOR_BGR2HSV).astype(float); s=hsv[:,x-2:x+3,1].mean(1)
    # find cover core: rows with s>=30 between 355 and 450
    rows=np.arange(355,450); core=rows[s[355:450]>=30]
    if len(core)<5: return None
    c0,c1=core.min(),core.max()
    vc=np.median(v[c0:c1+1])
    # top: board white above cover; walk up from c0 while v < (white+vc)/2
    white=np.max(v[c0-10:c0]); t=(white+vc)/2; j=c0
    while v[j]<t and j>c0-10: j-=1
    ytop=j+(v[j]-t)/(v[j]-v[j+1]) if v[j]!=v[j+1] else j
    # bottom: cover -> page block (darker grey); walk down from c1 while v > (vc+page)/2
    page=np.min(v[c1:c1+10]); t2=(vc+page)/2; k=c1
    while v[k]>t2 and k<c1+10: k+=1
    ybot=k-1+(v[k-1]-t2)/(v[k-1]-v[k])
    return ytop,ybot
for route in ['ruler','stated']:
    M=board_model(route); p0=M['B']+M['n']*H; allw=[]
    for fr in ['o22','o23','o24','o25','o26','o27','x26','x27']:
        W=[]
        for x in range(550,635,10):
            e=vedges(fr,x)
            if e is None: continue
            A=hit_plane(p0,M['n'],x,e[0]); B=hit_plane(p0,M['n'],x,e[1]); W.append(np.linalg.norm(A-B)*100)
        allw.append(np.median(W)); print(route,fr,'%.2f'%np.median(W),np.round(W,1).tolist())
    print(route,'median over frames %.2f'%np.median(allw))
