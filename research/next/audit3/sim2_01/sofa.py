import cv2, numpy as np, sys
c=sys.argv[1]
cap=cv2.VideoCapture(f'data/QuantiPhy/{c}.mp4'); ok,f=cap.read()
g=cv2.cvtColor(f,cv2.COLOR_BGR2GRAY)
m=(g>142).astype(np.uint8)
m[:, :170]=0; m[:, 1760:]=0; m[:300]=0
m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((5,5),np.uint8))
n,lab,st,cen=cv2.connectedComponentsWithStats(m)
for j in range(1,n):
    if st[j,4]>5000: print('comp',st[j])
# sofa: columns x>=560 ; carpet: x<560
ys,xs=np.nonzero(m)
sel=xs>=600
print('sofa-ish x %d-%d y %d-%d'%(xs[sel].min(),xs[sel].max(),ys[sel].min(),ys[sel].max()))
# carpet: rows extents in x<580
for y in range(380,900,40):
    r=np.nonzero(m[y,170:600])[0]
    print('carpet row',y,(170+r.min(),170+r.max()) if len(r) else '-')
for x in range(250,560,40):
    r=np.nonzero(m[300:1000,x])[0]
    print('carpet col',x,(300+r.min(),300+r.max()) if len(r) else '-')
