import cv2, numpy as np, json, sys
tag=sys.argv[1] if len(sys.argv)>1 else 'a'; f=float(sys.argv[2]) if len(sys.argv)>2 else 775.
E=json.load(open('/home/user/quantiphy-challenge/research/next/labaudit2/0031/remeasure_b/edge_%s.json'%tag))
def cap(k): return k if k<=11 else (k+1 if k<=35 else k+2)
P=np.load('/home/user/quantiphy-challenge/research/next/labaudit2/0031/remeasure_b/corners.npy')
W,D=60.3,76.0
obj=np.array([[-W/2,D,0],[W/2,D,0],[W/2,0,0],[-W/2,0,0]],float)
K=np.array([[f,0,640],[0,f,360],[0,0,1]])
ok,rv,tv=cv2.solvePnP(obj,P,K,None,flags=cv2.SOLVEPNP_IPPE)
Rm,_=cv2.Rodrigues(rv); C=(-Rm.T@tv).ravel()
Rb={'t':3.35,'w':2.0}
for b,lo,hi in (('t',20,43),('w',20,50)):
    rows=[]
    for o in E:
        if b not in o: continue
        c=cap(o['i'])
        if c<lo or c>hi: continue
        u,v=o[b][0],o[b][1]
        d=np.array([(u-640)/f,(v-360)/f,1.]); dw=Rm.T@d
        s=(Rb[b]-C[2])/dw[2]; X=C+s*dw
        rows.append((c,*X))
    A=np.array(rows); c=A[:,0]
    print(b, 'X,Y on table (cm) by capture frame:')
    print('  '+' '.join('%d:(%.1f,%.1f)'%(r[0],r[1],r[2]) for r in A))
    for l2,h2 in ((lo,hi),(lo+5,hi),(30,hi),(34,hi),(36,hi)):
        sel=(c>=l2)&(c<=h2)
        p1=[np.polyfit(c[sel],A[sel,j],1)[0] for j in (1,2)]
        p2=[np.polyfit(c[sel],A[sel,j],2) for j in (1,2)]
        v2=[np.polyval(np.polyder(p),40.5) for p in p2]
        print('  [%d-%d] linear speed %.1f cm/s; quad speed@40.5 %.1f cm/s; quad accel %.1f cm/s2'%(l2,h2,25*np.hypot(*p1),25*np.hypot(*v2), 625*2*np.hypot(p2[0][0],p2[1][0])*np.sign(-p2[1][0]*np.sign(p1[1]))))
