import cv2, numpy as np
cap=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0059.mp4')
F=[]
while True:
    ok,fr=cap.read()
    if not ok: break
    F.append(cv2.cvtColor(fr,cv2.COLOR_BGR2GRAY).astype(np.float32))
# template: rider head+torso at f24, full-res coords approx (head at ~1066,717; torso to ~1075,760)
f0=24
x0,y0,w,h=1040,710,45,50
T=F[f0][y0:y0+h,x0:x0+w]
prev=x0
res={}
for f in range(18,72):
    # search band
    sx0=max(0,prev-80); sx1=min(2160,prev+w+80)
    S=F[f][y0-15:y0+h+15, sx0:sx1]
    r=cv2.matchTemplate(S,T,cv2.TM_CCOEFF_NORMED)
    _,mx,_,loc=cv2.minMaxLoc(r)
    # subpixel
    px,py=loc
    def sub(a,i):
        if 0<i<len(a)-1:
            d=a[i-1]-2*a[i]+a[i+1]
            return i+0.5*(a[i-1]-a[i+1])/d if d!=0 else i
        return i
    sxp=sub(r[py],px); syp=sub(r[:,px],py)
    u=sx0+sxp; v=y0-15+syp
    res[f]=(u,v,mx); prev=int(round(u))
for f in sorted(res): print(f,'%.2f %.2f %.3f'%res[f])
