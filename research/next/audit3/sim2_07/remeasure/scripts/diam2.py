import cv2, numpy as np, json, sys
vid=sys.argv[1]; b0,b1=[int(x) for x in sys.argv[2].split(',')]; fsel=sys.argv[3]
c=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{vid}.mp4')
fr=[]
while True:
    ok,f=c.read()
    if not ok: break
    fr.append(f)
bg=np.median(np.stack(fr[b0:b1]),axis=0).astype(np.float32)
lo,hi=[int(x) for x in fsel.split(',')]
def circfit(x,y):
    A=np.c_[2*x,2*y,np.ones_like(x)]; b=x**2+y**2
    s=np.linalg.lstsq(A,b,rcond=None)[0]; r=np.sqrt(s[2]+s[0]**2+s[1]**2); return s[0],s[1],r
rows=[]
for i in range(lo,hi+1):
    f=fr[i].astype(np.float32)
    d=bg[...,0]-f[...,0]
    m=(d>40).astype(np.uint8)
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    if n<2: continue
    k=1+np.argmax(st[1:,4]); x,y,w,h,a=st[k]
    if x<3 or y<3 or x+w>1917 or y+h>1077: continue
    pad=6; x0,y0,x1,y1=x-pad,y-pad,x+w+pad,y+h+pad
    D=d[y0:y1,x0:x1]
    core=np.median(D[D>0.7*D.max()])
    eq=2*np.sqrt((D>=core/2).sum()/np.pi)
    # partial-volume area with clipping to [0,1], exclude far pixels
    pv=np.clip(D/core,0,1); pv[pv<0.25]=0
    eqpv=2*np.sqrt(pv.sum()/np.pi)
    # subpixel half-level contour via upsampling x8
    U=cv2.resize(D,None,fx=8,fy=8,interpolation=cv2.INTER_CUBIC)
    mu=(U>=core/2).astype(np.uint8)
    cs,_=cv2.findContours(mu,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    cc=max(cs,key=cv2.contourArea)[:,0,:].astype(np.float64)
    px=(cc[:,0]+0.5)/8-0.5+x0; py=(cc[:,1]+0.5)/8-0.5+y0
    cxa,cya,ra=circfit(px,py)
    # fit only the upper-left half (angle between 90..360 in image coords? use points with (px-cx)+(py-cy)<0 -> upper-left side)
    sel=((px-cxa)+(py-cya))<0
    cxu,cyu,ru=circfit(px[sel],py[sel])
    rows.append((i,eq,eqpv,2*ra,2*ru,cxa,cya,cxu,cyu))
    print(f'{i:2d} eq={eq:.2f} eqpv={eqpv:.2f} circAll={2*ra:.2f} circUL={2*ru:.2f} c=({cxa:.2f},{cya:.2f}) cUL=({cxu:.2f},{cyu:.2f}) core={core:.0f}')
R=np.array([r[1:5] for r in rows])
print('median eq,eqpv,circAll,circUL',np.median(R,0).round(2))
json.dump([[float(v) for v in r] for r in rows],open(f'diam2_{vid}.json','w'))
