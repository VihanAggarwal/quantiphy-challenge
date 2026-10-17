import cv2, numpy as np
p='/home/user/quantiphy-challenge/data/QuantiPhy/internet_0037.mp4'
cap=cv2.VideoCapture(p)
ref=None; rows=[]
i=0
while True:
    ok,im=cap.read()
    if not ok: break
    sm=cv2.resize(im,None,fx=0.5,fy=0.5,interpolation=cv2.INTER_AREA)
    # camera drift: phase correlation on coping strip (top) full width
    strip=cv2.cvtColor(sm[0:85,:],cv2.COLOR_BGR2GRAY).astype(np.float32)
    if ref is None: ref=strip; sh=(0.0,0.0)
    else:
        (dx,dy),r=cv2.phaseCorrelate(ref,strip); sh=(dx*2,dy*2)
    roi=sm[300:650,:].astype(np.int16)
    b,g,r_=roi[...,0],roi[...,1],roi[...,2]
    v=roi.max(2)
    hair=(v<70)&(r_>=g-5)   # dark, not teal
    skin=(r_>g+15)&(r_>b+25)&(r_>110)
    ys,xs=np.nonzero(hair)
    ys2,xs2=np.nonzero(skin)
    def cen(xs,ys):
        if len(xs)<20: return (np.nan,np.nan,0)
        mx=np.median(xs); keep=np.abs(xs-mx)<300
        return (xs[keep].mean()*2, (ys[keep].mean()+300)*2, keep.sum())
    h=cen(xs,ys); s=cen(xs2,ys2)
    # skin extent
    if len(xs2)>50:
        x_lo=np.percentile(xs2,1)*2; x_hi=np.percentile(xs2,99)*2
    else: x_lo=x_hi=np.nan
    rows.append((i,sh[0],sh[1],h[0],h[1],h[2],s[0],s[1],s[2],x_lo,x_hi))
    i+=1
R=np.array(rows)
np.savetxt('sw_track.txt',R,fmt='%.1f',header='f camdx camdy hairx hairy hairn skinx skiny skinn skinx1 skinx99')
for r in R[::10]: print(' '.join('%.0f'%v for v in r))
