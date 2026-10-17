import cv2, numpy as np, sys
v=sys.argv[1]; ymin=int(sys.argv[2]) if len(sys.argv)>2 else 0
c=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/simulation_{v}.mp4')
fr=[]
while True:
    ok,f=c.read()
    if not ok: break
    fr.append(cv2.cvtColor(f,cv2.COLOR_BGR2GRAY))
fr=np.array(fr)
med=np.median(fr,axis=0)
rows=[]
for i,g in enumerate(fr):
    d=np.abs(g.astype(float)-med)
    m=((d>35)&(g<70)).astype(np.uint8)  # dark moving pixels (cat body)
    m[:ymin]=0
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    k=1+np.argmax(st[1:,4])
    x,y,w,h,a=st[k]
    ys,xs=np.nonzero(lab==k)
    rows.append((i,x,x+w-1,y,y+h-1,a,xs.mean(),ys.mean()))
r=np.array(rows,float)
for row in r[::4]: print(' '.join(f'{v:.1f}' for v in row))
t=r[:,0]
sel=np.ones(len(t),bool)
for col,name in [(1,'left'),(2,'right'),(6,'cx')]:
    p=np.polyfit(t,r[:,col],1); res=r[:,col]-np.polyval(p,t)
    print(name,'slope %.3f'%p[0],'rms %.2f'%res.std())
print('bottom of dark body median',np.median(r[:,4]))
