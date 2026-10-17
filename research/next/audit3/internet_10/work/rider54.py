import cv2,numpy as np
c=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/internet_0054.mp4')
fr=[]
while True:
    ok,f=c.read()
    if not ok: break
    fr.append(cv2.resize(f,None,fx=0.5,fy=0.5,interpolation=cv2.INTER_AREA))
print(len(fr))
g0=cv2.cvtColor(fr[0],cv2.COLOR_BGR2GRAY).astype(np.float32)
# camera shift via phase correlation on building region (top-left), half-res
win=np.s_[40:330,40:880]
sh=[]
for k,f in enumerate(fr):
    g=cv2.cvtColor(f,cv2.COLOR_BGR2GRAY).astype(np.float32)
    (dx,dy),r=cv2.phaseCorrelate(g0[win],g[win]); sh.append((dx,dy))
sh=np.array(sh)
np.save('/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/sh54.npy',sh)
for k in range(0,len(fr),6): print(k,'shift half-res %.2f %.2f'%tuple(sh[k]))
# rider: white shirt mask (bright, low sat) in region y 380-600 half-res
for k in range(0,len(fr),3):
    hsv=cv2.cvtColor(fr[k],cv2.COLOR_BGR2HSV)
    reg=hsv[380:580,:]
    m=((reg[:,:,2]>200)&(reg[:,:,1]<40)).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    c2=[(st[j,4],j) for j in range(1,n) if 60<st[j,4]<3000 and st[j,3]>8]
    s=' '.join('(%.0f,%.0f a%d)'%(cen[j][0],cen[j][1]+380,a) for a,j in sorted(c2,reverse=True)[:3])
    print(k,s)
