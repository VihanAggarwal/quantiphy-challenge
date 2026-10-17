import cv2, numpy as np
p='data/QuantiPhy/internet_0047.mp4'
c=cv2.VideoCapture(p); fr=[]
while True:
    ok,f=c.read()
    if not ok: break
    fr.append(cv2.cvtColor(f,cv2.COLOR_BGR2GRAY))
print(len(fr))
# frame-to-frame absolute diff stats to detect duplicates
for i in range(1,len(fr)):
    d=np.abs(fr[i].astype(int)-fr[i-1].astype(int)).mean()
    print(i, round(d,2), end='; ')
print()
# homography of each frame to ref frame 29 using ORB with ball region excluded via bottom/region masks
ref=fr[29]
orb=cv2.ORB_create(5000)
def feats(img,mask=None):
    return orb.detectAndCompute(img,mask)
kr,dr=feats(ref)
bf=cv2.BFMatcher(cv2.NORM_HAMMING,crossCheck=True)
for i in range(30):
    k,d=feats(fr[i])
    m=bf.match(d,dr)
    src=np.float32([k[x.queryIdx].pt for x in m]); dst=np.float32([kr[x.trainIdx].pt for x in m])
    H,inl=cv2.findHomography(src,dst,cv2.RANSAC,2.0)
    A,inl2=cv2.estimateAffinePartial2D(src,dst,method=cv2.RANSAC,ransacReprojThreshold=2.0)
    s=np.hypot(A[0,0],A[1,0]); ang=np.degrees(np.arctan2(A[1,0],A[0,0]))
    print(i, 'n',int(inl.sum()), 'sim tx %.1f ty %.1f s %.4f rot %.3f'%(A[0,2],A[1,2],s,ang))
