import cv2, numpy as np, sys
c=sys.argv[1]
cap=cv2.VideoCapture(f'data/QuantiPhy/{c}.mp4')
F=[]
while True:
    ok,f=cap.read()
    if not ok: break
    F.append(cv2.resize(f,(960,540)))  # half res to save memory
F=np.array(F)
bg=np.median(F,axis=0).astype(np.uint8)
cv2.imwrite('/home/user/quantiphy-challenge/research/next/audit3/sim2_01/png/%s_bg.png'%c,bg)
for i in range(0,50,1):
    d=np.abs(F[i].astype(int)-bg.astype(int)).sum(2)
    m=(d>40).astype(np.uint8)
    hsv=cv2.cvtColor(F[i],cv2.COLOR_BGR2HSV)
    g=cv2.cvtColor(F[i],cv2.COLOR_BGR2GRAY)
    catm=(g<45)
    m2=m.copy(); m2[catm]=0
    m2=cv2.morphologyEx(m2,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m2)
    big=[(st[j,4],j) for j in range(1,n)]
    big.sort(reverse=True)
    j=big[0][1]; x,y,w,h,a=st[j]
    print(i,'dog(half-res) x %d-%d y %d-%d area %d  -> full x %d-%d y %d-%d w %d h %d'%(x,x+w-1,y,y+h-1,a,2*x,2*(x+w),2*y,2*(y+h),2*w,2*h))
