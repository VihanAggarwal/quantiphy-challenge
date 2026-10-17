import cv2,numpy as np
def fr(clip,k):
    c=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/internet_{clip}.mp4'); c.set(cv2.CAP_PROP_POS_FRAMES,k); ok,f=c.read(); return cv2.cvtColor(f,cv2.COLOR_BGR2GRAY)
a=fr('0060',100); b=fr('0063',90)
sift=cv2.SIFT_create(8000)
for name,(xa,xb) in {'wall':(0,1300),'floor':(1520,1920),'all':(0,1920)}.items():
    ma=np.zeros_like(a); ma[:,xa:xb]=255; mb=np.zeros_like(b); mb[:,xa:xb]=255
    ka,da=sift.detectAndCompute(a,ma); kb,db=sift.detectAndCompute(b,mb)
    m=cv2.BFMatcher().knnMatch(da,db,k=2)
    good=[p[0] for p in m if len(p)==2 and p[0].distance<0.75*p[1].distance]
    pa=np.float32([ka[g.queryIdx].pt for g in good]); pb=np.float32([kb[g.trainIdx].pt for g in good])
    if len(good)<6: print(name,'few',len(good)); continue
    M,inl=cv2.estimateAffinePartial2D(pa,pb,ransacReprojThreshold=3)
    s=np.hypot(M[0,0],M[1,0]); print(name,len(good),int(inl.sum()),'scale b/a=%.4f rot=%.2f deg'%(s,np.degrees(np.arctan2(M[1,0],M[0,0]))),M[:,2])
    H,inl2=cv2.findHomography(pa,pb,cv2.RANSAC,3)
    print('  H inliers',int(inl2.sum()))
    ii=inl.ravel()>0
    print('  inlier x range a',pa[ii,0].min(),pa[ii,0].max(),'y',pa[ii,1].min(),pa[ii,1].max())
