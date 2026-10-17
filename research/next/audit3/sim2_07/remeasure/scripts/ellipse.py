import cv2, numpy as np, json, sys
vid=sys.argv[1]; b0,b1=[int(x) for x in sys.argv[2].split(',')]; lo,hi=[int(x) for x in sys.argv[3].split(',')]
c=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{vid}.mp4')
fr=[]
while True:
    ok,f=c.read()
    if not ok: break
    fr.append(f)
bg=np.median(np.stack(fr[b0:b1]),axis=0).astype(np.float32)
H,W=fr[0].shape[:2]; cx0,cy0=W/2,H/2
out=[]
for i in range(lo,hi+1):
    f=fr[i].astype(np.float32); d=bg[...,0]-f[...,0]
    m=(d>40).astype(np.uint8)
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    if n<2: continue
    k=1+np.argmax(st[1:,4]); x,y,w,h,a=st[k]
    if x<3 or y<3 or x+w>W-3 or y+h>H-3: continue
    pad=6; x0,y0,x1,y1=x-pad,y-pad,x+w+pad,y+h+pad
    D=d[y0:y1,x0:x1]; core=np.median(D[D>0.7*D.max()])
    U=cv2.resize(D,None,fx=8,fy=8,interpolation=cv2.INTER_CUBIC)
    mu=(U>=core/2).astype(np.uint8)
    cs,_=cv2.findContours(mu,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    cc=max(cs,key=cv2.contourArea)[:,0,:].astype(np.float32)
    pts=np.c_[(cc[:,0]+0.5)/8-0.5+x0,(cc[:,1]+0.5)/8-0.5+y0].astype(np.float32)
    (ex,ey),(ea,eb),ang=cv2.fitEllipse(pts)
    maj,mnr=max(ea,eb),min(ea,eb)
    # orientation of major axis vs radial direction from image center
    majang=ang if ea>=eb else ang+90
    rad=np.degrees(np.arctan2(ey-cy0,ex-cx0))
    dang=((majang-rad+90)%180)-90
    rho=np.hypot(ex-cx0,ey-cy0)
    out.append((i,ex,ey,maj,mnr,dang,rho))
    print(f'{i:2d} c=({ex:7.2f},{ey:7.2f}) rho={rho:6.1f} major={maj:5.2f} minor={mnr:5.2f} sqrt(ab)={np.sqrt(maj*mnr):5.2f} majorVsRadial={dang:6.1f}deg')
O=np.array(out)
print('median minor',np.median(O[:,4]),'median major',np.median(O[:,3]))
json.dump(O.tolist(),open(f'ell_{vid}.json','w'))
