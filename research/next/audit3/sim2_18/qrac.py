from util import *
import sys
v=sys.argv[1]; thr=float(sys.argv[2]); ymax=int(sys.argv[3]) if len(sys.argv)>3 else 99999
fr=frames(v)
gs=[cv2.GaussianBlur(cv2.cvtColor(f,cv2.COLOR_BGR2GRAY),(5,5),0) for i,f in fr]
bg=np.median(np.stack(gs[::3]),axis=0)
rows=[]
for i,g in enumerate(gs):
    d=np.abs(g.astype(float)-bg)
    m=(d>thr).astype(np.uint8); m[ymax:]=0
    m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((5,5),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    k=1+np.argmax(st[1:,4])
    # merge components within 40 px of main bbox
    x0,y0,w,h=st[k,:4]; x1,y1=x0+w,y0+h
    for j in range(1,n):
        if j==k or st[j,4]<30: continue
        a,b,c,dd=st[j,:4]
        if a<x1+40 and a+c>x0-40 and b<y1+40 and b+dd>y0-40:
            x0=min(x0,a);y0=min(y0,b);x1=max(x1,a+c);y1=max(y1,b+dd)
    rows.append((i,x0,x1,y0,y1,x1-x0,y1-y0,cen[k][0],cen[k][1]))
a=np.array(rows,float)
np.set_printoptions(suppress=True,linewidth=160,precision=1)
print(a[::3])
print('median len',np.median(a[:,5]),'median h',np.median(a[:,6]))
for c,name in [(1,'xmin'),(2,'xmax'),(7,'cx')]:
    p=np.polyfit(a[2:,0],a[2:,c],1); print(name,'slope px/f %.2f'%p[0], 'x24-x12 %.1f'%(a[24,c]-a[12,c]), 'x24-x23 %.1f'%(a[24,c]-a[23,c]))
