import cv2,numpy as np,sys
v=sys.argv[1]; roi=eval(sys.argv[2]); thr=float(sys.argv[3]) if len(sys.argv)>3 else 30
x0,y0,x1,y1=roi
c=cv2.VideoCapture(f'data/QuantiPhy/{v}.mp4')
frs=[]
while True:
    ok,f=c.read()
    if not ok: break
    frs.append(f[y0:y1,x0:x1].astype(np.int16))
st=np.stack(frs); bg=np.median(st,axis=0)
out=[]
for i,f in enumerate(frs):
    d=np.abs(f-bg).max(axis=2)
    m=(d>thr).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((2,2),np.uint8))
    n,lab,s,cen=cv2.connectedComponentsWithStats(m)
    if n<2: out.append(None); continue
    k=1+np.argmax(s[1:,4])
    # merge components close to the biggest
    x,y,w,h,a=s[k]
    keep=[k]
    for j in range(1,n):
        if j==k or s[j,4]<15: continue
        xj,yj,wj,hj,_=s[j]
        if xj<x+w+8 and xj+wj>x-8 and yj<y+h+8 and yj+hj>y-8: keep.append(j)
    mm=np.isin(lab,keep)
    ys,xs=np.nonzero(mm)
    out.append((i,xs.min()+x0,xs.max()+x0,ys.min()+y0,ys.max()+y0,xs.mean()+x0,ys.mean()+y0,len(xs)))
for o in out: print(o)
r=np.array([o for o in out if o is not None],float)
t=r[:,0]
print('cx px/f %.3f  left %.3f right %.3f'%(np.polyfit(t,r[:,5],1)[0],np.polyfit(t,r[:,1],1)[0],np.polyfit(t,r[:,2],1)[0]))
W=r[:,2]-r[:,1]+1;H=r[:,4]-r[:,3]+1
print('W med %.1f mean %.1f max %.1f | H med %.1f max %.1f'%(np.median(W),W.mean(),W.max(),np.median(H),H.max()))
