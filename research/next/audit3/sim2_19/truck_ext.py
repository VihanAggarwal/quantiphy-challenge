import cv2, numpy as np
from common import frames
from tmpl import track
fr=frames('simulation_0189_segmented', idx={0,100,200,300,399})
f0=fr[0]
g=cv2.cvtColor(f0,cv2.COLOR_BGR2GRAY).astype(float)
# segmented: background presumably white; foreground mask
bgval=np.median(np.concatenate([g[:50].ravel(),g[:, :30].ravel()]))
print('bg',bgval)
m=(np.abs(f0.astype(float)-f0[5,5].astype(float)).max(axis=2)>20)
ys,xs=np.nonzero(m)
print('fg bbox',xs.min(),xs.max(),ys.min(),ys.max())
# box: brown pixels
hsv=cv2.cvtColor(f0,cv2.COLOR_BGR2HSV)
brown=(hsv[...,0]>5)&(hsv[...,0]<25)&(hsv[...,1]>60)&(hsv[...,2]>60)
brown[400:]=False
ys,xs=np.nonzero(brown)
print('brown bbox',xs.min(),xs.max(),ys.min(),ys.max())
for y in [220,260,300,340]:
    r=np.nonzero(brown[y])[0]; print(' row',y,r.min(),r.max(),r.max()-r.min()+1)
for x in [600,700,800,900,920]:
    c=np.nonzero(brown[:,x])[0]; print(' col',x,c.min(),c.max(),c.max()-c.min()+1)
# box motion over the whole clip via brown mask top/bottom at x=700
for f in sorted(fr):
    hsv=cv2.cvtColor(fr[f],cv2.COLOR_BGR2HSV)
    b=(hsv[...,0]>5)&(hsv[...,0]<25)&(hsv[...,1]>60)&(hsv[...,2]>60); b[450:]=False
    c=np.nonzero(b[:,700])[0]; r=np.nonzero(b[250])[0]
    print('f',f,'col700 top',c.min(),'bot',c.max(),'row250',r.min(),r.max())
# truck extents: rows with fg below 380
ys,xs=np.nonzero(m[380:]); print('truck x',xs.min(),xs.max(),'y bottom',ys.max()+380)
m2=m.copy(); m2[:, :]=m
# top of truck (rails) in x>1350
ys,xs=np.nonzero(m[:, 1350:1900]); print('truck front-part top y',ys.min())
