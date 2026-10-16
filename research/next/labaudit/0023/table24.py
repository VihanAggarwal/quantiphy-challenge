import cv2, numpy as np
from table import fitline, inter
F=711.;CX=640.;CY=360.
K=np.array([[F,0,CX],[0,F,CY],[0,0,1.]])
im=cv2.imread('others/captured_0024x_48.png').astype(float); g=im.max(2)
def topb(x):  # first y from top where g>40 (subpixel)
    c=g[300:700,x]; k=np.nonzero(c>40)[0][0]; return 300+k-1+(40-c[k-1])/(c[k]-c[k-1])
def botb(x):  # last y where g>40 in table region
    c=g[400:640,x]; k=np.nonzero(c>40)[0][-1]; return 400+k+(c[k]-40)/(c[k]-c[k+1])
def leftb(y):
    r=g[y,300:800]; k=np.nonzero(r>40)[0][0]; return 300+k-1+(40-r[k-1])/(r[k]-r[k-1])
LB=np.array([(x,topb(x)) for x in range(425,492,3)])
RB=np.array([(x,topb(x)) for x in range(880,1060,5)])
BLF=np.array([(x,botb(x)) for x in range(440,620,5)])   # bottom of thickness, left-front face
BFR=np.array([(x,botb(x)) for x in range(820,1090,5)])  # bottom of thickness, right-front face (avoid leg 742-796)
for nm,P in [('LB',LB),('RB',RB),('BLF',BLF),('BFR',BFR)]:
    l,e=fitline(P); print(nm,'resid',round(e,2),'slope',round(np.polyfit(P[:,0],P[:,1],1)[0],4))
lLB,_=fitline(LB); lRB,_=fitline(RB); lBLF,_=fitline(BLF); lBFR,_=fitline(BFR)
VP1=inter(lBLF,lRB); VP2=inter(lBFR,lLB)
print('VP1',VP1.round(1),'VP2',VP2.round(1))
d1=np.linalg.solve(K,np.r_[VP1,1]); d1/=np.linalg.norm(d1)
d2=np.linalg.solve(K,np.r_[VP2,1]); d2/=np.linalg.norm(d2)
print('angle between table directions (deg):',np.degrees(np.arccos(abs(d1@d2))).round(2))
n=np.cross(d1,d2); n/=np.linalg.norm(n); 
if n[1]<0: n=-n
print('normal',n.round(4))
np.save('others/t24_n.npy',n); np.save('others/t24_d.npy',np.array([d1,d2]))
np.save('others/t24_lines.npy',np.array([lLB,lRB,lBLF,lBFR]))
