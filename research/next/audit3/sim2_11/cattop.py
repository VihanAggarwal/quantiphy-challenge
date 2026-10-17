import cv2,numpy as np
cap=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0233_segmented.mp4')
rows=[]
i=0
while True:
    ok,f=cap.read()
    if not ok: break
    g=f.astype(int).sum(2)
    m=(g<300)
    m[:, 1400:]=False
    m=m.astype(np.uint8)
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    if n>1:
        k=1+np.argmax(st[1:,4]); 
        sel=np.zeros(m.shape,bool)
        x,y,w,h,a=st[k]
        for j in range(1,n):
            xj,yj,wj,hj,aj=st[j]
            if aj>5 and xj<x+w+20 and xj+wj>x-20 and yj<y+h+20 and yj+hj>y-20: sel|=(lab==j)
        ys,xs=np.nonzero(sel)
        # body: columns with thickness >= 25 px
        colth=np.bincount(xs,minlength=1920)
        body=np.nonzero(colth>=25)[0]
        rows.append((i,xs.min(),xs.max(),ys.min(),ys.max(),body.min() if len(body) else -1, body.max() if len(body) else -1, colth.max()))
        if i in (20,30,40,49):
            c=f[ys.min()-15:ys.max()+15, max(0,xs.min()-15):xs.max()+15]
            cv2.imwrite(f'crops/top_cat{i}.png',cv2.resize(c,None,fx=2,fy=2,interpolation=cv2.INTER_NEAREST))
    i+=1
for r in rows: print(*r,'len',r[2]-r[1]+1,'body',r[6]-r[5]+1,'tail',r[5]-r[1])
R=np.array(rows,float)
s=R[:,1]>2
for nm,c in [('tailtip',1),('nose',2),('bodyL',5)]:
    p=np.polyfit(R[s,0],R[s,c],1); print(nm,'%.3f'%p[0])
