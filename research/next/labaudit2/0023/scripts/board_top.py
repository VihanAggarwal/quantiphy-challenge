import numpy as np
D='/home/user/quantiphy-challenge/research/next/labaudit2/0023/'
for V in ['captured_0023x']:
  for ph in ['slope','table']:
    A=np.load(D+f'frames/avg_{V}_{ph}.npy'); lum=A.mean(-1)
    print(V,ph)
    for y in [358,360,362,364,366,370,375,380,390,400,420,440,460,475]:
        p=lum[y-300]
        # left edge: first x (from 480) where lum crosses 0.5*(bg+white)
        def cr(x0,x1,step):
            prev=None
            for x in range(x0,x1,step):
                v=p[x-400]
                if prev is not None and (prev-125)*(v-125)<=0: return x-step+step*(125-prev)/(v-prev)
                prev=v
            return np.nan
        xl=cr(480,560,1); xr=cr(700,620,-1)
        print('  y %d  left %.2f right %.2f  width %.2f'%(y,xl,xr,xr-xl))
