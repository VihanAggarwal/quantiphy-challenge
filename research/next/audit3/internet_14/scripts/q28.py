import cv2,numpy as np
c=cv2.VideoCapture('data/QuantiPhy/internet_0028.mp4')
G=[]
while True:
    ok,im=c.read()
    if not ok: break
    G.append(cv2.resize(cv2.cvtColor(im,cv2.COLOR_BGR2GRAY),None,fx=0.5,fy=0.5))
print(len(G))
# blue bag template at frame 0: half-res region x 300-1400, y 600-1000 ; track
def track(f0,box,n):
    x0,y0,x1,y1=box
    T=G[f0][y0:y1,x0:x1]
    out=[]
    for k in range(f0+1,min(f0+n,len(G))):
        r=cv2.matchTemplate(G[k],T,cv2.TM_CCOEFF_NORMED); _,mv,_,ml=cv2.minMaxLoc(r)
        out.append((k,ml[0]-x0,ml[1]-y0,round(mv,2)))
        if mv<0.5: break
    return out
print('blue logo region', track(0,(900,550,1250,800),12))
print('belt emboss region', track(0,(150,250,1250,500),10))
