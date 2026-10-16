import cv2, numpy as np
f=711.; cx,cy=640.,360.
K=np.array([[f,0,cx],[0,f,cy],[0,0,1]]); Ki=np.linalg.inv(K)
im=cv2.imread('frames/captured_0036x/f45.png')
hsv=cv2.cvtColor(im,cv2.COLOR_BGR2HSV)
m=((hsv[...,1]>40)|(hsv[...,2]<150)).astype(np.uint8)
m[690:,1020:]=0
def subpix_row(y, side):
    row=m[y].astype(float)
    xs=np.where(row[:1270]>0)[0]
    return xs.min() if side=='L' else xs.max()
def fitline(pts):
    pts=np.array(pts,float)
    mu=pts.mean(0); u,s,vt=np.linalg.svd(pts-mu); d=vt[0]
    n=np.array([-d[1],d[0]]); c=-n@mu
    return np.array([n[0],n[1],c])
L=[(subpix_row(y,'L')-0.5,y) for y in range(460,571)]
R=[(subpix_row(y,'R')+0.5,y) for y in range(460,571)]
B=[]
for x in range(470,700):
    ys=np.where(m[380:700,x])[0]+380; B.append((x,ys.min()-0.5))
# front top edge from gray profile: first strong drop below ~100 after y>570
g=im.astype(float).mean(2)
Fr=[]
for x in range(260,940,4):
    col=g[570:600,x]
    i=np.where(col<100)[0][0]
    # subpixel crossing at 100
    y=570+i-1+(col[i-1]-100)/(col[i-1]-col[i])
    Fr.append((x,y))
lines={k:fitline(v) for k,v in dict(L=L,R=R,B=B,F=Fr).items()}
for k,v in dict(L=L,R=R,B=B,F=Fr).items():
    l=lines[k]; r=np.array([l[0]*p[0]+l[1]*p[1]+l[2] for p in v]); print(k,'rms',r.std(),'max',abs(r).max())
def X(a,b): p=np.cross(a,b); return p/p[2]
vL=X(lines['L'],lines['R']); vF=X(lines['F'],lines['B'])
print('VP depth',vL,'VP front/back',vF)
d1=Ki@vL; d1/=np.linalg.norm(d1)
d2=Ki@vF; d2/=np.linalg.norm(d2)
print('angle between dirs',np.degrees(np.arccos(abs(d1@d2))))
n=np.cross(d1,d2); n/=np.linalg.norm(n)
if n[1]<0: n=-n  # normal pointing down in cam coords (y down) -> plane below camera
print('normal',n)
corners={'FL':X(lines['F'],lines['L']),'FR':X(lines['F'],lines['R']),'BL':X(lines['B'],lines['L']),'BR':X(lines['B'],lines['R'])}
print(corners)
def bp(p,h):
    r=Ki@np.array([p[0],p[1],1.]); t=h/(n@r); return r*t
for h in [0.10,0.15]:
    P={k:bp(v,h) for k,v in corners.items()}
    front=np.linalg.norm(P['FR']-P['FL']); back=np.linalg.norm(P['BR']-P['BL'])
    left=np.linalg.norm(P['BL']-P['FL']); right=np.linalg.norm(P['BR']-P['FR'])
    print('h',h,'front %.3f back %.3f left %.3f right %.3f  ratio side/front %.3f'%(front,back,left,right,(left+right)/(front+back)))
np.save('scripts/plane_n.npy',n)
np.save('scripts/corners.npy',np.array([corners[k] for k in ['FL','FR','BL','BR']]))
