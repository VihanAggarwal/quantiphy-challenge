import cv2, numpy as np, sys
v=sys.argv[1]; fi=int(sys.argv[2]); ref=int(sys.argv[3]) if len(sys.argv)>3 else 0
c = cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{v}.mp4')
c.set(cv2.CAP_PROP_POS_FRAMES, fi); ok,f=c.read()
c.set(cv2.CAP_PROP_POS_FRAMES, ref); ok,f0=c.read()
th=np.deg2rad(39.08)
u=np.array([np.cos(th), np.sin(th)])  # down-right along axis (towards tail)
n=np.array([-np.sin(th), np.cos(th)])
diff=np.abs(f.astype(int)-f0.astype(int)).max(2)
m=(diff>40).astype(np.uint8)
N,lab,st,cen=cv2.connectedComponentsWithStats(m)
k=1+np.argmax(st[1:,4])
ys,xs=np.nonzero(lab==k)
cx,cy=xs.mean(),ys.mean()
q=(xs-cx)*n[0]+(ys-cy)*n[1]
cx+=np.median(q)*n[0]; cy+=np.median(q)*n[1]
prof=[]
for s in np.arange(-150,150,1.0):
    vals=[]
    for t in np.arange(-2,2.1,0.5):
        x=cx+s*u[0]+t*n[0]; y=cy+s*u[1]+t*n[1]
        if 0<=int(round(y))<f.shape[0] and 0<=int(round(x))<f.shape[1]:
            vals.append(diff[int(round(y)),int(round(x))])
    prof.append((s,np.mean(vals) if vals else 0))
prof=np.array(prof)
on=prof[prof[:,1]>float(sys.argv[4]) if len(sys.argv)>4 else prof[:,1]>40]
print('frame',fi,'centre %.1f %.1f'%(cx,cy),'extent along axis: %.1f .. %.1f  len %.1f'%(on[0,0],on[-1,0],on[-1,0]-on[0,0]))
if len(sys.argv)>5:
    for s,vv in prof:
        if s<on[0,0]+25 or s>on[-1,0]-40: print(int(s), int(vv), end='; ')
    print()
