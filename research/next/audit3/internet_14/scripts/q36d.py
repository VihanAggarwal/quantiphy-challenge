import cv2,numpy as np
c=cv2.VideoCapture('data/QuantiPhy/internet_0036.mp4')
G=[]
while True:
    ok,im=c.read()
    if not ok: break
    G.append(cv2.cvtColor(cv2.resize(im,None,fx=0.5,fy=0.5,interpolation=cv2.INTER_AREA),cv2.COLOR_BGR2GRAY))
def chain(f0,f1,center,half=60,search=200,step=1):
    cx,cy=center[0]/2,center[1]/2
    pos=[(f0,cx*2,cy*2)]
    for f in range(f0,f1,step):
        x0,y0=int(cx-half),int(cy-half)
        T=G[f][y0:y0+2*half,x0:x0+2*half]
        sx0,sy0=max(0,x0-search),max(0,y0-search)
        R=G[f+step][sy0:y0+2*half+search, sx0:x0+2*half+search]
        r=cv2.matchTemplate(R,T,cv2.TM_CCOEFF_NORMED); _,mv,_,ml=cv2.minMaxLoc(r)
        nx,ny=sx0+ml[0],sy0+ml[1]
        cx+=nx-x0; cy+=ny-y0
        pos.append((f+step,cx*2,cy*2,round(mv,2)))
    return pos
# top hand back-of-hand (knuckles) at f35 ~ (1100,1250) full
p=chain(35,54,(1100,1300),half=70,search=220)
for q in p: print('top',q)
# bottom hand back at f12: hand comp centroid (816,2898) full
p=chain(12,35,(900,2750),half=70,search=150)
for q in p[::4]+[p[-1]]: print('bot',q)
