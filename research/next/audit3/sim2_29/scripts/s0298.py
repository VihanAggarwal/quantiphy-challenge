from util import *
fr=frames('simulation_0298')
bgc=np.median(fr[0].reshape(-1,3),axis=0).astype(np.float32)
R=[]
for i in range(0,48):
    d=np.abs(fr[i].astype(np.float32)-bgc).max(axis=2)
    m=(d>40).astype(np.uint8)
    nl,lab,st,cen=cv2.connectedComponentsWithStats(m)
    k=1+np.argmax(st[1:,4]); x,y,w,h,a=st[k]
    R.append((i,x,x+w,y,y+h,w,h,cen[k][0]))
R=np.array(R,float)
for r in R[::8]: print(r)
print('slopes front,rear,centroid',[np.polyfit(R[:,0],R[:,c],1)[0] for c in (1,2,7)])
# body width without mirrors: row-wise width profile at mid frame
i=20; d=np.abs(fr[i].astype(np.float32)-bgc).max(axis=2); m=d>40
cols=m.sum(axis=0); rows=m.sum(axis=1)
ys=np.where(rows>0)[0]; print('rows extent',ys.min(),ys.max())
# vertical extent per column band
x0=int(R[i,1]); x1=int(R[i,2])
for xc in range(x0,x1,40):
    yy=np.where(m[:,xc])[0]; print(xc, yy.min() if len(yy) else -1, yy.max() if len(yy) else -1, (yy.max()-yy.min()+1) if len(yy) else 0)
