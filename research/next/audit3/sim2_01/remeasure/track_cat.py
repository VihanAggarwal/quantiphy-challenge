import cv2, numpy as np, sys
v=sys.argv[1]
c=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/simulation_{v}.mp4')
rows=[]
i=0
while True:
    ok,f=c.read()
    if not ok: break
    g=cv2.cvtColor(f,cv2.COLOR_BGR2GRAY)
    m=(g<40).astype(np.uint8)
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    # choose largest component within cat region
    best=None
    for k in range(1,n):
        x,y,w,h,a=st[k]
        if a<500: continue
        if best is None or a>st[best][4]: best=k
    x,y,w,h,a=st[best]
    ys,xs=np.nonzero(lab==best)
    rows.append((i,x,x+w-1,y,y+h-1,a,xs.mean(),ys.mean()))
    i+=1
r=np.array(rows)
for row in r[::5]: print(' '.join(f'{v:.1f}' for v in row))
t=r[:,0]
for col,name in [(1,'left'),(2,'right'),(6,'cx')]:
    p=np.polyfit(t,r[:,col],1); res=r[:,col]-np.polyval(p,t)
    print(name,'slope px/frame %.3f'%p[0],'rms %.2f'%res.std())
py=np.polyfit(t,r[:,7],1); print('cy slope',py[0])
