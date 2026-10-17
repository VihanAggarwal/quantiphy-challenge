import cv2, numpy as np, math
S='/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/'
for rend in ['a','ax']:
    arr=np.load(S+rend+'.npy')
    print('render',rend)
    for k in list(range(6,27)):
        hsv=cv2.cvtColor(arr[k],cv2.COLOR_BGR2HSV).astype(np.float32)
        # soft orange-ness score
        m=(((hsv[...,0]<22)|(hsv[...,0]>170))&(hsv[...,1]>90)&(hsv[...,2]>50)).astype(np.uint8)
        m[:,600:]=0 if k<12 else m[:,600:]
        m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((5,5),np.uint8))
        m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
        n,lab,st,cen=cv2.connectedComponentsWithStats(m,8)
        i=1+np.argmax(st[1:,4]); mm=(lab==i).astype(np.uint8)
        cnt=max(cv2.findContours(mm,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)[0],key=len)[:,0,:].astype(float)
        # algebraic circle fit on contour pts not on the image border
        p=cnt[(cnt[:,1]<718)&(cnt[:,0]>1)]
        A=np.c_[2*p[:,0],2*p[:,1],np.ones(len(p))]; b=(p**2).sum(1)
        for it in range(3):
            sol,*_=np.linalg.lstsq(A,b,rcond=None)
            xc,yc=sol[0],sol[1]; r=math.sqrt(sol[2]+xc*xc+yc*yc)
            res=np.hypot(p[:,0]-xc,p[:,1]-yc)-r
            keep=np.abs(res)<2.5*res.std()+0.5
            A=A[keep]; b=b[keep]; p=p[keep]
        ys,xs=np.nonzero(mm)
        colc=int(round(xc)); col=ys[xs==colc]
        print(' v%2d c%2d circle=(%.1f,%.1f) D=%.1f  bbox w=%d h=%d  vert-extent@centre=%d-%d (%d)'%(k, math.floor(k*25/24+0.5), xc,yc,2*r, xs.max()-xs.min()+1, ys.max()-ys.min()+1, col.min(),col.max(),col.max()-col.min()+1))
