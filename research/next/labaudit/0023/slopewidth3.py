import cv2, numpy as np
from geo import *
from slope3d import board_model, hit_plane
H=0.0146
def cover_edges(fr,x,ylo,yhi):
    im=cv2.imread(f'frames/{fr}.png'); hsv=cv2.cvtColor(im,cv2.COLOR_BGR2HSV).astype(float)
    s=hsv[ylo:yhi,x-2:x+3,1].mean(1)
    smax=np.percentile(s,95); 
    k=np.argmax(s>=0.85*smax)  # inside cover
    # top: walk up from k until s < half of (smax + base_top)
    base_t=np.median(s[:max(3,k-12)]) if k>12 else s[:max(k,1)].min()
    t=(smax+base_t)/2; j=k
    while j>0 and s[j]>=t: j-=1
    ytop=ylo+j+(t-s[j])/(s[j+1]-s[j])
    # bottom: last index with s>=0.85smax then walk down
    kk=len(s)-1-np.argmax(s[::-1]>=0.85*smax)
    base_b=np.median(s[kk+6:kk+14]) if kk+14<len(s) else s[kk:].min()
    t2=(smax+base_b)/2; j=kk
    while j<len(s)-1 and s[j]>=t2: j+=1
    ybot=ylo+j-1+(s[j-1]-t2)/(s[j-1]-s[j])
    return ytop,ybot
res={}
for route in ['stated','ruler']:
    M=board_model(route); p0=M['B']+M['n']*H
    allW=[];allL=[]
    for fr in ['o23','o24','o25','o26','o27','o28','s24','s25','s26','s27','x24','x25','x26','x27']:
        i=int(fr[1:]); Ws=[]
        for x in range(550,635,10):
            yt,yb=cover_edges(fr,x,357,450)
            A=hit_plane(p0,M['n'],x,yt); B=hit_plane(p0,M['n'],x,yb); Ws.append(np.linalg.norm(A-B)*100)
        allW.append(np.median(Ws))
        print(route,fr,'W med %.2f  (cols %s)'%(np.median(Ws),np.round(Ws,1).tolist()))
    print(route,'ALL frames median W %.2f, IQR %.2f-%.2f'%(np.median(allW),np.percentile(allW,25),np.percentile(allW,75)))
