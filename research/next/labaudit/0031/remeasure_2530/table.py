import cv2, numpy as np
f=cv2.imread('frames/captured_0031x_48.png').astype(int)
m=(f.sum(2)>60)
m[:400]=0; m[540:]=0
# column-wise top boundary of mask (back edge)
pts_top=[]; 
for x in range(470,965):
    ys=np.where(m[400:540,x])[0]
    if len(ys): pts_top.append((x,400+ys[0]))
pts_top=np.array(pts_top)
# back edge: x in 600..830 roughly
sel=(pts_top[:,0]>600)&(pts_top[:,0]<830)
pb=np.polyfit(pts_top[sel,0],pts_top[sel,1],1); print('back edge y=%.4f x + %.2f'%tuple(pb))
# left side edge: x in 480..560
sel=(pts_top[:,0]>480)&(pts_top[:,0]<560)
pl=np.polyfit(pts_top[sel,0],pts_top[sel,1],1); print('left edge y=%.4f x + %.2f'%tuple(pl))
sel=(pts_top[:,0]>870)&(pts_top[:,0]<950)
pr=np.polyfit(pts_top[sel,0],pts_top[sel,1],1); print('right edge y=%.4f x + %.2f'%tuple(pr))
# front crease: brightness change along columns: top surface lighter than front face
g=cv2.cvtColor(cv2.imread('frames/captured_0031x_48.png'),cv2.COLOR_BGR2GRAY).astype(float)
g=cv2.GaussianBlur(g,(3,3),0)
pts_f=[]
for x in range(480,950,5):
    if 600<x<700: continue
    col=g[470:510,x]; d=np.diff(col)
    k=np.argmin(d); pts_f.append((x,470+k+0.5,d[k]))
pts_f=np.array(pts_f); print(pts_f[:,1].astype(int))
pfr=np.polyfit(pts_f[:,0],pts_f[:,1],1); print('front crease y=%.4f x + %.2f'%tuple(pfr))
def inter(a,b):
    x=(b[1]-a[1])/(a[0]-b[0]); return np.array([x,a[0]*x+a[1]])
BL=inter(pb,pl); BR=inter(pb,pr); FL=inter(pfr,pl); FR=inter(pfr,pr)
print('BL',BL,'BR',BR,'FL',FL,'FR',FR)
np.save('corners.npy',np.array([BL,BR,FR,FL]))
