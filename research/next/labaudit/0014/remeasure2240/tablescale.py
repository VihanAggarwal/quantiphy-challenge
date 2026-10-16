import numpy as np
f=711.0; cx,cy=640.,360.
def ray(u,v):
    r=np.array([(u-cx)/f,(v-cy)/f,1.]); return r/np.linalg.norm(r)
nt=np.load('table_normal.npy')
Pt,Pb,e,h,n=np.load('model.npy')
NL=np.array([425.5,500.]); NR=np.array([728,455.5])
def hit(px,D):  # plane nt.X = -D  (nt points toward camera, so nt.X<0 for points)
    R=ray(*px); s=-D/(nt@R); return s*R
D0=-(nt@Pb)  # plane through Pb
for W,lab in [(76.0,'76 width'),(60.3,'60.3 width')]:
    L0=np.linalg.norm(hit(NR,D0)-hit(NL,D0))
    D=D0*W/100/L0
    print(lab,': plane distance %.4f vs through-Pb %.4f; near edge at Pb-plane = %.1f cm'%(D,D0,100*L0))
    for nm,px,st in [('board bottom mid',(559.1,416.0),1.701),('pen',(468.3,437.2),1.6725),('book',(654,410.7),1.665)]:
        print('   %s: table-plane range %.4f stated %.4f diff %.1f cm'%(nm,np.linalg.norm(hit(px,D)),st,100*(np.linalg.norm(hit(px,D))-st)))
