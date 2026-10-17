import cv2,numpy as np
c=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/internet_0024.mp4')
fr=[]
while True:
    ok,f=c.read()
    if not ok: break
    fr.append(cv2.cvtColor(cv2.resize(f,None,fx=0.5,fy=0.5,interpolation=cv2.INTER_AREA),cv2.COLOR_BGR2GRAY))
# template: mug at frame k, box around coffee found by thresholding near expected center
def coffee(g,guess):
    m=(g<50).astype(np.uint8); m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((9,9),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    best=None
    for j in range(1,n):
        if st[j,4]<5000: continue
        d=np.hypot(cen[j][0]-guess[0],cen[j][1]-guess[1])
        if best is None or d<best[0]: best=(d,j)
    j=best[1]; return cen[j],st[j]
g=(1615,653)
pos=[]
for k in range(len(fr)):
    cc,st=coffee(fr[k],g); g=cc; pos.append(cc)
    print(k,'coffee centre full-res (%.0f,%.0f) w%d h%d area%d'%(cc[0]*2,cc[1]*2,st[2]*2,st[3]*2,st[4]*4))
# template matching of mug patch frame k -> k+1
for k in range(9,16):
    cx,cy=map(int,pos[k]); r=130
    T=fr[k][cy-r:cy+r,cx-r:cx+r]
    S=fr[k+1]
    res=cv2.matchTemplate(S,T,cv2.TM_CCOEFF_NORMED); _,mx,_,loc=cv2.minMaxLoc(res)
    dx=loc[0]+r-cx; dy=loc[1]+r-cy
    print('TM %d->%d d=(%d,%d) full-res step %.1f score %.2f'%(k,k+1,dx*2,dy*2,2*np.hypot(dx,dy),mx))
