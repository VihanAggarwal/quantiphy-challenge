import cv2, numpy as np, sys
W='/home/user/quantiphy-challenge/research/next/labaudit/0035/remeasure_work/'
v=sys.argv[1]
F=np.load(W+v+'.npy')
cent=np.load(W+'captured_0035b_cent.npy')
cx,cy=640,360
rows=[]
for i in range(len(F)):
    f=F[i].astype(np.int16)
    if v.endswith('x'):
        m=(255-f.min(axis=2))>60
    else:
        bg=np.array([0]) # s render: background varies; use orange-ness
        hsv=cv2.cvtColor(F[i],cv2.COLOR_BGR2HSV)
        m=(hsv[...,1]>90)&((hsv[...,0]<25)|(hsv[...,0]>170))
    x0,y0=cent[i]
    roi=np.zeros_like(m); roi[int(y0)-55:int(y0)+55,int(x0)-55:int(x0)+55]=True
    m=(m&roi).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((5,5),np.uint8))
    n,lab,st,cc=cv2.connectedComponentsWithStats(m)
    j=1+np.argmax(st[1:,4]); mm=(lab==j).astype(np.uint8)
    # fill holes
    cnts,_=cv2.findContours(mm,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    c=max(cnts,key=cv2.contourArea)
    area=cv2.contourArea(c)
    (ex,ey),(a,b),ang=cv2.fitEllipse(c)
    # widths along radial / tangential directions via projection of contour
    rad=np.array([ex-cx,ey-cy]); rad=rad/np.linalg.norm(rad); tang=np.array([-rad[1],rad[0]])
    P=c[:,0,:].astype(float)
    wr=np.ptp(P@rad); wt=np.ptp(P@tang)
    mv=cent[min(i+1,len(F)-1)]-cent[max(i-1,0)]
    if np.linalg.norm(mv)<3: mv=np.array([1.,0.])
    mv=mv/np.linalg.norm(mv); pp=np.array([-mv[1],mv[0]])
    wp=np.ptp(P@pp); wm=np.ptp(P@mv)
    rows.append((i,ex,ey,area,2*np.sqrt(area/np.pi),min(a,b),max(a,b),wr,wt,wp,wm))
    print('%2d c=(%.1f,%.1f) area=%.0f eqd=%.2f ell=%.1f/%.1f rad=%.1f tang=%.1f perpmv=%.1f alongmv=%.1f'%rows[-1])
np.save(W+v+'_mask.npy',np.array(rows))
