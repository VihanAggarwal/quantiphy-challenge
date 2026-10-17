import numpy as np, cv2
D='/home/user/quantiphy-challenge/research/next/labaudit2/0023/'
for V in ['captured_0023x','captured_0023s']:
  for ph in ['table','slope']:
    im=cv2.imread(D+f'frames/avg_{V}_{ph}.png').astype(np.float32)
    B,G,R=im[...,0],im[...,1],im[...,2]
    s=R-B   # wood: R-B ~ 50; black bg: 0; blue bg (s render): negative
    L=[];Rr=[]
    for y in range(452,524):
        p=s[y]
        def cross(xs,lev=25):
            prev=None
            for x in xs:
                v=p[x]
                if prev is not None and (prev-lev)*(v-lev)<=0 and v!=prev:
                    return xp+(lev-prev)/(v-prev)*(x-xp)
                prev=v; xp=x
            return np.nan
        L.append((y,cross(range(250,480)))); Rr.append((y,cross(range(1000,760,-1))))
    L=np.array(L); Rr=np.array(Rr)
    aL,bL=np.polyfit(L[:,0],L[:,1],1); aR,bR=np.polyfit(Rr[:,0],Rr[:,1],1)
    q2L=np.polyfit(L[:,0],L[:,1],2)[0]; q2R=np.polyfit(Rr[:,0],Rr[:,1],2)[0]
    yv=(bR-bL)/(aL-aR); xv=aL*yv+bL
    rs=np.std(L[:,1]-(aL*L[:,0]+bL)); rr=np.std(Rr[:,1]-(aR*Rr[:,0]+bR))
    print(V,ph,'table side VP (%.1f, %.1f); resid %.2f %.2f; quad coef %.5f %.5f'%(xv,yv,rs,rr,q2L,q2R))
