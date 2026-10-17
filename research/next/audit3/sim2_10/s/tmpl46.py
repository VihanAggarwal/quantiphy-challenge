import cv2, numpy as np
c='simulation_0246'
cap=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{c}.mp4')
fr=[]
while True:
    ok,im=cap.read()
    if not ok: break
    fr.append(cv2.cvtColor(im,cv2.COLOR_BGR2GRAY))
ref=37
# patches (x0,y0,w,h) in frame 37, from mask visual (half-scale coords *2)
P={'tuft':(640,555,60,45),'torso_rump':(800,520,100,100),'torso_mid':(950,515,100,110),'head':(1195,525,110,95),'rabbit':(1245,310,100,65)}
b=np.loadtxt('/home/user/quantiphy-challenge/research/next/audit3/sim2_10/top46.csv',delimiter=',')
for nm,(x0,y0,w,h) in P.items():
    T=fr[ref][y0:y1] if False else fr[ref][y0:y0+h,x0:x0+w]
    xs=[];sc=[]
    for i,g in enumerate(fr):
        guess = x0 + (i-ref)*9.2 if nm!='rabbit' else x0+(i-ref)*8.6
        gx0=int(max(0,guess-80)); gx1=int(min(g.shape[1],guess+w+80))
        S=g[max(0,y0-60):y0+h+60, gx0:gx1]
        if S.shape[1]<w+2: xs.append(np.nan); sc.append(0); continue
        r=cv2.matchTemplate(S,T,cv2.TM_CCOEFF_NORMED)
        _,mx,_,loc=cv2.minMaxLoc(r)
        xs.append(gx0+loc[0]); sc.append(mx)
    xs=np.array(xs,float); sc=np.array(sc); t=np.arange(len(xs))
    ok=(sc>0.5)&~np.isnan(xs)
    p=np.polyfit(t[ok],xs[ok],1)
    res=xs[ok]-np.polyval(p,t[ok])
    print(f'{nm:11s} slope {p[0]:.3f} px/f  n_ok {ok.sum()} score med {np.median(sc):.2f} resid sd {res.std():.1f}')
