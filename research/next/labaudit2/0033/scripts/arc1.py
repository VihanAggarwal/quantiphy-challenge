# t = 0.5 s (capture 12.5): arc-1 free fall. Image parabola on the 25 fps clock, range from three routes,
# label-style forward differences c12->c13 and c13->c14 (c12 is the dropped frame: click interpolated).
import numpy as np, sys, json
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit2/0033/scripts')
from geo import *
for R in ['x','s']:
    Cp=json.load(open(BASE+'capsule_%s.json'%R)) if R=='x' else None
    T=load_track(R)
    ks=[8,9,10,11,12,13]  # c8-c14 (the hand still touches the ball before c8)
    c=np.array([cap(k) for k in ks],float)
    u=np.array([Cp[str(k)]['mid'][0] if Cp else T[k]['cx'] for k in ks]); v=np.array([Cp[str(k)]['mid'][1] if Cp else T[k]['cy'] for k in ks])
    pu=np.polyfit(c,u,1); pv=np.polyfit(c,v,2)
    res=v-np.polyval(pv,c)
    a=2*pv[0]; apex=-pv[1]/(2*pv[0])
    print(R,'v-parabola a=%.2f px/fr^2 apex c%.2f rms %.2f; u slope %.2f px/fr'%(a,apex,np.sqrt(np.mean(res**2)),pu[0]))
    for f in [711,740]:
        Zg=f*980/625/a
        # sizes (capsule diameters, x render) over c8-c14
        if Cp: dsz=np.mean([2*Cp[str(k)]['r'] for k in [8,9,10,11,12,13]]); d35=2*Cp['34']['r']
        else: dsz=24.2; d35=33.7
        Zs_raw=f*4/dsz; Zs_cal=Zs_raw*(75.8/(f*4/d35))
        routes={'gravity':Zg,'size(raw)':Zs_raw,'size(cal. to ToF c35)':Zs_cal,'ToF-like 1.457':145.7}
        line=[]
        for name,Z in routes.items():
            vals=[]
            for (c0,c1) in [(12,13),(13,14)]:
                P0=Z*ray(np.polyval(pu,c0),np.polyval(pv,c0),f); P1=Z*ray(np.polyval(pu,c1),np.polyval(pv,c1),f)
                vals.append(np.linalg.norm(P1-P0)*25)
            line.append('%s Z=%.0f: %.0f / %.0f'%(name,Z,vals[0],vals[1]))
        print('  f%d'%f,' | '.join(line))
    print('  physical (g only): c12->13 %.0f, c13->14 %.0f, inst c12.5 %.0f'%(980*(12.5-apex)/25,980*(13.5-apex)/25,980*(12.5-apex)/25))
