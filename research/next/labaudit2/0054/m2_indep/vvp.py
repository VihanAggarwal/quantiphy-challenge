from common import *
import numpy as np, cv2
f0=frames('a')[0]
g=cv2.cvtColor(f0,cv2.COLOR_BGR2GRAY)
lsd=cv2.createLineSegmentDetector(0)
lines=lsd.detect(g)[0].reshape(-1,4)
L=[]
for x1,y1,x2,y2 in lines:
    dx,dy=x2-x1,y2-y1; l=np.hypot(dx,dy)
    if l>60 and abs(dx)/l<0.15: L.append((x1,y1,x2,y2,l))
L=np.array(L); print(len(L))
# homogeneous lines, find VP by least squares (minimize sum of squared normalized distances)
def vp_fit(L):
    H=[]
    for x1,y1,x2,y2,l in L:
        a=np.cross([x1,y1,1],[x2,y2,1]); a=a/np.hypot(a[0],a[1]); H.append(a*np.sqrt(l))
    H=np.array(H); _,_,Vt=np.linalg.svd(H); v=Vt[-1]; return v/v[2] if abs(v[2])>1e-9 else v
v=vp_fit(L); print('VP',v)
# robust: iterate removing lines with large angular residual
for it in range(5):
    res=[]
    for x1,y1,x2,y2,l in L:
        mx,my=(x1+x2)/2,(y1+y2)/2
        d1=np.array([x2-x1,y2-y1]); d2=np.array([v[0]-mx,v[1]-my])
        c=abs(d1@d2)/np.linalg.norm(d1)/np.linalg.norm(d2); res.append(np.degrees(np.arccos(min(1,c))))
    res=np.array(res); keep=res<1.0
    print(it,len(L),keep.sum(),np.median(res))
    L=L[keep]; v=vp_fit(L); print('VP',v)
img=f0.copy()
for x1,y1,x2,y2,l in L: cv2.line(img,(int(x1),int(y1)),(int(x2),int(y2)),(0,0,255),2)
cv2.imwrite(OUT+'frames/vlines.png',img)
f=711.; cx,cy=640,360
d=np.array([(v[0]-cx)/f,(v[1]-cy)/f,1.]); d/=np.linalg.norm(d)
if d[1]<0: d=-d
print('down dir in cam',d, 'pitch(deg, camera tilt down)',np.degrees(np.arcsin(d[2])),'roll',np.degrees(np.arctan2(-d[0],d[1])))
np.save(OUT+'down.npy',d)
