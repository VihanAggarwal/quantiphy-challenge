from util import *
import sys
v=sys.argv[1]
fr=frames(v)
xs=[];ys=[];ext=[]
for i,f in fr:
    hsv=cv2.cvtColor(f,cv2.COLOR_BGR2HSV)
    m=((hsv[...,0]>75)&(hsv[...,0]<100)&(hsv[...,1]>120)&(hsv[...,2]>80)).astype(np.uint8)
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    # pick component with area>500 and y>500 (rolling cup)
    best=None
    for k in range(1,n):
        if st[k,4]>800 and cen[k][1]>520:
            best=k
    if best is None: continue
    xs.append((i,cen[best][0],cen[best][1],st[best,2],st[best,3],st[best,4]))
a=np.array(xs)
print(a[:4]); print(a[-3:])
t=a[:,0]; x=a[:,1]
sel=t>=2
p=np.polyfit(t[sel],x[sel],1); print('px/frame',p[0],'resid',np.std(x[sel]-np.polyval(p,t[sel])))
s=0.338/(p[0]*24); print('scale m/px',s)
print('bbox w median',np.median(a[:,3]),'h median',np.median(a[:,4]))
print('len m',np.median(a[:,4])*s,'diam m',np.median(a[:,3])*s)
