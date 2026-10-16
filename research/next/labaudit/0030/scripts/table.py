import cv2,numpy as np
med=cv2.imread('/home/user/quantiphy-challenge/research/next/labaudit/0030/median_x.png')
g=cv2.cvtColor(med,cv2.COLOR_BGR2GRAY).astype(float)
m=g>25
# left/right edge subpixel per row 448..527
L=[];R=[]
for y in range(448,527):
    row=np.nonzero(m[y])[0]
    row=row[row<1000]
    L.append((row.min(),y)); R.append((row.max(),y))
L=np.array(L,float); R=np.array(R,float)
pl=np.polyfit(L[:,1],L[:,0],1); pr=np.polyfit(R[:,1],R[:,0],1)
print('left x=%.4f*y+%.2f'%tuple(pl),'right x=%.4f*y+%.2f'%tuple(pr))
# back edge: for columns 420..780 find first non-black row
B=[]
for x in range(420,781,5):
    col=np.nonzero(m[380:600,x])[0]
    B.append((x,380+col.min()))
B=np.array(B,float); pb=np.polyfit(B[:,0],B[:,1],1); print('back y=%.5f*x+%.2f'%tuple(pb), 'resid',np.std(B[:,1]-np.polyval(pb,B[:,0])))
# front edge of top surface: find strong brightness drop (top surface -> front face) per column
F=[]
for x in range(260,920,5):
    colv=g[500:560,x]
    dv=np.diff(colv)
    k=np.argmin(dv)  # biggest drop
    F.append((x,500+k+0.5))
F=np.array(F,float); pf=np.polyfit(F[:,0],F[:,1],1); print('front y=%.5f*x+%.2f'%tuple(pf),'resid',np.std(F[:,1]-np.polyval(pf,F[:,0])))
# bottom of front face
Bo=[]
for x in range(260,920,5):
    col=np.nonzero(m[540:600,x])[0]
    # first black after face
    k=np.nonzero(~m[540:600,x])[0]
    Bo.append((x,540+k.min()))
Bo=np.array(Bo,float); pbo=np.polyfit(Bo[:,0],Bo[:,1],1); print('face bottom y=%.5f*x+%.2f'%tuple(pbo))
def inter(pxy, pyx):
    # line1 x=a*y+b ; line2 y=c*x+d
    a,b=pxy; c,dd=pyx
    y=(c*b+dd)/(1-c*a); x=a*y+b; return np.array([x,y])
BL=inter(pl,pb); BR=inter(pr,pb); FL=inter(pl,pf); FR=inter(pr,pf)
print('BL',BL,'BR',BR,'FL',FL,'FR',FR)
np.save('/home/user/quantiphy-challenge/research/next/labaudit/0030/corners.npy',np.array([FL,FR,BR,BL]))
f=711.; c=np.array([640.,360.])
def ray(p): return np.array([(p[0]-c[0])/f,(p[1]-c[1])/f,1.])
# vanishing points
def vp(p1,p2,p3,p4):
    l1=np.cross([*p1,1],[*p2,1]); l2=np.cross([*p3,1],[*p4,1]); v=np.cross(l1,l2); return v
vd=vp(FL,BL,FR,BR); vw=vp(FL,FR,BL,BR)
print('vp depth',vd[:2]/vd[2] if abs(vd[2])>1e-9 else vd, 'vp width', vw)
Dd=np.array([(vd[0]/vd[2]-c[0])/f,(vd[1]/vd[2]-c[1])/f,1.]); Dd/=np.linalg.norm(Dd)
Dw=np.array([vw[0],vw[1],vw[2]*0]) if abs(vw[2])<1e-9*np.linalg.norm(vw) else np.array([(vw[0]/vw[2]-c[0])/f,(vw[1]/vw[2]-c[1])/f,1.])
Dw=np.array([vw[0]-c[0]*vw[2], vw[1]-c[1]*vw[2], f*vw[2]]); Dw/=np.linalg.norm(Dw)
print('cos(width,depth)=',Dw@Dd)
