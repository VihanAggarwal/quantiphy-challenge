import cv2, numpy as np, sys
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0103_p2/scripts')
from track import *; from geom import *
fr=frames('simulation_0043_segmented')
res={}
for i,im in fr.items():
    m=fgmask(im); m[:470,:]=False
    ys,xs=np.where(m); res[i]=(xs.min(),xs.max(),ys.min(),ys.max(),xs.mean(),ys.mean(),len(xs))
for i in [0,1,12,24,36,48,60,71]: print(i,res[i])
def gray(im): 
    g=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY).astype(np.float32); g[:470]=255; return g
def sub(R,px,py):
    l,c,r=R[py,px-1],R[py,px],R[py,px+1]; dx=0.5*(l-r)/(l-2*c+r)
    u,c,d=R[py-1,px],R[py,px],R[py+1,px]; dy=0.5*(u-d)/(u-2*c+d)
    return px+dx,py+dy
def disp(i,j):
    a=gray(fr[i]); b=gray(fr[j]); x0,x1,y0,y1=res[i][:4]
    T=a[y0-3:y1+4,x0-3:x1+4]; R=cv2.matchTemplate(b,T,cv2.TM_SQDIFF_NORMED)
    mn,_,ml,_=cv2.minMaxLoc(R); sx,sy=sub(R,*ml); return sx-(x0-3), sy-(y0-3), mn
for (i,j) in [(24,48),(12,36),(1,24),(24,36),(36,48),(48,71)]:
    print(i,j,np.round(disp(i,j),3))
