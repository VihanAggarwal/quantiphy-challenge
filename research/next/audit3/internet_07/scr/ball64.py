import cv2, numpy as np
W='/home/user/quantiphy-challenge/research/next/audit3/internet_07/'
cap=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/internet_0064.mp4'); f=0; out=[]
while True:
    ok,im=cap.read()
    if not ok: break
    b,g,r=[im[:,:,i].astype(np.float32) for i in range(3)]
    red=r-(g+b)/2
    for thr in (30,22):
        m=(red>thr).astype(np.uint8)
        m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((5,5),np.uint8))
        n,lab,st,cen=cv2.connectedComponentsWithStats(m)
        cands=[]
        for i in range(1,n):
            x,y,w,h,a=st[i]
            if not (60<=w<=120 and 60<=h<=120): continue
            if a<0.6*w*h: continue
            cands.append((abs(w-h),x,y,w,h,a,cen[i][0],cen[i][1]))
        if cands: break
    if cands:
        c=min(cands)
        out.append((f,c[6],c[7],c[1],c[2],c[3],c[4],c[5],thr))
    f+=1
out=np.array(out); np.savetxt(W+'ball64.txt',out,fmt='%.2f')
for r in out: print('%d c=(%.1f,%.1f) box x%d y%d w%d h%d a%d thr%d'%tuple(r))
