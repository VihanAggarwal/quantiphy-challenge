import cv2, numpy as np
for v in ['0006','0007']:
    bg=cv2.imread(f'/home/user/quantiphy-challenge/research/next/audit3/internet_01/b{v}_bg.png')  # corridor x 480-640
    hsv=cv2.cvtColor(bg,cv2.COLOR_BGR2HSV).astype(float)
    g=cv2.cvtColor(bg,cv2.COLOR_BGR2GRAY).astype(float)
    out=[]
    for y0 in range(100,1900,200):
        s=hsv[y0:y0+100,:,1].mean(axis=0)  # saturation profile across x
        gg=g[y0:y0+100].mean(axis=0)
        # centre line: brightest column near 555-565 (use max of 95th pct)
        p95=np.percentile(g[y0:y0+100],95,axis=0)
        cl=480+40+np.argmax(p95[40:110])
        # asphalt: low saturation; find edges where s crosses midway between asphalt and verge levels
        sa=np.median(s[50:110]); 
        left=s[:60]; right=s[110:]
        sv_l=np.median(s[5:25]); sv_r=np.median(s[135:155])
        thrl=(sa+sv_l)/2; thrr=(sa+sv_r)/2
        # scan outward from centre
        xl=None
        for x in range(cl-480,0,-1):
            if s[x]>thrl: xl=x+0.5; break
        xr=None
        for x in range(cl-480,len(s)):
            if s[x]>thrr: xr=x-0.5; break
        out.append((y0,cl,xl+480 if xl else None,xr+480 if xr else None))
    for o in out: print(v,o, 'Lw', round(o[1]-o[2],1) if o[2] else None,'Rw', round(o[3]-o[1],1) if o[3] else None, 'road',round(o[3]-o[2],1) if o[2] and o[3] else None)
