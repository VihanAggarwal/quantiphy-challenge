import cv2, numpy as np, sys
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/audit3/sim2_04/scripts')
from track import read_all, build_bg
W='/home/user/quantiphy-challenge/research/next/audit3/sim2_04/'
i=int(sys.argv[1]); fr=int(sys.argv[2]); x0,y0,x1,y1=[int(v) for v in sys.argv[3].split(',')]; sc=float(sys.argv[4]); gain=float(sys.argv[5]); out=sys.argv[6]
F=read_all(i); bg,split=build_bg(F)
f=F[fr][y0:y1,x0:x1].astype(np.int16); b=bg[y0:y1,x0:x1].astype(np.int16)
d=np.abs(f-b).max(2)
im=np.clip(d*gain,0,255).astype(np.uint8)
im=cv2.cvtColor(im,cv2.COLOR_GRAY2BGR)
for gx in range((x0//50+1)*50, x1, 50):
    cv2.line(im,(gx-x0,0),(gx-x0,8 if gx%100 else 20),(0,0,255),1)
for gy in range((y0//50+1)*50, y1, 50):
    cv2.line(im,(0,gy-y0),(8 if gy%100 else 20,gy-y0),(0,0,255),1)
im=cv2.resize(im,None,fx=sc,fy=sc,interpolation=cv2.INTER_NEAREST)
cv2.putText(im,f'{i} f{fr} x0={x0} y0={y0} gain{gain}',(5,20),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,255),1)
cv2.imwrite(W+out,im)
# print column profile of max diff in rows band
band=d
colmax=band.max(0)
xs=np.arange(x0,x1)
print('cols where maxdiff>=8 (last 15):', [ (int(x),int(v)) for x,v in zip(xs,colmax) if v>=8][-15:])
