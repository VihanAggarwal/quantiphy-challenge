import cv2,numpy as np
v=cv2.VideoCapture('data/QuantiPhy/internet_0051.mp4')
fr=[]
while True:
    ok,im=v.read()
    if not ok: break
    fr.append(im)
print(len(fr))
g=[cv2.cvtColor(f,cv2.COLOR_BGR2GRAY).astype(np.float32) for f in fr]
# background shift: rows 100-560 (trees, above cars), whole width; and car row 600-800 cols excluding rider? use ORB similarity
orb=cv2.ORB_create(4000)
def H(a,b,mask):
    k1,d1=orb.detectAndCompute(a.astype(np.uint8),mask); k2,d2=orb.detectAndCompute(b.astype(np.uint8),mask)
    m=cv2.BFMatcher(cv2.NORM_HAMMING,crossCheck=True).match(d1,d2)
    p1=np.float32([k1[x.queryIdx].pt for x in m]); p2=np.float32([k2[x.trainIdx].pt for x in m])
    A,inl=cv2.estimateAffinePartial2D(p1,p2,ransacReprojThreshold=2)
    return A,inl.sum()
mask=np.zeros(g[0].shape,np.uint8); mask[600:830,:]=255  # car row
mask2=np.zeros(g[0].shape,np.uint8); mask2[50:560,:]=255
for f in (12,24,36,49):
    A,n=H(g[0],g[f],mask); B,n2=H(g[0],g[f],mask2)
    print(f,'carrow tx %.1f ty %.1f s %.4f n%d'%(A[0,2],A[1,2],np.hypot(A[0,0],A[1,0]),n),' trees tx %.1f ty %.1f s %.4f n%d'%(B[0,2],B[1,2],np.hypot(B[0,0],B[1,0]),n2))
