"""Surface range vs capture frame: stated anchors, linear interpolation of the anchors (pipeline), dynamic fit,
geometric route, half-max size route. Drawn with OpenCV."""
import sys, json; sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit2/0010/scripts')
from common import *
import geo
B='/home/user/quantiphy-challenge/research/next/labaudit2/0010/'
D3=json.load(open(B+'pend3d_v3.json')); S=json.load(open(B+'size_s.json'))
k=np.arange(49); n=np.array([cap(i) for i in k])
W,H=1000,560; img=np.full((H,W,3),255,np.uint8)
X=lambda c: int(60+c*(W-90)/50); Y=lambda r: int(H-40-(r-1.25)*(H-80)/0.65)
for r in np.arange(1.3,1.91,0.1): cv2.line(img,(60,Y(r)),(W-30,Y(r)),(230,230,230),1); cv2.putText(img,f"{r:.1f}",(10,Y(r)+5),0,0.45,(0,0,0),1)
for c in range(0,51,5): cv2.line(img,(X(c),20),(X(c),H-40),(235,235,235),1); cv2.putText(img,f"c{c}",(X(c)-12,H-20),0,0.4,(0,0,0),1)
def poly(cs,rs,col,th=2):
    pts=np.array([[X(c),Y(r)] for c,r in zip(cs,rs)],np.int32); cv2.polylines(img,[pts],False,col,th,cv2.LINE_AA)
R=np.array(D3['a07']['R'])-0.035; poly(np.arange(len(R)),R,(200,0,0))                 # blue: dynamic fit
Rg=geo.ranges(1.52,0.346,pu=np.full(49,640.3),pv=np.full(49,234.1))[0]-0.035; poly(n,Rg,(0,150,0),1)  # green: geometric
Rs=F*0.07/np.array([S[i]['wh'] for i in k])-0.035
for c,r in zip(n,Rs): cv2.circle(img,(X(c),Y(r)),3,(120,120,120),-1)                 # grey dots: half-max size
ts=np.array([0.3,0.6,0.9,1.2,1.5,1.8]); st=np.array([1.706,1.344,1.4605,1.784,1.717,1.350])
poly(ts*25,st,(0,0,220),1)                                                               # red: linear interp (pipeline)
for c,r in zip(ts*25,st): cv2.drawMarker(img,(X(c),Y(r)),(0,0,220),cv2.MARKER_TILTED_CROSS,14,2)
cv2.line(img,(X(15),20),(X(15),H-40),(0,140,255),1); cv2.line(img,(X(16),20),(X(16),H-40),(0,140,255),1)
for i,(t,c) in enumerate([("blue: pendulum fit (surface)",(200,0,0)),("green: sphere geometry",(0,150,0)),("grey: half-max size",(120,120,120)),("red: stated anchors, linear interp (pipeline)",(0,0,220)),("orange: c15,c16 (t=0.6 FD)",(0,140,255))]):
    cv2.putText(img,t,(W-400,40+18*i),0,0.45,c,1,cv2.LINE_AA)
cv2.imwrite(B+'img/range_vs_capture.png',img)
