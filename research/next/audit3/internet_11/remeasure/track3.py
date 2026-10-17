import cv2, numpy as np
p='data/QuantiPhy/internet_0047.mp4'
c=cv2.VideoCapture(p); fr=[]
while True:
    ok,f=c.read()
    if not ok: break
    fr.append(f)
g=[cv2.cvtColor(f,cv2.COLOR_BGR2GRAY) for f in fr]
orb=cv2.ORB_create(6000); bf=cv2.BFMatcher(cv2.NORM_HAMMING,crossCheck=True)
REF=15
kr,dr=orb.detectAndCompute(g[REF],None)
al=[];Hs=[]
for i in range(30):
    k,d=orb.detectAndCompute(g[i],None); m=bf.match(d,dr)
    src=np.float32([k[x.queryIdx].pt for x in m]); dst=np.float32([kr[x.trainIdx].pt for x in m])
    H,_=cv2.findHomography(src,dst,cv2.RANSAC,1.5)
    Hs.append(H)
    al.append(cv2.warpPerspective(fr[i],H,(1920,1080),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REPLICATE).astype(np.float32))
bg=np.median(np.stack(al),axis=0)
lab=cv2.cvtColor(bg.astype(np.uint8),cv2.COLOR_BGR2Lab).astype(np.float32)
out=[]
for i in range(3,24):
    L=cv2.cvtColor(al[i].astype(np.uint8),cv2.COLOR_BGR2Lab).astype(np.float32)
    d=np.sqrt(((L-lab)**2).sum(axis=2))
    d=cv2.GaussianBlur(d,(3,3),0)
    m0=(d>25).astype(np.uint8)
    m0=cv2.morphologyEx(m0,cv2.MORPH_OPEN,np.ones((7,7),np.uint8))
    n,labl,st,cen=cv2.connectedComponentsWithStats(m0)
    j=1+np.argmax(st[1:,4]); x,y,w,h,a=st[j]
    roi=d[max(y-20,0):y+h+20, max(x-20,0):x+w+20]
    ox,oy=max(x-20,0),max(y-20,0)
    full=np.percentile(roi[roi>25],60)
    row=[i]
    for th in (0.3,0.5,0.7):
        mm=(roi>th*full).astype(np.uint8)
        mm=cv2.morphologyEx(mm,cv2.MORPH_CLOSE,np.ones((15,15),np.uint8))
        nn,ll,ss,cc=cv2.connectedComponentsWithStats(mm)
        jj=1+np.argmax(ss[1:,4])
        # fill holes
        blob=(ll==jj).astype(np.uint8)
        cnts,_=cv2.findContours(blob,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
        cv2.drawContours(blob,cnts,-1,1,-1)
        M=cv2.moments(blob,True)
        row+= [M['m10']/M['m00']+ox, M['m01']/M['m00']+oy]
    # alpha-weighted centroid
    al_=np.clip(roi/full,0,1)
    yy,xx=np.mgrid[0:roi.shape[0],0:roi.shape[1]]
    row+=[(al_*xx).sum()/al_.sum()+ox,(al_*yy).sum()/al_.sum()+oy]
    out.append(row)
    print('%2d '%i+' '.join('%.1f'%v for v in row[1:]))
out=np.array(out)
np.savetxt('research/next/audit3/internet_11/remeasure/track47c.txt',out,fmt='%.3f')
# camera: where does a floor point move? print H translation at image center for info
for i in (0,10,15,20,29):
    pt=cv2.perspectiveTransform(np.float32([[[960,540]]]),Hs[i])[0,0]
    print('H',i,pt)
