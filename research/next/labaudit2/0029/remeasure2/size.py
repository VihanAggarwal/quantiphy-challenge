import cv2,numpy as np,json,sys
T=json.load(open('track_raw.json'))
tag=sys.argv[1] if len(sys.argv)>1 else ''
c=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/captured_0029{tag}.mp4'); frames=[]
while True:
    ok,f=c.read()
    if not ok: break
    frames.append(f)
def fit_circle(p):
    A=np.c_[2*p[:,0],2*p[:,1],np.ones(len(p))]; b=(p**2).sum(1)
    s=np.linalg.lstsq(A,b,rcond=None)[0]; r=np.sqrt(s[2]+s[0]**2+s[1]**2); return s[0],s[1],r
out={}
for i in range(18,49):
    f=frames[i]; hsv=cv2.cvtColor(f,cv2.COLOR_BGR2HSV).astype(float)
    # yellowness channel: saturation*value-ish -> use S channel (ball saturated; bg white/grey/brown less)
    # use b* from Lab: yellow strongly positive b*
    lab=cv2.cvtColor(f,cv2.COLOR_BGR2LAB).astype(float); B=cv2.GaussianBlur(lab[:,:,2],(3,3),0)
    x0,y0=T[tag][i][1],T[tag][i][2]
    pts=[];allpts=[]
    for ang in np.radians(np.arange(0,360,5)):
        d=np.array([np.cos(ang),-np.sin(ang)])  # ang measured CCW from +x, image y up
        rs=np.arange(5,45,0.25); xs=x0+rs*d[0]; ys=y0+rs*d[1]
        v=cv2.remap(B.astype(np.float32),xs.astype(np.float32)[None],ys.astype(np.float32)[None],cv2.INTER_LINEAR)[0]
        g=-np.gradient(v); k=np.argmax(g)
        if 1<=k<len(g)-1:
            # parabolic subpixel
            dd=(g[k-1]-g[k+1])/(2*(g[k-1]-2*g[k]+g[k+1])); r=rs[k]+dd*0.25
        else: r=rs[k]
        deg=np.degrees(ang)%360
        allpts.append((deg,x0+r*d[0],y0+r*d[1]))
    A=np.array(allpts)
    up=A[(A[:,0]>=20)&(A[:,0]<=160)]
    side=A[((A[:,0]>=20)&(A[:,0]<=160))|((A[:,0]>=200)&(A[:,0]<=340)&False)]
    cx,cy,r=fit_circle(up[:,1:])
    # vertical: top edge at 90deg, and also left/right at 0/180
    rad=lambda deg: np.hypot(*(A[np.argmin(np.abs(A[:,0]-deg)),1:]-[x0,y0]))
    out[i]=dict(cx=cx,cy=cy,r=r,top=rad(90),bot=rad(270),left=rad(180),right=rad(0))
    print(f'v{i:02d} circ c=({cx:6.1f},{cy:6.1f}) d={2*r:5.2f}  top={rad(90):5.1f} bot={rad(270):5.1f} L={rad(180):5.1f} R={rad(0):5.1f}  vert={rad(90)+rad(270):5.1f} horiz={rad(0)+rad(180):5.1f}')
json.dump(out,open(f'size_{tag or "c"}.json','w'))
