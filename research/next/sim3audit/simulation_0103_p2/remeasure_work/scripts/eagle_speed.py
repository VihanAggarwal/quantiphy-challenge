import numpy as np
from reg import *
from vio import load
import cv2
# C2 eagle track: darker blob association
def track_dark(v, start, thr=40, maxjump=40):
    fr=load(v).astype(np.int16); med=np.median(fr[::3],axis=0).astype(np.int16)
    pos=[]; p=np.array(start,float)
    for k in range(len(fr)):
        d=np.abs(fr[k]-med).max(axis=2); m=(d>thr).astype(np.uint8)
        n,lab,st,cen=cv2.connectedComponentsWithStats(m)
        best=None
        for i in range(1,n):
            if st[i,4]<15: continue
            dist=np.linalg.norm(cen[i]-p)
            if dist<maxjump and (best is None or dist<best[0]): best=(dist,i)
        if best is None: pos.append([k,np.nan,np.nan]); continue
        i=best[1]; p=cen[i]; pos.append([k,cen[i][0],cen[i][1]])
        p=p+ (np.array(pos[-1][1:])-np.array(pos[-2][1:]) if len(pos)>1 and not np.isnan(pos[-2][1]) else 0)
    return np.array(pos)
if __name__=='__main__':
    import sys
    v=sys.argv[1]; sx,sy=float(sys.argv[2]),float(sys.argv[3]); cname=sys.argv[4]; zE=float(sys.argv[5])
    pos=track_dark(v,(sx,sy))
    np.savetxt(W+'eagle_dark_%s.txt'%v,pos,fmt='%.2f')
    F=frame_of(cname)
    ok=~np.isnan(pos[:,1])
    k=pos[ok,0]; u=pos[ok,1]; vv=pos[ok,2]
    r=F['cam'].ray(u,vv)              # world ENU dirs from cam
    rb=r@F['M'].T                     # boat-frame dirs
    Cb=F['C']
    t=(zE-Cb[2])/rb[:,2]; Pb=Cb+t[:,None]*rb
    X=Pb[:,0]; Y=Pb[:,1]
    # fit X(t) with quad + sin
    w=2*np.pi/25.5
    A=np.c_[np.ones_like(k),k,k**2,np.sin(w*k),np.cos(w*k)]
    cX=np.linalg.lstsq(A,X,rcond=None)[0]
    print('X fit: v0=%.3f m/frame, acc=%.5f m/frame^2 -> speed at t=1: %.2f m/s, t=2: %.2f, avg[1,2]: %.2f'%(cX[1],cX[2],-(cX[1]+2*cX[2]*24)*24,-(cX[1]+2*cX[2]*48)*24, -(cX[1]+cX[2]*72)*24))
    print('Y mean %.2f sd %.2f'%(Y.mean(),Y.std()))
    for kk in [0,12,24,36,48,60]:
        j=np.where(k==kk)[0]
        if len(j): print(kk, np.round(Pb[j[0]],2))
