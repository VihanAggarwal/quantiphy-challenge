import numpy as np
D='/home/user/quantiphy-challenge/research/next/labaudit2/0023/'
for V in ['captured_0023x','captured_0023s','captured_0023']:
    A=np.load(D+f'frames/avg_{V}_slope.npy')
    # cover color: light blue (R~178,G~207,B~209); board white (~250); background black/blue/blur
    R,G,B=A[...,2],A[...,1],A[...,0]
    blu=(G-R)  # cover: G-R ~ 30; board white ~0; black 0; skin negative
    rows=[]
    for y in range(352,378):
        p=blu[y-300]
        # left end: scan x from 505 rightward, crossing of level 15
        def cr(x0,x1,step,lev=15):
            prev=None
            for x in range(x0,x1,step):
                v=p[x-400]
                if prev is not None and (prev-lev)*(v-lev)<=0 and v!=prev: return x-step+step*(lev-prev)/(v-prev)
                prev=v
            return np.nan
        xl=cr(505,580,1); xr=cr(690,600,-1)
        rows.append((y,xl,xr))
    rows=np.array(rows)
    print(V)
    for r in rows[::3]: print('  y %d  L %.2f  R %.2f  len %.2f'%(r[0],r[1],r[2],r[2]-r[1]))
    m=(rows[:,0]>=356)&(rows[:,0]<=374)
    aL,bL=np.polyfit(rows[m,0],rows[m,1],1); aR,bR=np.polyfit(rows[m,0],rows[m,2],1)
    yv=(bR-bL)/(aL-aR); xv=aL*yv+bL
    print('  left x=%.4f y+%.1f  right x=%.4f y+%.1f  cover-side VP (%.1f, %.1f)'%(aL,bL,aR,bR,xv,yv))
    yb,yf=349.9,379.0
    Lb=(aR*yb+bR)-(aL*yb+bL); Lf=(aR*yf+bR)-(aL*yf+bL)
    print('  extrapolated length at back %.2f px, at front %.2f px, ratio Zb/Zf=%.4f'%(Lb,Lf,Lf/Lb))
