import cv2,numpy as np,sys
rend,fr,x0,y0,w=sys.argv[1],int(sys.argv[2]),int(sys.argv[3]),int(sys.argv[4]),int(sys.argv[5])
pts=np.load('/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/edge_%s_%d.npy'%(rend,fr))
im=cv2.imread('/home/user/quantiphy-challenge/research/next/labaudit/0016/frames/f%s_%02d.png'%(rend,fr))
c=im[y0:y0+w,x0:x0+w].copy(); S=4
c=cv2.resize(c,None,fx=S,fy=S,interpolation=cv2.INTER_NEAREST)
for p in pts: cv2.circle(c,(int((p[0]-x0)*S),int((p[1]-y0)*S)),3,(0,0,255),-1)
if len(sys.argv)>6:
    u,v,b,th=map(float,sys.argv[6:10]); 
    ppx=np.array([640.,360.]); x=np.array([u,v])-ppx; ur=x/np.hypot(*x); a=b/np.cos(np.radians(th))
    ang=np.degrees(np.arctan2(ur[1],ur[0]))
    cv2.ellipse(c,(int((u-x0)*S),int((v-y0)*S)),(int(a*S),int(b*S)),ang,0,360,(255,0,0),1)
cv2.imwrite('/home/user/quantiphy-challenge/research/next/labaudit2/0016/img/edge_%s_%d.png'%(rend,fr),c)
