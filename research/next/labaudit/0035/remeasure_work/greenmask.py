import cv2, numpy as np, sys
W='/home/user/quantiphy-challenge/research/next/labaudit/0035/remeasure_work/'
f_=711.; cx,cy=640,360; D=0.232
def measure(v, i, near, rad=70):
    f=np.load(W+v+'.npy')[i].astype(np.int16)
    b,g,r=f[...,0],f[...,1],f[...,2]
    m=~((g>200)&(r<80)&(b<80))
    roi=np.zeros(m.shape,bool); x,y=near; roi[max(0,y-rad):y+rad,max(0,x-rad):x+rad]=True
    m=(m&roi).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    n,lab,st,cc=cv2.connectedComponentsWithStats(m)
    j=1+np.argmax(st[1:,4]); mm=(lab==j).astype(np.uint8)
    cnts,_=cv2.findContours(mm,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    c=max(cnts,key=cv2.contourArea); area=cv2.contourArea(c)
    (ex,ey),(a,bb),ang=cv2.fitEllipse(c)
    eqd=2*np.sqrt(area/np.pi)
    u=np.array([ex-cx,ey-cy,f_]); u/=np.linalg.norm(u); cth=u[2]
    rc=f_*D/(eqd*cth**1.5); rc_minor=f_*D/(min(a,bb)*cth)
    return ex,ey,eqd,min(a,bb),max(a,bb),st[j][2],st[j][3],rc,rc_minor
if __name__=='__main__':
    v=sys.argv[1]; x,y=int(sys.argv[2]),int(sys.argv[3]); frames=eval(sys.argv[4])
    for i in frames:
        r=measure(v,i,(x,y))
        print(v,i,'c=(%.1f,%.1f) eqd=%.1f ell=%.1f/%.1f bbox=%dx%d  rc(eqd)=%.3f rc(minor)=%.3f surf=%.3f'%(r+(r[7]-D/2,)))
        x,y=int(r[0]),int(r[1])
