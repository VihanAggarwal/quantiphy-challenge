import cv2,numpy as np,sys
v=sys.argv[1]
cap=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{v}.mp4')
F=[]
while True:
    ok,f=cap.read()
    if not ok: break
    F.append(f[550:800,0:1100].copy())
F=np.array(F)
bg=np.median(F,axis=0).astype(np.int16)
rows=[]
for i,f in enumerate(F):
    d=np.abs(f.astype(np.int16)-bg).sum(2)
    m=(d>45).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((2,2),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    k=1+np.argmax(st[1:,4]); x,y,w,h,a=st[k]
    sel=np.zeros(m.shape,bool)
    for j in range(1,n):
        xj,yj,wj,hj,aj=st[j]
        if aj>10 and xj<x+w+15 and xj+wj>x-15 and yj<y+h+15 and yj+hj>y-15: sel|=(lab==j)
    ys,xs=np.nonzero(sel)
    dark=(f.astype(int).sum(2)<150)&sel
    yd,xd=np.nonzero(dark)
    rows.append((i,xs.min(),xs.max(),ys.min()+550,ys.max()+550,xd.mean(),yd.mean()+550))
    if i in (12,24,36):
        c=F[i][ys.min()-10:ys.max()+10, xs.min()-10:xs.max()+10].copy()
        c=cv2.resize(c,None,fx=3,fy=3,interpolation=cv2.INTER_NEAREST)
        cv2.imwrite(f'crops/{v}_cat{i}.png',c)
R=np.array(rows,float)
for r in rows: print(r[0],r[1],r[2],r[3],r[4],'w',r[2]-r[1]+1,'h',r[4]-r[3]+1,'cx %.1f'%r[5])
t=R[:,0]
for nm,col in [('left',1),('right',2),('darkcx',5)]:
    s=(t>=3)
    p=np.polyfit(t[s],R[s,col],1); print(nm,'slope px/frame %.3f'%p[0])
print('mean w (3..49) %.1f  med %.1f'%(np.mean(R[3:,2]-R[3:,1]+1),np.median(R[3:,2]-R[3:,1]+1)))
print('mean h %.1f med %.1f'%(np.mean(R[3:,4]-R[3:,3]+1),np.median(R[3:,4]-R[3:,3]+1)))
