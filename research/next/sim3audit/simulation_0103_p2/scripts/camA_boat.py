import cv2, numpy as np, sys
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0103_p2/scripts')
from track import *
fr=frames('simulation_0024_segmented')
# boat mask: foreground below y=312 excluding rock region (rock bbox y<=311); use rows>=315 plus mast
res={}
for i,im in fr.items():
    m=fgmask(im)
    m[:315,:]=False  # drop rock rows (mast top may be clipped; fine for centroid of hull)
    ys,xs=np.where(m)
    res[i]=(xs.min(),xs.max(),ys.min(),ys.max(),xs.mean(),ys.mean(),len(xs))
for i in [0,12,24,36,48,60,72,74]:
    print(i,res[i])
# template tracking of hull between frames using phase correlation on grayscale masked region
def crop(im): return cv2.cvtColor(im,cv2.COLOR_BGR2GRAY).astype(np.float32)
a=crop(fr[24]); b=crop(fr[48])
# mask out rock
a[:315]=255; b[:315]=255
# brute-force subpixel template match: template from frame 24 bbox
x0,x1,y0,y1=res[24][0],res[24][1],res[24][2],res[24][3]
T=a[y0-2:y1+3, x0-2:x1+3]
R=cv2.matchTemplate(b, T, cv2.TM_SQDIFF_NORMED)
mn,mx,ml,Ml=cv2.minMaxLoc(R)
px,py=ml
# subpixel parabola
def sub(R,px,py):
    if 0<px<R.shape[1]-1:
        l,c,r=R[py,px-1],R[py,px],R[py,px+1]; dx=0.5*(l-r)/(l-2*c+r)
    else: dx=0
    if 0<py<R.shape[0]-1:
        u,c,d=R[py-1,px],R[py,px],R[py+1,px]; dy=0.5*(u-d)/(u-2*c+d)
    else: dy=0
    return px+dx,py+dy
sx,sy=sub(R,px,py)
print('template disp 24->48:', sx-(x0-2), sy-(y0-2), 'score',mn)
