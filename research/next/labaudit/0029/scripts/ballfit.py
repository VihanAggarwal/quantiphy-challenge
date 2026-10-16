import cv2, numpy as np, json
fr='/home/user/quantiphy-challenge/research/next/labaudit/0029/frames/'
f0=711.0
def seg_centre(img):
    hsv=cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
    m=cv2.inRange(hsv,(22,90,90),(45,255,255))
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    k=1+np.argmax(st[1:,4]); return cen[k], st[k]
def fitcircle(P):
    A=np.c_[2*P[:,0],2*P[:,1],np.ones(len(P))]; b=(P**2).sum(1)
    s=np.linalg.lstsq(A,b,rcond=None)[0]; r=np.sqrt(s[2]+s[0]**2+s[1]**2); return s[0],s[1],r
out={}
for i in range(18,49):
    img=cv2.imread(fr+f'rx_{i:02d}.png')
    (cx,cy),st=seg_centre(img)
    g=img.astype(float).sum(2)/3
    pts=[]
    R0=max(st[2],st[3])/2
    for ang in np.deg2rad(np.arange(-175,-4,5)):  # upper half (image y up = negative)
        d=np.array([np.cos(ang),np.sin(ang)])
        rs=np.arange(R0*0.4,R0*1.8,0.25)
        xs=cx+rs*d[0]; ys=cy+rs*d[1]
        vals=cv2.remap(g.astype(np.float32),xs.astype(np.float32)[None],ys.astype(np.float32)[None],cv2.INTER_LINEAR)[0]
        # inside value: median of first part; threshold half to black
        inside=np.median(vals[:len(vals)//4])
        thr=inside/2
        idx=np.where(vals<thr)[0]
        if len(idx)==0: continue
        j=idx[0]
        if vals[min(j+8,len(vals)-1)]>20: continue  # must stay black outside (else table)
        # subpixel
        r=rs[j-1]+(vals[j-1]-thr)/(vals[j-1]-vals[j])*(rs[j]-rs[j-1])
        pts.append((cx+r*d[0],cy+r*d[1]))
    P=np.array(pts)
    if len(P)>=8:
        a,b,r=fitcircle(P)
        out[i]=dict(seg=(round(cx,1),round(cy,1)),circ=(round(a,1),round(b,1)),D=round(2*r,2),n=len(P),R_size=round(f0*6.7/(2*r),1))
        print(i,out[i])
    else: print(i,'few',len(P),round(cx,1),round(cy,1))
json.dump(out,open('/home/user/quantiphy-challenge/research/next/labaudit/0029/scripts/ballfit.json','w'))
