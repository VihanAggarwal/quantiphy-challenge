import cv2, numpy as np
from geo import *
def sub_cross(prof, thr):
    # first index where prof crosses thr going from <thr to >=thr; returns subpixel
    k=np.nonzero(prof>=thr)[0]
    if len(k)==0: return None
    k=k[0]
    if k==0: return 0.
    return k-1+(thr-prof[k-1])/(prof[k]-prof[k-1])
def board_edges(fr, rows=range(392,476), thr=None):
    im=cv2.imread(f'frames/{fr}.png').astype(float); g=im.min(2)
    L=[];R=[]
    for y in rows:
        p=g[y,440:600]; bg=np.median(p[:20]); wh=np.median(p[-30:]); t=(bg+wh)/2
        xl=sub_cross(p,t); 
        q=g[y,600:740][::-1]; bg2=np.median(q[:20]); t2=(bg2+np.median(q[-30:]))/2
        xr=sub_cross(q,t2)
        if xl is not None: L.append((440+xl,y))
        if xr is not None: R.append((739-xr,y))
    return np.array(L),np.array(R)
def fitline(P):
    P=np.asarray(P,float); c=P.mean(0); u,s,vt=np.linalg.svd(P-c); d=vt[0]; n=np.array([-d[1],d[0]])
    return np.array([n[0],n[1],-n@c]), np.abs((P-c)@n).max()
def xat(l,y): return -(l[1]*y+l[2])/l[0]
if __name__=='__main__':
    for fr in ['o20','x20','o44','x44','o48','x48']:
        L,R=board_edges(fr)
        lL,eL=fitline(L); lR,eR=fitline(R)
        print(fr,'resid',round(eL,2),round(eR,2),' x at y=356:',round(xat(lL,356),1),round(xat(lR,356),1),' y=483:',round(xat(lL,483),1),round(xat(lR,483),1))
        np.save(f'boardLR_{fr}.npy',np.array([lL,lR]))
    # top and bottom edges: vertical profiles
    for fr in ['o20','x20','o44','x44','o48','x48','o00']:
        im=cv2.imread(f'frames/{fr}.png').astype(float); g=im.min(2)
        tops=[];bots=[]
        for x in range(520,660,10):
            p=g[330:420,x]; t=(np.median(p[:10])+np.median(p[-15:]))/2
            yt=sub_cross(p,t); 
            q=g[440:520,x][::-1]; t2=(np.median(q[:10])+np.median(q[-15:]))/2
            yb=sub_cross(q,t2)
            tops.append(None if yt is None else round(330+yt,1)); bots.append(None if yb is None else round(519-yb,1))
        print(fr,'top',tops); print(fr,'bot',bots)
