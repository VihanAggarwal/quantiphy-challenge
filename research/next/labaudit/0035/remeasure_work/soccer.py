import cv2, numpy as np
W='/home/user/quantiphy-challenge/research/next/labaudit/0035/remeasure_work/'
B=np.load(W+'captured_0035b.npy'); med=cv2.imread(W+'b_median.png')
cx,cy,f=640,360,711.
near=(437,683)
out=[]
for i in range(len(B)):
    d=np.abs(B[i].astype(np.int16)-med.astype(np.int16)).max(axis=2)
    hsv=cv2.cvtColor(B[i],cv2.COLOR_BGR2HSV)
    for thr in (40,):
        m=(d>thr)&(hsv[...,1]<70)   # not orange
        roi=np.zeros(m.shape,bool); x,y=near; roi[max(0,y-50):y+50,max(0,x-50):x+50]=True
        m=(m&roi).astype(np.uint8)
        m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((7,7),np.uint8))
        m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
        n,lab,st,cc=cv2.connectedComponentsWithStats(m)
        if n<2: print(i,'none'); continue
        j=1+np.argmax(st[1:,4]); mm=(lab==j).astype(np.uint8)
        cnts,_=cv2.findContours(mm,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
        c=max(cnts,key=cv2.contourArea); area=cv2.contourArea(c)
        (ex,ey),(a,b),ang=cv2.fitEllipse(c)
        u=np.array([ex-cx,ey-cy,f]); u/=np.linalg.norm(u)
        out.append((i,ex,ey,2*np.sqrt(area/np.pi),min(a,b),max(a,b),u[2]))
        print('%2d c=(%.1f,%.1f) eqd=%.1f ell=%.1f/%.1f bbox=%dx%d cos=%.3f'%(i,ex,ey,2*np.sqrt(area/np.pi),min(a,b),max(a,b),st[j][2],st[j][3],u[2]))
        near=(int(ex),int(ey))
np.save(W+'soccer_track.npy',np.array(out))
