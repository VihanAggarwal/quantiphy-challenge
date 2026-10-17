import cv2,numpy as np
c=cv2.VideoCapture('data/QuantiPhy/internet_0033.mp4')
F=[]
while True:
    ok,im=c.read()
    if not ok: break
    F.append(im)
print(len(F))
# red tomato centroid: red mask
def red_centroid(im, box):
    x0,y0,x1,y1=box
    hsv=cv2.cvtColor(im[y0:y1,x0:x1],cv2.COLOR_BGR2HSV)
    m=((hsv[...,0]<8)|(hsv[...,0]>172))&(hsv[...,1]>120)&(hsv[...,2]>80)
    ys,xs=np.nonzero(m)
    return (xs.mean()+x0, ys.mean()+y0, m.sum())
for f in [0,5,10,13,20,25,30,35,40,46]:
    print(f, [round(v,1) for v in red_centroid(F[f],(1300,600,2100,1100))])
# bowl rim template tracking: template from frame 0 around bowl (display 540-600,290-350 -> full 1440-1600, 773-933)
T=cv2.cvtColor(F[0][760:950,1420:1620],cv2.COLOR_BGR2GRAY)
for f in [5,10,13]:
    g=cv2.cvtColor(F[f],cv2.COLOR_BGR2GRAY)
    r=cv2.matchTemplate(g[600:1100,1300:2100],T,cv2.TM_CCOEFF_NORMED); _,mv,_,ml=cv2.minMaxLoc(r)
    print('tmpl',f,ml[0]+1300-1420, ml[1]+600-760, round(mv,2))
# camera drift: phase correlation on floor region left
for f in [13,25,40]:
    a=np.float32(cv2.cvtColor(F[0][100:500,0:350],cv2.COLOR_BGR2GRAY)); b=np.float32(cv2.cvtColor(F[f][100:500,0:350],cv2.COLOR_BGR2GRAY))
    print('cam',f,cv2.phaseCorrelate(a,b))
