import cv2, numpy as np, sys
D='/home/user/quantiphy-challenge/data/QuantiPhy/'
for v in sys.argv[1:]:
    c=cv2.VideoCapture(D+v+'.mp4'); rows=[]
    i=0
    while True:
        ok,f=c.read()
        if not ok: break
        g=cv2.cvtColor(f,cv2.COLOR_BGR2GRAY)
        # cat region: dark pixels, lower-left; restrict to y 800-940, x<1000 to avoid chairs
        sub=g[780:940,:]
        m=(sub<60).astype(np.uint8)
        n,lab,st,cen=cv2.connectedComponentsWithStats(m)
        if n<2: rows.append((i,np.nan,)*1); i+=1; continue
        k=1+np.argmax(st[1:,4])
        x,y,w,h,a=st[k]
        ys,xs=np.nonzero(lab==k)
        rows.append((i,cen[k][0],cen[k][1]+780,x,x+w-1,y+780,y+h-1+780,a))
        i+=1
    R=np.array([r for r in rows if len(r)==8],float)
    t=R[:,0]
    for j,name in [(1,'cx'),(3,'left'),(4,'right')]:
        p=np.polyfit(t,R[:,j],1); res=R[:,j]-np.polyval(p,t)
        print(v,name,'slope px/frame %.4f'%p[0],'px/s %.2f'%(p[0]*24),'rms %.2f'%res.std())
    print(v,'cy mean %.1f std %.2f'%(R[:,2].mean(),R[:,2].std()),'bottom median',np.median(R[:,6]),'top median',np.median(R[:,5]),'width median',np.median(R[:,4]-R[:,3]+1),'area',np.median(R[:,7]))
    print(v,'first/last cx',R[0,1],R[-1,1],'nframes',len(R))
